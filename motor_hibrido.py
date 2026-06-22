import pandas as pd
import numpy as np
import os
from scipy.stats import poisson
from sklearn.ensemble import RandomForestClassifier
import fusion_sensores as fs

print("Inicializando Motor Predictivo Híbrido con Sistema ELO + Poisson...")

# 1. Cargar Datos (Ahora leemos directamente el historial inteligente)
df_combinado = pd.read_csv('historial_con_elo.csv')

# --- TRADUCTOR DE NACIONES BLINDADO ---
mapeo_naciones = {
    'Cape Verde': 'Cabo Verde', 'Cape Verde Islands': 'Cabo Verde',
    'United States': 'USA', 'Korea Republic': 'South Korea',
    'Korea DPR': 'North Korea', "Côte d'Ivoire": 'Ivory Coast',
    'Czech Republic': 'Czechia', 'Turkey': 'Türkiye',
    'IR Iran': 'Iran', 'Republic of Ireland': 'Ireland',
    'Bosnia-Herzegovina': 'Bosnia and Herzegovina'
}

# Seguimos leyendo tu archivo manual SOLO para saber qué equipos proteger en el filtro blindado
equipos_manuales = []
if os.path.exists('partidos_manuales.csv') and os.path.getsize('partidos_manuales.csv') > 10:
    df_manual = pd.read_csv('partidos_manuales.csv')
    df_manual['local'] = df_manual['local'].astype(str).str.strip().replace(mapeo_naciones)
    df_manual['visita'] = df_manual['visita'].astype(str).str.strip().replace(mapeo_naciones)
    equipos_manuales = pd.concat([df_manual['local'], df_manual['visita']]).unique()

# Seguimos leyendo tu archivo manual SOLO para saber qué equipos proteger en el filtro blindado
equipos_manuales = []
if os.path.exists('partidos_manuales.csv') and os.path.getsize('partidos_manuales.csv') > 10:
    df_manual = pd.read_csv('partidos_manuales.csv')
    equipos_manuales = pd.concat([df_manual['local'], df_manual['visita']]).unique()

## 2. CAPA BASE (POISSON)
df_local = df_combinado[['local', 'goles_local', 'goles_visita']].rename(columns={'local': 'equipo', 'goles_local': 'GF', 'goles_visita': 'GC'})
df_visita = df_combinado[['visita', 'goles_visita', 'goles_local']].rename(columns={'visita': 'equipo', 'goles_visita': 'GF', 'goles_local': 'GC'})
df_equipos = pd.concat([df_local, df_visita])

estadisticas = df_equipos.groupby('equipo').agg(partidos=('equipo', 'count'), GF=('GF', 'sum'), GC=('GC', 'sum')).reset_index()

# Filtro blindado: Mantiene al equipo si tiene >= 1 partido o si tú lo anotaste a mano [cite: 3]
estadisticas = estadisticas[(estadisticas['partidos'] >= 1) | (estadisticas['equipo'].isin(equipos_manuales))]

promedio_global = estadisticas['GF'].sum() / (estadisticas['partidos'].sum())
estadisticas['FA'] = (estadisticas['GF'] / estadisticas['partidos']) / promedio_global
estadisticas['FD'] = (estadisticas['GC'] / estadisticas['partidos']) / promedio_global

dict_fa = estadisticas.set_index('equipo')['FA'].to_dict()
dict_fd = estadisticas.set_index('equipo')['FD'].to_dict()

# 3. CAPA DE SENSORES (MICRO-VARIABLES)
equipos_unicos = pd.concat([df_combinado['local'], df_combinado['visita']]).unique()
dict_plantilla_atq, dict_plantilla_def = {}, {}

for equipo in equipos_unicos:
    atq, df_def = fs.calcular_metricas_plantilla('rendimiento_jugadores.csv', equipo)
    dict_plantilla_atq[equipo] = atq
    dict_plantilla_def[equipo] = df_def

df_combinado['Plantilla_Atq_Local'] = df_combinado['local'].map(dict_plantilla_atq)
df_combinado['Plantilla_Def_Local'] = df_combinado['local'].map(dict_plantilla_def)
df_combinado['Plantilla_Atq_Visita'] = df_combinado['visita'].map(dict_plantilla_atq)
df_combinado['Plantilla_Def_Visita'] = df_combinado['visita'].map(dict_plantilla_def)

df_combinado['FA_local'] = df_combinado['local'].map(dict_fa)
df_combinado['FD_local'] = df_combinado['local'].map(dict_fd)
df_combinado['FA_visita'] = df_combinado['visita'].map(dict_fa)
df_combinado['FD_visita'] = df_combinado['visita'].map(dict_fd)

df_ml = df_combinado.dropna().copy()
df_ml['diferencia_FA'] = df_ml['FA_local'] - df_ml['FA_visita']
df_ml['diferencia_FD'] = df_ml['FD_local'] - df_ml['FD_visita']
df_ml['dif_Plantilla_Atq'] = df_ml['Plantilla_Atq_Local'] - df_ml['Plantilla_Atq_Visita']
df_ml['dif_Plantilla_Def'] = df_ml['Plantilla_Def_Local'] - df_ml['Plantilla_Def_Visita']

def determinar_resultado(fila):
    if fila['goles_local'] > fila['goles_visita']: return 2
    elif fila['goles_local'] == fila['goles_visita']: return 1
    return 0
df_ml['resultado_real'] = df_ml.apply(determinar_resultado, axis=1)

# === PONDERACIÓN DE MUESTRAS ===
def calcular_peso_importancia(fila):
    nivel = fila.get('importancia', 1)
    
    if nivel == 2:
        return 3.0  # ¡NIVEL MUNDIAL! Pesa el triple en la red neuronal
    elif nivel == 1:
        return 1.0  # Torneos Oficiales y Eliminatorias (Peso normal)
    else:
        return 0.2  # Amistosos (Peso casi nulo para que no ensucien la estadística)

df_ml['peso_entrenamiento'] = df_ml.apply(calcular_peso_importancia, axis=1)

# === INYECCIÓN ELO: Ahora la red neuronal también aprende del puntaje Elo ===
X = df_ml[['FA_local', 'FD_local', 'FA_visita', 'FD_visita', 'diferencia_FA', 'diferencia_FD', 'dif_Plantilla_Atq', 'dif_Plantilla_Def', 'elo_local', 'elo_visita']]
Y = df_ml['resultado_real']

# Entrenamos pasando el vector de pesos creado
modelo_rf = RandomForestClassifier(n_estimators=150, max_depth=5, random_state=42)
modelo_rf.fit(X, Y, sample_weight=df_ml['peso_entrenamiento'])
print("¡Red Neuronal entrenada con priorización mundialista y ponderación de fuerza ELO!\n")

# ================================================================
# LA FUSIÓN DEFINITIVA: POISSON (PRESENTE) + ML ELO (PASADO)
# ================================================================

def calcular_probabilidades_poisson(xg_local, xg_visita, max_goles=10):
    """Convierte los Goles Esperados en Porcentajes exactos de victoria"""
    p_local, p_empate, p_visita = 0.0, 0.0, 0.0
    
    for gl in range(max_goles):
        for gv in range(max_goles):
            prob = poisson.pmf(gl, xg_local) * poisson.pmf(gv, xg_visita)
            if gl > gv:
                p_local += prob
            elif gl < gv:
                p_visita += prob
            else:
                p_empate += prob
                
    # Retornamos en el mismo orden que el ML: [Visita(0), Empate(1), Local(2)]
    return p_visita, p_empate, p_local


def predecir_partido(equipo_A, equipo_B):
    if equipo_A not in dict_fa or equipo_B not in dict_fa:
        return None, None, [0.33, 0.33, 0.34]

    fa_a, fd_a = dict_fa[equipo_A], dict_fd[equipo_A]
    fa_b, fd_b = dict_fa[equipo_B], dict_fd[equipo_B]
    atq_a, def_a = dict_plantilla_atq.get(equipo_A, 50.0), dict_plantilla_def.get(equipo_A, 50.0)
    atq_b, def_b = dict_plantilla_atq.get(equipo_B, 50.0), dict_plantilla_def.get(equipo_B, 50.0)

    # 1. CÁLCULO DEL PRESENTE (xG y Probabilidades de Poisson)
    xg_a = fa_a * fd_b * promedio_global
    xg_b = fa_b * fd_a * promedio_global
    poisson_v, poisson_e, poisson_l = calcular_probabilidades_poisson(xg_a, xg_b)

    # 2. CARGA DE ELO EN VIVO
    try:
        df_elo_vivo = pd.read_csv('ranking_elo_vivo.csv').set_index('equipo')
        elo_l = df_elo_vivo.loc[equipo_A, 'elo_actual'] if equipo_A in df_elo_vivo.index else 1100.0
        elo_v = df_elo_vivo.loc[equipo_B, 'elo_actual'] if equipo_B in df_elo_vivo.index else 1100.0
    except FileNotFoundError:
        elo_l, elo_v = 1100.0, 1100.0

    # 3. CÁLCULO DEL PASADO (Probabilidades de la Red Neuronal)
    vector = pd.DataFrame([{
        'FA_local': fa_a, 'FD_local': fd_a, 'FA_visita': fa_b, 'FD_visita': fd_b,
        'diferencia_FA': fa_a - fa_b, 'diferencia_FD': fd_a - fd_b,
        'dif_Plantilla_Atq': atq_a - atq_b, 'dif_Plantilla_Def': def_a - def_b,
        'elo_local': elo_l, 'elo_visita': elo_v
    }])
    probs_ml = modelo_rf.predict_proba(vector)[0]
    
    ml_v = probs_ml[0]
    ml_e = probs_ml[1]
    ml_l = probs_ml[2]

    # 4. LA VOTACIÓN SUAVE (BLENDING)
    # 60% peso a la forma actual de los jugadores, 40% a la historia del equipo
    PESO_PRESENTE = 0.60
    PESO_HISTORIA = 0.40
    
    prob_final_v = (poisson_v * PESO_PRESENTE) + (ml_v * PESO_HISTORIA)
    prob_final_e = (poisson_e * PESO_PRESENTE) + (ml_e * PESO_HISTORIA)
    prob_final_l = (poisson_l * PESO_PRESENTE) + (ml_l * PESO_HISTORIA)
    
    probs_hibridas = [prob_final_v, prob_final_e, prob_final_l]

    return xg_a, xg_b, probs_hibridas
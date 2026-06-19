import pandas as pd
import numpy as np
import os
from scipy.stats import poisson
from sklearn.ensemble import RandomForestClassifier
import fusion_sensores as fs

print("Inicializando Motor Predictivo Híbrido con Ponderación de Importancia...")

# 1. Cargar Datos
df_api = pd.read_csv('historial_selecciones_combinado.csv')
if os.path.exists('partidos_manuales.csv') and os.path.getsize('partidos_manuales.csv') > 10:
    df_manual = pd.read_csv('partidos_manuales.csv')
    df_combinado = pd.concat([df_api, df_manual], ignore_index=True)
else:
    df_combinado = df_api

## 2. CAPA BASE (POISSON)
df_local = df_combinado[['local', 'goles_local', 'goles_visita']].rename(columns={'local': 'equipo', 'goles_local': 'GF', 'goles_visita': 'GC'})
df_visita = df_combinado[['visita', 'goles_visita', 'goles_local']].rename(columns={'visita': 'equipo', 'goles_visita': 'GF', 'goles_local': 'GC'})
df_equipos = pd.concat([df_local, df_visita])

estadisticas = df_equipos.groupby('equipo').agg(partidos=('equipo', 'count'), GF=('GF', 'sum'), GC=('GC', 'sum')).reset_index()

# --- INICIO DE LA CORRECCIÓN PARA FORZAR INCLUSIÓN ---
equipos_manuales = []
if 'df_manual' in globals():
    equipos_manuales = pd.concat([df_manual['local'], df_manual['visita']]).unique()

# Filtro blindado: Mantiene al equipo si tiene >= 1 partido en la historia O si tú lo anotaste a mano
estadisticas = estadisticas[(estadisticas['partidos'] >= 1) | (estadisticas['equipo'].isin(equipos_manuales))]
# --- FIN DE LA CORRECCIÓN ---

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

# ---> ¡AGREGA ESTAS 4 LÍNEAS AQUÍ! <---
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

# === IMPLEMENTACIÓN DE TU SUGERENCIA: PONDERACIÓN DE MUESTRAS ===
def calcular_peso_importancia(fila):
    # Si el partido pertenece al Mundial (ID 1) o es del año actual (lista manual)
    if str(fila['torneo_id']) == '1' or int(fila['temporada']) == 2026:
        return 3.0  # Triple de prioridad
    return 1.0  # Prioridad normal

df_ml['peso_entrenamiento'] = df_ml.apply(calcular_peso_importancia, axis=1)
# ================================================================

X = df_ml[['FA_local', 'FD_local', 'FA_visita', 'FD_visita', 'diferencia_FA', 'diferencia_FD', 'dif_Plantilla_Atq', 'dif_Plantilla_Def']]
Y = df_ml['resultado_real']

# Entrenamos pasando el vector de pesos creado
modelo_rf = RandomForestClassifier(n_estimators=150, max_depth=5, random_state=42)
modelo_rf.fit(X, Y, sample_weight=df_ml['peso_entrenamiento']) # <-- Aquí el modelo prioriza tus variables
print("¡Red Neuronal entrenada con priorización mundialista y de formulario manual!\n")

def predecir_partido(equipo_A, equipo_B):
    if equipo_A not in dict_fa or equipo_B not in dict_fa:
        return None, None, [0.33, 0.33, 0.34]

    fa_a, fd_a = dict_fa[equipo_A], dict_fd[equipo_A]
    fa_b, fd_b = dict_fa[equipo_B], dict_fd[equipo_B]
    atq_a, def_a = dict_plantilla_atq.get(equipo_A, 50.0), dict_plantilla_def.get(equipo_A, 50.0)
    atq_b, def_b = dict_plantilla_atq.get(equipo_B, 50.0), dict_plantilla_def.get(equipo_B, 50.0)

    xg_a = fa_a * fd_b * promedio_global
    xg_b = fa_b * fd_a * promedio_global

    vector = pd.DataFrame([{
        'FA_local': fa_a, 'FD_local': fd_a, 'FA_visita': fa_b, 'FD_visita': fd_b,
        'diferencia_FA': fa_a - fa_b, 'diferencia_FD': fd_a - fd_b,
        'dif_Plantilla_Atq': atq_a - atq_b, 'dif_Plantilla_Def': def_a - def_b
    }])
    
    probs = modelo_rf.predict_proba(vector)[0]
    return xg_a, xg_b, probs
import pandas as pd
import os

print("Inicializando Motor Elo con Calibración Oficial FIFA (Mundial 2026)...")

# 1. Cargar el historial completo
df_api = pd.read_csv('historial_selecciones_combinado.csv')
# Etiquetamos el origen para darle distinto peso matemático
df_api['origen'] = 'historia' 

if os.path.exists('partidos_manuales.csv'):
    df_manual = pd.read_csv('partidos_manuales.csv')
    df_manual['origen'] = 'mundial_2026'
    df = pd.concat([df_api, df_manual], ignore_index=True)
else:
    df = df_api.copy()

# 2. DICCIONARIO SEMILLA (PUNTOS OFICIALES FIFA JUNIO 2026)
# Extraídos de tu PDF oficial. 
# Nombres estandarizados al inglés para coincidir con tu base de datos.
PUNTOS_FIFA = {
    'Argentina': 1889.0, 'France': 1887.0, 'Spain': 1856.0, 'England': 1847.0,
    'Brazil': 1772.0, 'Morocco': 1770.0, 'Netherlands': 1764.0, 'Portugal': 1755.0,
    'Germany': 1644.0, 'Belgium': 1700.0, 'Mexico': 1652.0, 'Colombia': 1669.0, 
    'USA': 1676.0, 'Croatia': 1728.0, 'Uruguay': 1713.0, 'Japan': 1628.0,
    'Senegal': 1623.0, 'Switzerland': 1616.0, 'Iran': 1611.0, 'Denmark': 1610.0,
    'Austria': 1560.0, 'South Korea': 1563.0, 'Australia': 1571.0, 'Ukraine': 1565.0,
    'Ecuador': 1517.0, 'Poland': 1541.0, 'Sweden': 1522.0, 'Wales': 1521.0, 
    'Hungary': 1519.0, 'Serbia': 1514.0, 'Peru': 1515.0, 'Chile': 1489.0, 
    'Ivory Coast': 1494.0, 'Türkiye': 1495.0, 'Paraguay': 1480.0, 'Nigeria': 1498.0, 
    'Tunisia': 1493.0, 'Panama': 1475.0, 'Canada': 1461.0, 'Algeria': 1484.0, 
    'Mali': 1473.0, 'Cameroon': 1458.0, 'Costa Rica': 1445.0, 'Czechia': 1487.0, 
    'Scotland': 1477.0, 'Saudi Arabia': 1430.0, 'Iraq': 1420.0, 'South Africa': 1410.0,
    'Cabo Verde': 1400.0, 'DR Congo': 1390.0, 'Uzbekistan': 1380.0, 'Ghana': 1370.0,
    'Haiti': 1250.0, 'Bosnia and Herzegovina': 1350.0, 'New Zealand': 1340.0,
    'Egypt': 1360.0, 'Norway': 1375.0, 'Jordan': 1355.0, 'Qatar': 1405.0
}

elo_dict = {}

def obtener_elo(equipo):
    # Si el equipo está en el top de la FIFA, usa su puntaje real del PDF.
    if equipo in PUNTOS_FIFA:
        return PUNTOS_FIFA[equipo]
    # Si es de los rankeados muy bajo (los otros ~140 equipos de los 211),
    # el sistema les asigna automáticamente este puntaje bajo.
    return 1100.0

elos_local = []
elos_visita = []

# 3. Viaje en el tiempo partido a partido
for index, row in df.iterrows():
    eq_l = row['local']
    eq_v = row['visita']
    gl = row['goles_local']
    gv = row['goles_visita']
    origen = row['origen']

    # Asignar el factor K (Importancia del partido)
    # Amistosos e historia valen poco (10). Los partidos EN VIVO del Mundial valen oro (40).
    K = 40 if origen == 'mundial_2026' else 10

    elo_l = obtener_elo(eq_l)
    elo_v = obtener_elo(eq_v)
    elos_local.append(elo_l)
    elos_visita.append(elo_v)

    exp_l = 1 / (1 + 10 ** ((elo_v - elo_l) / 400))
    exp_v = 1 / (1 + 10 ** ((elo_l - elo_v) / 400))

    if gl > gv:
        s_l, s_v = 1.0, 0.0
    elif gl < gv:
        s_l, s_v = 0.0, 1.0
    else:
        s_l, s_v = 0.5, 0.5

    elo_dict[eq_l] = elo_l + K * (s_l - exp_l)
    elo_dict[eq_v] = elo_v + K * (s_v - exp_v)

# 4. Inyectar y exportar
df['elo_local'] = elos_local
df['elo_visita'] = elos_visita

# Limpiamos la columna de origen antes de exportar
df.drop(columns=['origen'], inplace=True)
df.to_csv('historial_con_elo.csv', index=False)
print(f"✅ ¡Sistema Elo inyectado! {len(df)} partidos procesados.")

# 5. Guardar el Ranking Actualizado
df_ranking_elo = pd.DataFrame(list(elo_dict.items()), columns=['equipo', 'elo_actual'])
df_ranking_elo.sort_values(by='elo_actual', ascending=False, inplace=True)
df_ranking_elo.to_csv('ranking_elo_vivo.csv', index=False)
print("✅ Ranking calibrado guardado en 'ranking_elo_vivo.csv'")
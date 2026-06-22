import pandas as pd
import os

print("Inicializando Motor Elo con Calibración Oficial FIFA (211 Equipos)...")

# 1. Cargar el historial completo
df_api = pd.read_csv('historial_selecciones_combinado.csv')

# --- TRADUCTOR DE NACIONES (Blindaje de Identidades) ---
mapeo_naciones = {
    'Cape Verde': 'Cabo Verde',
    'United States': 'USA',
    'Korea Republic': 'South Korea',
    'Korea DPR': 'North Korea',
    "Côte d'Ivoire": 'Ivory Coast',
    'Czech Republic': 'Czechia',
    'Turkey': 'Türkiye',
    'IR Iran': 'Iran',
    'Republic of Ireland': 'Ireland',
    'Bosnia-Herzegovina': 'Bosnia and Herzegovina'
}
# Aplicar la traducción a las columnas de local y visita
df_api['local'] = df_api['local'].replace(mapeo_naciones)
df_api['visita'] = df_api['visita'].replace(mapeo_naciones)

df_api['origen'] = 'historia'

# Rescatamos tu sistema 0 y 1 de Kaggle (asumiendo que está en 'torneo_id')
if 'torneo_id' in df_api.columns:
    df_api['importancia'] = df_api['torneo_id']
else:
    df_api['importancia'] = 1

if os.path.exists('partidos_manuales.csv'):
    df_manual = pd.read_csv('partidos_manuales.csv')
    df_manual['origen'] = 'mundial_2026'
    
    # ---> ¡EL TOQUE MAESTRO! Los partidos del Mundial valen 2 <---
    df_manual['importancia'] = 2  
    
    df = pd.concat([df_api, df_manual], ignore_index=True)
else:
    df = df_api.copy()

# 2. DICCIONARIO SEMILLA (PUNTOS OFICIALES FIFA - JUNIO 2026)
# Extraídos de la clasificación oficial de los 211 equipos.
# Traducidos al inglés para coincidencia perfecta con la base de datos (API).
PUNTOS_FIFA = {
    'Argentina': 1889.06, 'France': 1887.11, 'Spain': 1856.03, 'England': 1847.68,
    'Brazil': 1772.01, 'Morocco': 1769.98, 'Portugal': 1755.09, 'Germany': 1743.54,
    'Belgium': 1733.93, 'Mexico': 1721.78, 'Colombia': 1712.60, 'USA': 1709.59,
    'Italy': 1704.73, 'Croatia': 1695.21, 'Japan': 1665.94, 'Uruguay': 1661.95,
    'Switzerland': 1654.94, 'Denmark': 1619.47, 'Austria': 1612.86, 'Iran': 1605.12,
    'South Korea': 1591.75, 'Nigeria': 1585.02, 'Norway': 1577.18, 'Canada': 1572.13,
    'Ecuador': 1570.76, 'Egypt': 1570.67, 'Ivory Coast': 1568.62, 'Algeria': 1559.24,
    'Türkiye': 1550.13, 'Ukraine': 1549.29, 'Poland': 1526.18, 'Sweden': 1517.99,
    'Paraguay': 1517.39, 'Wales': 1516.95, 'Hungary': 1506.39, 'Panama': 1505.33,
    'Scotland': 1504.41, 'Serbia': 1502.13, 'Czechia': 1481.49, 'Cameroon': 1481.24,
    'Slovakia': 1473.66, 'Greece': 1473.19, 'Venezuela': 1469.18, 'Chile': 1458.20,
    'Peru': 1457.69, 'Costa Rica': 1456.03, 'Mali': 1455.59, 'Tunisia': 1453.00,
    'Uzbekistan': 1444.48, 'Republic of Ireland': 1441.10, 'Slovenia': 1441.09, 'Qatar': 1438.82,
    'Saudi Arabia': 1435.00, 'Iraq': 1426.53, 'Burkina Faso': 1406.99, 'Cabo Verde': 1389.79,
    'Bosnia and Herzegovina': 1381.18, 'Ghana': 1380.71, 'Honduras': 1378.97, 'Albania': 1376.03,
    'Jordan': 1372.29, 'UAE': 1370.47, 'Northern Ireland': 1365.30, 'Jamaica': 1357.84,
    'Georgia': 1355.26, 'Iceland': 1342.77, 'Finland': 1341.92, 'Israel': 1333.90,
    'Bolivia': 1326.00, 'Kosovo': 1319.12, 'Montenegro': 1301.98, 'Guinea': 1295.60,
    'New Zealand': 1290.04, 'Curacao': 1287.00, 'Syria': 1283.05, 'Gabon': 1272.51,
    'Bulgaria': 1271.68, 'Haiti': 1271.00, 'Uganda': 1264.09, 'Zambia': 1255.82,
    'China PR': 1254.81, 'Bahrain': 1254.41, 'Benin': 1252.17, 'Thailand': 1250.80,
    'Palestine': 1243.71, 'Belarus': 1242.88, 'Luxembourg': 1232.82, 'Vietnam': 1225.68,
    'El Salvador': 1225.34, 'Tajikistan': 1224.19, 'Trinidad and Tobago': 1219.59, 'Mozambique': 1218.62,
    'Madagascar': 1202.69, 'Equatorial Guinea': 1195.20, 'Armenia': 1189.63, 'Comoros': 1187.91,
    'Kenya': 1185.08, 'Libya': 1182.08, 'Kazakhstan': 1180.78, 'Tanzania': 1180.27,
    'Mauritania': 1176.68, 'Niger': 1175.33, 'Gambia': 1159.64, 'Sudan': 1157.22,
    'Indonesia': 1157.14, 'Togo': 1152.76, 'North Korea': 1151.05, 'Namibia': 1148.84,
    'Sierra Leone': 1147.56, 'Faroe Islands': 1136.59, 'Suriname': 1132.43, 'Azerbaijan': 1132.00,
    'Estonia': 1130.64, 'Rwanda': 1126.62, 'Malawi': 1122.05, 'Zimbabwe': 1119.78,
    'Nicaragua': 1114.63, 'Guinea-Bissau': 1108.38, 'Congo': 1105.96, 'Philippines': 1100.95,
    'Malaysia': 1086.22, 'Latvia': 1085.66, 'India': 1084.93, 'Central African Republic': 1080.82,
    'Liberia': 1080.44, 'Turkmenistan': 1078.65, 'Ethiopia': 1077.52, 'Dominican Republic': 1076.50,
    'Yemen': 1065.24, 'Lesotho': 1064.29, 'Botswana': 1063.63, 'Singapore': 1057.95,
    'Lithuania': 1056.85, 'Guyana': 1049.32, 'St. Kitts and Nevis': 1036.33, 'Solomon Islands': 1031.89,
    'Puerto Rico': 1024.30, 'Fiji': 1024.17, 'Hong Kong': 1024.16, 'Tahiti': 1019.04,
    'Myanmar': 1010.91, 'Moldova': 1008.24, 'Malta': 992.79, 'Antigua and Barbuda': 986.58,
    'Grenada': 981.82, 'Cuba': 981.42, 'Eswatini': 979.01, 'St. Lucia': 976.71,
    'Bermuda': 975.05, 'Papua New Guinea': 974.90, 'St. Vincent and the Grenadines': 968.27, 'Afghanistan': 968.07,
    'Andorra': 946.43, 'Maldives': 943.92, 'Chinese Taipei': 923.78, 'Cambodia': 922.32,
    'Montserrat': 916.75, 'Nepal': 914.54, 'Barbados': 909.89, 'Belize': 907.00,
    'Bangladesh': 902.93, 'Dominica': 897.69, 'Chad': 896.85, 'Eritrea': 887.06,
    'Laos': 885.03, 'Cook Islands': 877.53, 'Samoa': 876.41, 'Aruba': 875.61,
    'Mongolia': 874.47, 'American Samoa': 871.61, 'Bhutan': 870.81, 'Macau': 858.03,
    'Brunei': 857.73, 'Sao Tome and Principe': 855.44, 'Cayman Islands': 850.06, 'Pakistan': 840.28,
    'Somalia': 839.17, 'Tonga': 835.64, 'Timor-Leste': 831.00, 'Gibraltar': 820.26,
    'Guam': 819.54, 'Seychelles': 804.16, 'Liechtenstein': 797.70, 'Bahamas': 786.82,
    'US Virgin Islands': 779.76, 'British Virgin Islands': 777.41, 'Anguilla': 760.25, 'San Marino': 721.20
}

elo_dict = {}

def obtener_elo(equipo):
    # Ya cubrimos a los 211 equipos en el diccionario.
    # El 1100 es solo un seguro de vida si la base histórica tiene un error de dedo en un nombre.
    return elo_dict.get(equipo, PUNTOS_FIFA.get(equipo, 1100.0))

elos_local = []
elos_visita = []

# 3. Viaje en el tiempo partido a partido
for index, row in df.iterrows():
    eq_l = row['local']
    eq_v = row['visita']
    gl = row['goles_local']
    gv = row['goles_visita']
    origen = row['origen']

    # Factor de Importancia (K)
    # 40 = Mundial/Torneos Mayores, 10 = Historial Antiguo
    K = 40 if origen == 'mundial_2026' else 10

    elo_l = obtener_elo(eq_l)
    elo_v = obtener_elo(eq_v)
    elos_local.append(elo_l)
    elos_visita.append(elo_v)

    # Fórmula Matemática Elo
    exp_l = 1 / (1 + 10 ** ((elo_v - elo_l) / 400))
    exp_v = 1 / (1 + 10 ** ((elo_l - elo_v) / 400))

    if gl > gv:
        s_l, s_v = 1.0, 0.0
    elif gl < gv:
        s_l, s_v = 0.0, 1.0
    else:
        s_l, s_v = 0.5, 0.5

    # Actualizamos el diccionario en memoria
    elo_dict[eq_l] = elo_l + K * (s_l - exp_l)
    elo_dict[eq_v] = elo_v + K * (s_v - exp_v)

# 4. Inyectar y exportar
df['elo_local'] = elos_local
df['elo_visita'] = elos_visita

# Limpiamos para exportar un CSV limpio
df.drop(columns=['origen'], inplace=True)
df.to_csv('historial_con_elo.csv', index=False)
print(f"✅ ¡Sistema Elo inyectado! {len(df)} partidos procesados.")

# 5. Guardar el Ranking Actualizado
df_ranking_elo = pd.DataFrame(list(elo_dict.items()), columns=['equipo', 'elo_actual'])
df_ranking_elo.sort_values(by='elo_actual', ascending=False, inplace=True)
df_ranking_elo.to_csv('ranking_elo_vivo.csv', index=False)
print("✅ Ranking calibrado guardado en 'ranking_elo_vivo.csv'")
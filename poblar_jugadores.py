import pandas as pd
import os

print("Iniciando motor de Data Engineering (Cruce de Bases de Datos)...")

# 1. Verificar el archivo gigante
if not os.path.exists('fifa_players.csv'):
    print("Error: No se encontró 'fifa_players.csv'.")
    exit()

# 2. Cargar bases de datos (low_memory=False porque FIFA tiene +18,000 filas y 100+ columnas)
df_nuestro = pd.read_csv('historial_selecciones_combinado.csv')
df_fifa = pd.read_csv('fifa_players.csv', low_memory=False)

equipos_necesarios = pd.concat([df_nuestro['local'], df_nuestro['visita']]).dropna().unique()

# 3. Diccionario de traducción para limpiar datos inconsistentes
traduccion_paises = {
    'South Korea': 'Korea Republic',
    'USA': 'United States',
    'Türkiye': 'Turkey',
    'Czechia': 'Czech Republic',
    'Ivory Coast': "Côte d'Ivoire",
    'DR Congo': 'Congo DR',
    'Bosnia and Herzegovina': 'Bosnia and Herzegovina',
    'Republic of Ireland': 'Republic of Ireland'
}

lista_final = []

def mapear_posicion(pos_fifa):
    pos = str(pos_fifa).split(',')[0].upper() 
    if pos in ['GK']: return 'POR'
    if pos in ['CB', 'RB', 'LB', 'RWB', 'LWB']: return 'DEF'
    if pos in ['CM', 'CDM', 'CAM', 'RM', 'LM']: return 'MED'
    if pos in ['ST', 'CF', 'RW', 'LW']: return 'DEL'
    return 'MED'

print(f"Filtrando métricas para {len(equipos_necesarios)} selecciones nacionales...")

# 4. El motor de búsqueda
for equipo in sorted(equipos_necesarios):
    pais_fifa = traduccion_paises.get(equipo, equipo)
    jugadores_pais = df_fifa[df_fifa['nationality_name'] == pais_fifa].copy()
    
    # Si es una isla/país muy pequeño que no sale en el juego, le damos stats genéricas
    if jugadores_pais.empty:
        lista_final.append({'equipo': equipo, 'jugador': f'Portero {equipo}', 'posicion': 'POR', 'rating_ataque': 10, 'rating_defensa': 70, 'fisco': 70})
        lista_final.append({'equipo': equipo, 'jugador': f'Defensa {equipo}', 'posicion': 'DEF', 'rating_ataque': 30, 'rating_defensa': 70, 'fisco': 70})
        lista_final.append({'equipo': equipo, 'jugador': f'Medio {equipo}', 'posicion': 'MED', 'rating_ataque': 70, 'rating_defensa': 70, 'fisco': 70})
        lista_final.append({'equipo': equipo, 'jugador': f'Delantero {equipo}', 'posicion': 'DEL', 'rating_ataque': 70, 'rating_defensa': 30, 'fisco': 70})
        continue

    jugadores_pais['pos_nuestra'] = jugadores_pais['player_positions'].apply(mapear_posicion)
    
    # Encontramos al #1 de cada posición para ese país
    for pos in ['POR', 'DEF', 'MED', 'DEL']:
        candidatos = jugadores_pais[jugadores_pais['pos_nuestra'] == pos]
        if not candidatos.empty:
            mejor = candidatos.sort_values(by='overall', ascending=False).iloc[0]
            
            # Limpiamos valores nulos (los porteros no suelen tener stat de tiro en el CSV)
            atq = mejor.get('shooting', 15) if pd.notna(mejor.get('shooting')) else 15
            dfns = mejor.get('defending', mejor['overall']) if pd.notna(mejor.get('defending')) else mejor['overall']
            fis = mejor.get('physic', mejor['overall']) if pd.notna(mejor.get('physic')) else mejor['overall']
            
            lista_final.append({
                'equipo': equipo,
                'jugador': str(mejor['short_name']),
                'posicion': pos,
                'rating_ataque': int(atq),
                'rating_defensa': int(dfns),
                'fisco': int(fis)
            })
        else:
            lista_final.append({'equipo': equipo, 'jugador': f'Reserva {pos}', 'posicion': pos, 'rating_ataque': 60, 'rating_defensa': 60, 'fisco': 60})

# 5. Exportar el cerebro táctico
df_resultado = pd.DataFrame(lista_final)
df_resultado.to_csv('rendimiento_jugadores.csv', index=False, encoding='utf-8')
print("¡Data Blending Exitoso! Tu archivo 'rendimiento_jugadores.csv' tiene ahora a los verdaderos cracks del fútbol.")
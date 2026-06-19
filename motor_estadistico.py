import pandas as pd
import numpy as np
from scipy.stats import poisson

# 1. Cargar la matriz de datos crudos
df = pd.read_csv('historial_selecciones_combinado.csv')

# 2. Reestructurar los datos: Separar el rendimiento como Local y Visita
# Necesitamos consolidar los goles de cada equipo sin importar dónde jugó
df_local = df[['local', 'goles_local', 'goles_visita']].rename(
    columns={'local': 'equipo', 'goles_local': 'goles_favor', 'goles_visita': 'goles_contra'})

df_visita = df[['visita', 'goles_visita', 'goles_local']].rename(
    columns={'visita': 'equipo', 'goles_visita': 'goles_favor', 'goles_local': 'goles_contra'})

# Unimos ambas tablas en una sola matriz de rendimiento general
df_equipos = pd.concat([df_local, df_visita])

# 3. Agrupar la estadística por equipo
estadisticas = df_equipos.groupby('equipo').agg(
    partidos=('equipo', 'count'),
    goles_favor=('goles_favor', 'sum'),
    goles_contra=('goles_contra', 'sum')
).reset_index()

# 4. Cálculo de Coeficientes del Sistema (FA y FD)
total_goles = estadisticas['goles_favor'].sum()
total_partidos = estadisticas['partidos'].sum() / 2  # Cada partido tiene 2 equipos
promedio_global = total_goles / (total_partidos * 2)

estadisticas['goles_favor_promedio'] = estadisticas['goles_favor'] / estadisticas['partidos']
estadisticas['goles_contra_promedio'] = estadisticas['goles_contra'] / estadisticas['partidos']

estadisticas['FA'] = estadisticas['goles_favor_promedio'] / promedio_global
estadisticas['FD'] = estadisticas['goles_contra_promedio'] / promedio_global

print("--- COEFICIENTES DE LOS EQUIPOS (Muestra) ---")
print(estadisticas[['equipo', 'FA', 'FD']].head(10).to_string(index=False))
print("\n")

# 5. Función de Predicción usando la Distribución de Poisson
def simular_partido(equipo_A, equipo_B):
    try:
        # Extraer parámetros de los equipos
        fa_A = estadisticas.loc[estadisticas['equipo'] == equipo_A, 'FA'].values[0]
        fd_A = estadisticas.loc[estadisticas['equipo'] == equipo_A, 'FD'].values[0]
        
        fa_B = estadisticas.loc[estadisticas['equipo'] == equipo_B, 'FA'].values[0]
        fd_B = estadisticas.loc[estadisticas['equipo'] == equipo_B, 'FD'].values[0]
    except IndexError:
        return "Error: Uno de los equipos no está en la base de datos."

    # Calcular Lambdas (Goles Esperados)
    lambda_A = fa_A * fd_B * promedio_global
    lambda_B = fa_B * fd_A * promedio_global

    # Generar matriz de probabilidades de marcadores exactos (hasta 5 goles)
    prob_A = [poisson.pmf(i, lambda_A) for i in range(6)]
    prob_B = [poisson.pmf(i, lambda_B) for i in range(6)]
    
    # Calcular probabilidades cruzadas (Victoria, Empate, Derrota)
    prob_victoria_A = 0
    prob_empate = 0
    prob_victoria_B = 0
    
    for goles_A in range(6):
        for goles_B in range(6):
            prob_marcador = prob_A[goles_A] * prob_B[goles_B]
            if goles_A > goles_B:
                prob_victoria_A += prob_marcador
            elif goles_A == goles_B:
                prob_empate += prob_marcador
            else:
                prob_victoria_B += prob_marcador

    print(f"--- PREDICCIÓN: {equipo_A} vs {equipo_B} ---")
    print(f"Goles Esperados (xG) {equipo_A}: {lambda_A:.2f}")
    print(f"Goles Esperados (xG) {equipo_B}: {lambda_B:.2f}")
    print("-" * 30)
    print(f"Prob. Victoria {equipo_A}: {prob_victoria_A * 100:.2f}%")
    print(f"Prob. Empate: {prob_empate * 100:.2f}%")
    print(f"Prob. Victoria {equipo_B}: {prob_victoria_B * 100:.2f}%")

# 6. Prueba del Motor (Asegúrate de escribir los nombres tal como aparecen en el CSV)
simular_partido('Mexico', 'Argentina')
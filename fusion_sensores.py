import pandas as pd
import numpy as np

def calcular_metricas_plantilla(archivo_jugadores, equipo_nombre):
    # 1. Cargar el catálogo local de jugadores
    try:
        df_jugadores = pd.read_csv(archivo_jugadores)
    except FileNotFoundError:
        # Valores por defecto si el archivo no existe aún
        return 50.0, 50.0

    # Filtramos la plantilla del equipo en cuestión
    plantilla = df_jugadores[df_jugadores['equipo'] == equipo_nombre]
    
    if plantilla.empty:
        return 50.0, 50.0 # Retorno neutral si no hay datos

    # 2. Definición de la Matriz de Pesos Ponderados (W) según la posición
    # Posiciones: DEL (Delantero), MED (Mediocampista), DEF (Defensa), POR (Portero)
    pesos_ataque = {'DEL': 1.0, 'MED': 0.6, 'DEF': 0.1, 'POR': 0.0}
    pesos_defensa = {'DEL': 0.1, 'MED': 0.5, 'DEF': 1.0, 'POR': 1.0}

    # 3. Aplicar la combinación lineal
    plantilla = plantilla.copy()
    plantilla['W_ataque'] = plantilla['posicion'].map(pesos_ataque)
    plantilla['W_defensa'] = plantilla['posicion'].map(pesos_defensa)

    # Cálculo del promedio ponderado para el sistema ofensivo y defensivo
    score_ataque = np.average(plantilla['rating_ataque'], weights=plantilla['W_ataque'])
    score_defensa = np.average(plantilla['rating_defensa'], weights=plantilla['W_defensa'])

    return round(score_ataque, 2), round(score_defensa, 2)

# Prueba rápida del algoritmo de fusión de sensores
if __name__ == "__main__":
    print("Calculando índices de calidad de plantilla...")
    
    # 1. Quitamos el '#' para que se ejecute la función
    calidad_atq, calidad_def = calcular_metricas_plantilla('rendimiento_jugadores.csv', 'Mexico')
    
    # 2. Imprimimos los resultados en la terminal
    print(f"Índice Ofensivo (Ataque): {calidad_atq}")
    print(f"Índice Defensivo (Defensa): {calidad_def}")
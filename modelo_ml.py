import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# 1. Cargar datos históricos
print("Cargando base de datos...")
df = pd.read_csv('historial_selecciones_combinado.csv')

# 2. Ingeniería de Características (Feature Engineering)
# Calculamos métricas históricas simples que el ML usará para aprender.
# (En un sistema final, estas vendrían del script de Poisson que hicimos antes)

# Simplificación para el entrenamiento: ¿Cuántos goles ha promediado cada equipo en el dataset?
promedios_goles = df.groupby('local')['goles_local'].mean().to_dict()
promedios_concedidos = df.groupby('local')['goles_visita'].mean().to_dict()

# Mapeamos esos valores a cada partido histórico
df['fuerza_ataque_local'] = df['local'].map(promedios_goles).fillna(1.0)
df['fuerza_defensa_local'] = df['local'].map(promedios_concedidos).fillna(1.0)
df['fuerza_ataque_visita'] = df['visita'].map(promedios_goles).fillna(1.0) # Usamos el mismo dict por simplicidad
df['fuerza_defensa_visita'] = df['visita'].map(promedios_concedidos).fillna(1.0)

# Simulamos una variable de contexto: "Diferencia de nivel"
df['diferencia_nivel'] = df['fuerza_ataque_local'] - df['fuerza_ataque_visita']

# 3. Definir la Variable Objetivo (Lo que queremos predecir)
# 2 = Gana Local, 1 = Empate, 0 = Gana Visita
def determinar_resultado(fila):
    if fila['goles_local'] > fila['goles_visita']:
        return 2
    elif fila['goles_local'] == fila['goles_visita']:
        return 1
    else:
        return 0

df['resultado_real'] = df.apply(determinar_resultado, axis=1)

# 4. Separar los datos en Entrenamiento (X) y Objetivo (Y)
# X son las variables que el algoritmo puede "ver" antes del partido
X = df[['fuerza_ataque_local', 'fuerza_defensa_local', 'fuerza_ataque_visita', 'fuerza_defensa_visita', 'diferencia_nivel']]
# Y es el resultado que debe adivinar
Y = df['resultado_real']

# Dividimos: 80% para entrenar, 20% para probar (backtesting)
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

# 5. Entrenar el Modelo (Random Forest)
print("Entrenando el modelo de Machine Learning...")
modelo_rf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
modelo_rf.fit(X_train, Y_train)

# 6. Evaluar la precisión (Backtesting)
predicciones = modelo_rf.predict(X_test)
precision = accuracy_score(Y_test, predicciones)

print("\n--- RESULTADOS DEL ENTRENAMIENTO ---")
print(f"Precisión del modelo en datos desconocidos: {precision * 100:.2f}%")

print("\n--- PREDICCIÓN EN VIVO (MÉXICO VS ARGENTINA) ---")
# Aquí ingresamos los parámetros del partido usando la lógica de nuestro código anterior
# Simulemos los datos para México (Local) vs Argentina (Visita)
datos_partido = pd.DataFrame([{
    'fuerza_ataque_local': 1.2,   # xG de México (ejemplo)
    'fuerza_defensa_local': 1.5,  # Goles que suele conceder
    'fuerza_ataque_visita': 2.5,  # xG de Argentina (ejemplo)
    'fuerza_defensa_visita': 0.8, # Goles que suele conceder
    'diferencia_nivel': 1.2 - 2.5 # Contexto matemático
}])

probabilidades = modelo_rf.predict_proba(datos_partido)[0]

print(f"Prob. Victoria Argentina (Visita): {probabilidades[0] * 100:.2f}%")
print(f"Prob. Empate: {probabilidades[1] * 100:.2f}%")
print(f"Prob. Victoria México (Local): {probabilidades[2] * 100:.2f}%")
import pandas as pd

print("⚽ Leyendo la mega base de datos de Kaggle...")

try:
    # 1. Cargar el dataset gigante
    df_kaggle = pd.read_csv('results.csv')
except FileNotFoundError:
    print("❌ Error: No se encontró el archivo 'results.csv'. Asegúrate de haberlo extraído en esta carpeta.")
    exit()

# Eliminar partidos del futuro donde los goles sean nulos (NA)
df_kaggle = df_kaggle.dropna(subset=['home_score', 'away_score'])

# Convertir la fecha al formato correcto
df_kaggle['date'] = pd.to_datetime(df_kaggle['date'])

# 2. Filtrar post-Mundial de Qatar (2023 en adelante)
df_reciente = df_kaggle[df_kaggle['date'] >= '2023-01-01'].copy()

# === EL NUEVO FIX: ELIMINAR EL MUNDIAL 2026 DE KAGGLE ===
# Identificamos los partidos del torneo "FIFA World Cup" del año 2026 en adelante
filtro_mundial_actual = (df_reciente['tournament'] == 'FIFA World Cup') & (df_reciente['date'].dt.year >= 2026)

# Usamos el símbolo ~ (NOT) para decirle que conserve TODO EXCEPTO esos partidos
df_reciente = df_reciente[~filtro_mundial_actual]

# 3. Mapear la importancia del torneo (Kaggle: Amistosos vs Oficiales)
def clasificar_torneo(nombre_torneo):
    if 'Friendly' in nombre_torneo:
        return 0  # Peso nulo/bajo
    else:
        return 1  # Eliminatorias, Nations League, Copa América, etc.

df_reciente['torneo_id'] = df_reciente['tournament'].apply(clasificar_torneo)
df_reciente['temporada'] = df_reciente['date'].dt.year

# 4. Renombrar columnas para nuestro motor híbrido
df_reciente.rename(columns={
    'home_team': 'local',
    'away_team': 'visita',
    'home_score': 'goles_local',
    'away_score': 'goles_visita'
}, inplace=True)

# Convertimos los goles a enteros para cálculos limpios
df_reciente['goles_local'] = df_reciente['goles_local'].astype(int)
df_reciente['goles_visita'] = df_reciente['goles_visita'].astype(int)

# 5. Seleccionar solo las columnas para Machine Learning
columnas_finales = ['local', 'visita', 'goles_local', 'goles_visita', 'torneo_id', 'temporada']
df_final = df_reciente[columnas_finales]

# 6. Sobrescribir nuestro historial combinado
df_final.to_csv('historial_selecciones_combinado.csv', index=False)

# Métricas de control
oficiales = len(df_final[df_final['torneo_id'] == 1])
amistosos = len(df_final[df_final['torneo_id'] == 0])

print(f"\n✅ ¡Filtro completado con éxito (Sin duplicados del Mundial actual)!")
print(f"📊 Se extrajeron {len(df_final)} partidos desde el 1 de enero de 2023.")
print(f"🏆 Partidos Oficiales (Clasificatorias/Copas/Nations League): {oficiales}")
print(f"🤝 Partidos Amistosos: {amistosos}")
print("\nEl archivo 'historial_selecciones_combinado.csv' ha sido actualizado y está listo para recibir el Sistema Elo.")
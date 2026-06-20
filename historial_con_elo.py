import pandas as pd
import os

print("Inicializando Motor Elo...")

# 1. Cargar el historial completo (API + Manuales)
df_api = pd.read_csv('historial_selecciones_combinado.csv')
if os.path.exists('partidos_manuales.csv'):
    df_manual = pd.read_csv('partidos_manuales.csv')
    df = pd.concat([df_api, df_manual], ignore_index=True)
else:
    df = df_api.copy()

# 2. Configuración del Sistema Elo
K = 30 # Factor de impacto (Un valor alto como 30 hace que las sorpresas pesen más)
elo_dict = {}

def obtener_elo(equipo):
    return elo_dict.get(equipo, 1500.0)

elos_local = []
elos_visita = []

# 3. Viaje en el tiempo: Calculando partido a partido
for index, row in df.iterrows():
    eq_l = row['local']
    eq_v = row['visita']
    gl = row['goles_local']
    gv = row['goles_visita']

    # Registrar el Elo exacto ANTES de que suene el silbato
    elo_l = obtener_elo(eq_l)
    elo_v = obtener_elo(eq_v)
    elos_local.append(elo_l)
    elos_visita.append(elo_v)

    # Fórmula Elo para calcular probabilidad esperada (E)
    exp_l = 1 / (1 + 10 ** ((elo_v - elo_l) / 400))
    exp_v = 1 / (1 + 10 ** ((elo_l - elo_v) / 400))

    # Determinar quién ganó realmente (S)
    if gl > gv:
        s_l, s_v = 1.0, 0.0 # Gana Local
    elif gl < gv:
        s_l, s_v = 0.0, 1.0 # Gana Visita
    else:
        s_l, s_v = 0.5, 0.5 # Empate

    # Actualizar la fuerza del equipo para el futuro
    elo_dict[eq_l] = elo_l + K * (s_l - exp_l)
    elo_dict[eq_v] = elo_v + K * (s_v - exp_v)

# 4. Inyectar las nuevas columnas al DataFrame
df['elo_local'] = elos_local
df['elo_visita'] = elos_visita

# 5. Exportar el nuevo cerebro histórico
df.to_csv('historial_con_elo.csv', index=False)
print(f"✅ ¡Sistema Elo inyectado! {len(df)} partidos procesados.")

# 6. Guardar el Ranking Actual (Para predecir los partidos de mañana)
df_ranking_elo = pd.DataFrame(list(elo_dict.items()), columns=['equipo', 'elo_actual'])
df_ranking_elo.sort_values(by='elo_actual', ascending=False, inplace=True)
df_ranking_elo.to_csv('ranking_elo_vivo.csv', index=False)
print("✅ Ranking actual guardado en 'ranking_elo_vivo.csv'")
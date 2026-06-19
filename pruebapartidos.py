import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd
import time

# 1. Crear una "Sesión Blindada" con tolerancia a fallos de red
session = requests.Session()
# Si falla, reintentará hasta 5 veces, esperando cada vez más tiempo (Backoff)
retries = Retry(total=5, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

url = "https://v3.football.api-sports.io/fixtures"
headers = {
    "x-apisports-key": "806a5e5aedb81f7f7e77e3033db6b721", # Pon tu clave
    "x-rapidapi-host": "v3.football.api-sports.io"
}

torneos_a_descargar = [
    ("1", "2022"),   # Mundial 2022
    ("1", "2026"),   # Mundial 2026
    ("4", "2024"),   # Eurocopa 2024
    ("9", "2024"),   # Copa América 2024
    ("6", "2023"),   # Copa Africana de Naciones 2023
    
    # --- CICLO MUNDIALISTA 2026 ---
    ("34", "2026"),  # Eliminatorias CONMEBOL (Actuales)
    ("31", "2026"),  # Eliminatorias CONCACAF (Actuales)
    ("33", "2026"),  # Eliminatorias AFC (Asia - Actuales)
    
    # --- CICLO MUNDIALISTA 2022 (Para historial profundo) ---
    ("34", "2022"),  # Eliminatorias CONMEBOL (Pasadas)
    ("31", "2022"),  # Eliminatorias CONCACAF (Pasadas)
    ("33", "2022"),  # Eliminatorias AFC (Asia - Pasadas)
    ("32", "2022")   # Eliminatorias UEFA (Europa - Pasadas)
]

lista_partidos = []
print("Iniciando extracción con Sesión Blindada...")

for id_liga, temporada in torneos_a_descargar:
    print(f"-> Solicitando ID {id_liga} (Temporada {temporada})...")
    querystring = {"league": id_liga, "season": temporada}
    
    try:
        # Usamos nuestra 'session' en lugar del 'requests' normal
        response = session.get(url, headers=headers, params=querystring, timeout=15)
        datos = response.json()
        
        resp_data = datos.get('response', [])
        
        if not resp_data:
            print("   [!] No hay partidos con ese año.")
        else:
            guardados = 0
            for item in resp_data:
                if item['fixture']['status']['short'] == 'FT':
                    partido = {
                        'torneo_id': id_liga,
                        'temporada': temporada,
                        'fecha': item['fixture']['date'].split("T")[0],
                        'local': item['teams']['home']['name'],
                        'visita': item['teams']['away']['name'],
                        'goles_local': item['goals']['home'],
                        'goles_visita': item['goals']['away']
                    }
                    lista_partidos.append(partido)
                    guardados += 1
            print(f"   [OK] Guardados {guardados} partidos.")
            
        time.sleep(6) # Pausa por Rate Limit

    except requests.exceptions.ConnectionError as e:
        print(f"   [Error fatal de conexión]: El servidor rechazó el reintento.")
    except Exception as e:
        print(f"   [Error inesperado]: {e}")

# 3. Guardar base de datos
df_partidos = pd.DataFrame(lista_partidos)
if not df_partidos.empty:
    df_partidos['fecha'] = pd.to_datetime(df_partidos['fecha'])
    df_partidos = df_partidos.sort_values('fecha')
    df_partidos.to_csv("historial_selecciones_combinado.csv", index=False, encoding='utf-8')
    print(f"\n¡Listo! Tienes {len(df_partidos)} partidos guardados.")
else:
    print("\nNo se descargaron datos.")
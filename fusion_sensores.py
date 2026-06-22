import pandas as pd
import numpy as np

def calcular_metricas_plantilla(archivo_jugadores, equipo_nombre):
    # 1. Cargar el catálogo local de jugadores
    try:
        df_jugadores = pd.read_csv(archivo_jugadores)
        
        # Blindaje dinámico de columnas
        df_jugadores.columns = df_jugadores.columns.str.strip().str.lower()
        col_eq = [c for c in df_jugadores.columns if 'equip' in c or 'team' in c][0]
        col_nom = [c for c in df_jugadores.columns if 'nom' in c or 'jug' in c][0]
        
        # Traductor de Naciones para alinear la base sucia con el simulador
        mapeo_naciones = {
            'Cape Verde': 'Cabo Verde', 'Cape Verde Islands': 'Cabo Verde',
            'United States': 'USA', 'Korea Republic': 'South Korea',
            'Korea DPR': 'North Korea', "Côte d'Ivoire": 'Ivory Coast',
            'Czech Republic': 'Czechia', 'Turkey': 'Türkiye',
            'IR Iran': 'Iran', 'Republic of Ireland': 'Ireland',
            'Bosnia-Herzegovina': 'Bosnia and Herzegovina'
        }
        df_jugadores[col_eq] = df_jugadores[col_eq].astype(str).str.strip().replace(mapeo_naciones)
        
    except Exception:
        # Valores por defecto si el archivo no existe o está corrupto
        return 50.0, 50.0

    # Filtramos la plantilla del equipo en cuestión
    plantilla = df_jugadores[df_jugadores[col_eq] == equipo_nombre].copy()
    
    if plantilla.empty:
        return 50.0, 50.0 # Retorno neutral si no hay datos

    # ==========================================
    # 🚧 ESCÁNER NEURONAL (WHITELIST FIFA) 🚧
    # ==========================================
    try:
        df_oficial = pd.read_csv('convocados_oficiales.csv')
        oficiales_equipo = df_oficial[df_oficial['Equipo'].str.contains(equipo_nombre, case=False, na=False)]
        
        if not oficiales_equipo.empty:
            def quitar_acentos(s):
                reemplazos = {'á':'a', 'é':'e', 'í':'i', 'ó':'o', 'ú':'u', 'ñ':'n', 'č':'c', 'ć':'c', 'š':'s', 'ë':'e', 'ö':'o', 'ü':'u'}
                for a, b in reemplazos.items(): s = s.replace(a, b)
                return s
                
            nombres_of_limpios = [quitar_acentos(str(n).lower()) for n in oficiales_equipo['Jugador_Oficial'].tolist()]
            
            def es_convocado_sensor(nombre_db):
                nom_db_limpio = quitar_acentos(str(nombre_db).lower())
                for nom_oficial in nombres_of_limpios:
                    # Checamos si el apellido oficial hace match
                    if nom_oficial in nom_db_limpio or nom_db_limpio in nom_oficial:
                        return True
                return False
                
            plantilla_aprobada = plantilla[plantilla[col_nom].apply(es_convocado_sensor)]
            
            # Si la criba encontró a los jugadores correctos, reemplazamos la plantilla sucia
            if not plantilla_aprobada.empty:
                plantilla = plantilla_aprobada
    except FileNotFoundError:
        pass # Si el CSV oficial no existe, calculamos con la base de datos completa (sucia)

    # 2. Definición de la Matriz de Pesos Ponderados (W) según la posición
    # Posiciones: DEL (Delantero), MED (Mediocampista), DEF (Defensa), POR (Portero)
    pesos_ataque = {'DEL': 1.0, 'MED': 0.6, 'DEF': 0.1, 'POR': 0.0}
    pesos_defensa = {'DEL': 0.1, 'MED': 0.5, 'DEF': 1.0, 'POR': 1.0}

    # 3. Aplicar la combinación lineal
    plantilla['W_ataque'] = plantilla['posicion'].map(pesos_ataque).fillna(0)
    plantilla['W_defensa'] = plantilla['posicion'].map(pesos_defensa).fillna(0)

    try:
        # Cálculo del promedio ponderado estricto (Ataque y Defensa)
        score_ataque = np.average(plantilla['rating_ataque'], weights=plantilla['W_ataque'])
        score_defensa = np.average(plantilla['rating_defensa'], weights=plantilla['W_defensa'])
    except ZeroDivisionError:
        # Prevención de crasheo si la plantilla se queda sin jugadores con peso asignado
        return 50.0, 50.0

    return round(score_ataque, 2), round(score_defensa, 2)
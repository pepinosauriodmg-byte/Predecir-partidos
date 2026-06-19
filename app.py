import streamlit as st
import pandas as pd
import requests
import motor_hibrido as mh  # Tu cerebro de IA intacto

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="AI Football Predictor 2026", layout="wide", page_icon="⚽")
st.title("⚽ Plataforma Predictiva Híbrida - Mundial 2026")

# --- VARIABLES DE API-FOOTBALL ---
# Reemplaza 'TU_API_KEY' con la llave que usaste para descargar el historial
API_KEY = "806a5e5aedb81f7f7e77e3033db6b721"  
HEADERS = {
    "x-rapidapi-host": "v3.football.api-sports.io",
    "x-rapidapi-key": API_KEY
}

# --- ALGORITMO: TOP 5 PROBABLES GANADORES (POWER INDEX V3 - LAPLACE) ---
@st.cache_data(ttl=3600)
def calcular_power_ranking():
    ranking = []
    stats_df = mh.estadisticas.set_index('equipo')
    
    for equipo in mh.dict_fa.keys():
        try:
            partidos_jugados = stats_df.loc[equipo, 'partidos']
        except KeyError:
            partidos_jugados = 0
            
        # Aumentamos el filtro a 15 partidos para limpiar selecciones pequeñas
        if partidos_jugados < 15:
            continue
            
        fa = mh.dict_fa.get(equipo, 1.0)
        fd = mh.dict_fd.get(equipo, 1.0) 
        atq = mh.dict_plantilla_atq.get(equipo, 50.0)
        dfn = mh.dict_plantilla_def.get(equipo, 50.0)
        
        # EL SUAVIZADO: 
        # 1. Multiplicamos la historia por el nivel de los jugadores actuales.
        poder_ofensivo = fa * atq
        
        # 2. Invertimos la defensa (100 - dfn = vulnerabilidad) y aplicamos Suavizado de Laplace (+1.0)
        # Esto destruye el "Efecto Oceanía" porque impide que el divisor sea cero.
        vulnerabilidad_plantilla = max(1.0, (100.0 - dfn))
        fragilidad_defensiva = (fd + 1.0) * vulnerabilidad_plantilla
        
        # Ecuación de Índice de Poder final
        power_index = (poder_ofensivo / fragilidad_defensiva) * 100
        
        ranking.append({'Equipo': equipo, 'Power Index': round(power_index, 2)})
        
    df_ranking = pd.DataFrame(ranking).sort_values(by='Power Index', ascending=False).head(5)
    df_ranking.reset_index(drop=True, inplace=True)
    df_ranking.index += 1
    return df_ranking

# --- ALGORITMO: MARCADORES EN VIVO (API-FOOTBALL) ---
def obtener_marcadores_vivo():
    try:
        # CORRECCIÓN: Agregamos &league=1 para filtrar SOLO partidos de la Copa del Mundo
        url = "https://v3.football.api-sports.io/fixtures?live=all&league=1"
        response = requests.get(url, headers=HEADERS, timeout=5)
        datos = response.json()
        
        if not datos.get('response'):
            return ["No hay partidos de la Copa del Mundo en vivo en este momento."]
            
        resultados = []
        for partido in datos['response']:
            local = partido['teams']['home']['name']
            visita = partido['teams']['away']['name']
            goles_local = partido['goals']['home']
            goles_visita = partido['goals']['away']
            minuto = partido['fixture']['status']['elapsed']
            resultados.append(f"🏆 {minuto}' | {local} {goles_local} - {goles_visita} {visita}")
            
        return resultados
    except Exception as e:
        return ["Error al conectar con el satélite de la API."]

# ==========================================
# INTERFAZ WEB (FRONTEND)
# ==========================================

# Dividimos la pantalla en 3 columnas
col1, col2, col3 = st.columns([1, 2, 1])

# --- COLUMNA 1: MARCADORES EN VIVO ---
with col1:
    st.subheader("🔴 En Vivo")
    if st.button("Actualizar Marcadores"):
        marcadores = obtener_marcadores_vivo()
        if isinstance(marcadores, list):
            for m in marcadores:
                st.info(m)
        else:
            st.write(marcadores)
    else:
        st.write("Presiona para conectar al satélite de API-Football.")

# --- COLUMNA 2: EL MOTOR DE PREDICCIÓN ---
with col2:
    st.subheader("Simulador de Enfrentamientos")
    equipos_disponibles = sorted(list(mh.dict_fa.keys()))
    
    # Selectores web (Reemplazan a los combobox de Tkinter)
    eq_a = st.selectbox("Selecciona Equipo Local:", equipos_disponibles, index=equipos_disponibles.index("Mexico") if "Mexico" in equipos_disponibles else 0)
    eq_b = st.selectbox("Selecciona Equipo Visitante:", equipos_disponibles, index=equipos_disponibles.index("Germany") if "Germany" in equipos_disponibles else 1)
    
    if st.button("Predecir", use_container_width=True):
        if eq_a == eq_b:
            st.warning("¡Selecciona dos equipos diferentes!")
        else:
            with st.spinner("Fusionando variables históricas y de plantilla..."):
                xg_a, xg_b, probs = mh.predecir_partido(eq_a, eq_b)
                
                if xg_a is not None:
                    # Probabilidades suelen ser [Derrota_A, Empate, Victoria_A] o similar, 
                    # asumiendo orden: [Derrota Local, Empate, Victoria Local] según tu modelo
                    prob_visita = probs[0] * 100
                    prob_empate = probs[1] * 100
                    prob_local  = probs[2] * 100
                    
                    st.success("Análisis Completado")
                    
                    # Barras de progreso visuales
                    st.write(f"**Victoria {eq_a}:** {prob_local:.1f}%")
                    st.progress(int(prob_local))
                    
                    st.write(f"**Empate:** {prob_empate:.1f}%")
                    st.progress(int(prob_empate))
                    
                    st.write(f"**Victoria {eq_b}:** {prob_visita:.1f}%")
                    st.progress(int(prob_visita))
                    
                    st.caption(f"xG (Goles Esperados): {eq_a} {xg_a:.2f} - {xg_b:.2f} {eq_b}")
                else:
                    st.error("Datos insuficientes para uno de los equipos.")

# --- COLUMNA 3: TOP 5 FAVORITOS ---
with col3:
    st.subheader("🏆 Power Ranking Top 5")
    st.caption("Basado en el algoritmo híbrido FA/FD y forma en vivo")
    df_top5 = calcular_power_ranking()
    
    # Mostramos la tabla formateada
    st.dataframe(df_top5, use_container_width=True)
    
 
    
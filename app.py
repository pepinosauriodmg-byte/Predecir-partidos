import streamlit as st
import pandas as pd
import motor_hibrido as mh

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(page_title="AI Football Predictor 2026", layout="wide", page_icon="⚽")
st.title("⚽ Plataforma Predictiva Híbrida - Mundial 2026")

# ==========================================
# 2. MOTOR DE POWER RANKING (SUAVIZADO DE LAPLACE)
# ==========================================
@st.cache_data(ttl=3600)
def calcular_power_ranking():
    ranking = []
    stats_df = mh.estadisticas.set_index('equipo')
    
    for equipo in mh.dict_fa.keys():
        try:
            partidos_jugados = stats_df.loc[equipo, 'partidos']
        except KeyError:
            partidos_jugados = 0
            
        # Filtro de 15 partidos para limpiar selecciones pequeñas
        if partidos_jugados < 15:
            continue
            
        fa = mh.dict_fa.get(equipo, 1.0)
        fd = mh.dict_fd.get(equipo, 1.0) 
        atq = mh.dict_plantilla_atq.get(equipo, 50.0)
        dfn = mh.dict_plantilla_def.get(equipo, 50.0)
        
        poder_ofensivo = fa * atq
        vulnerabilidad_plantilla = max(1.0, (100.0 - dfn))
        fragilidad_defensiva = (fd + 1.0) * vulnerabilidad_plantilla
        
        power_index = (poder_ofensivo / fragilidad_defensiva) * 100
        ranking.append({'Equipo': equipo, 'Power Index': round(power_index, 2)})
        
    df_ranking = pd.DataFrame(ranking).sort_values(by='Power Index', ascending=False).head(5)
    df_ranking.reset_index(drop=True, inplace=True)
    df_ranking.index += 1
    return df_ranking

# ==========================================
# 3. MAQUETACIÓN PRINCIPAL
# ==========================================
col_principal, col_ranking = st.columns([2, 1])

with col_ranking:
    st.subheader("🏆 Power Ranking Top 5")
    st.caption("Basado en algoritmo híbrido FA/FD y forma en vivo")
    df_ranking = calcular_power_ranking()
    st.dataframe(df_ranking, use_container_width=True)

with col_principal:
    tab1, tab2, tab3 = st.tabs(["🔮 Simulador", "📊 Resultados Recientes", "📅 Próxima Jornada"])

    # --- PESTAÑA 1: SIMULADOR MANUAL ---
    with tab1:
        st.subheader("Simulador de Enfrentamientos")
        equipos = sorted(list(mh.dict_fa.keys()))
        
        c1, c2 = st.columns(2)
        with c1:
            idx_local = equipos.index('Mexico') if 'Mexico' in equipos else 0
            local = st.selectbox("Selecciona Equipo Local:", equipos, index=idx_local)
        with c2:
            idx_visita = equipos.index('South Korea') if 'South Korea' in equipos else 1
            visitante = st.selectbox("Selecciona Equipo Visitante:", equipos, index=idx_visita)
            
        if st.button("Predecir", use_container_width=True):
            p_local, p_empate, p_visita = mh.predecir_partido(local, visitante)
            
            # EL FIX DE INGENIERÍA: Forzamos la matriz a convertirse en número Float
            p_local = float(p_local)
            p_empate = float(p_empate)
            p_visita = float(p_visita)
            
            st.success("Análisis Completado")
            
            st.write(f"**Victoria {local}: {p_local*100:.1f}%**")
            st.progress(p_local)
            
            st.write(f"**Empate: {p_empate*100:.1f}%**")
            st.progress(p_empate)
            
            st.write(f"**Victoria {visitante}: {p_visita*100:.1f}%**")
            st.progress(p_visita)

    # --- PESTAÑA 2: RESULTADOS RECIENTES ---
    with tab2:
        st.subheader("🏁 Historial de Partidos Jugados")
        try:
            df_partidos = pd.read_csv('partidos_manuales.csv')
            df_recientes = df_partidos.iloc[::-1]
            st.dataframe(df_recientes, use_container_width=True, hide_index=True)
        except FileNotFoundError:
            st.warning("Aún no hay datos guardados en 'partidos_manuales.csv'.")

    # --- PESTAÑA 3: PRÓXIMA JORNADA ---
    with tab3:
        st.subheader("🔮 Predicciones de la IA para Mañana")
        st.caption("Procesamiento automático por lotes.")
        
        partidos_manana = [
            ('Germany', 'Spain'),
            ('Brazil', 'France'),
            ('Argentina', 'England')
        ]
        
        for eq_l, eq_v in partidos_manana:
            if eq_l in equipos and eq_v in equipos:
                with st.expander(f"🏟️ {eq_l} vs {eq_v}"):
                    p_l, p_e, p_v = mh.predecir_partido(eq_l, eq_v)
                    
                    # EL FIX DE INGENIERÍA: Forzamos a Float para que Streamlit pueda imprimirlos
                    p_l, p_e, p_v = float(p_l), float(p_e), float(p_v)
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric(label=f"Gana {eq_l}", value=f"{p_l*100:.1f}%")
                    m2.metric(label="Empate", value=f"{p_e*100:.1f}%")
                    m3.metric(label=f"Gana {eq_v}", value=f"{p_v*100:.1f}%")
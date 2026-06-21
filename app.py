import streamlit as st
import pandas as pd
import numpy as np
import motor_hibrido as mh

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILO FRUTIGER AERO
# ==========================================
st.set_page_config(page_title="AI Football Predictor 2026", layout="wide", page_icon="⚽")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #022c22 50%, #0369a1 100%); }
    .frutiger-title {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 800;
        background: linear-gradient(to right, #38bdf8, #4ade80, #0ea5e9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 4px 12px rgba(56, 189, 248, 0.3);
        margin-bottom: 20px;
    }
    .frutiger-card {
        background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 168, 255, 0.15), inset 0 4px 4px rgba(255,255,255,0.1);
        margin-bottom: 15px;
    }
    .match-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.1) 0%, rgba(74, 222, 128, 0.1) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 12px 25px;
        margin-bottom: 10px;
        box-shadow: inset 0 2px 4px rgba(255,255,255,0.05);
    }
    .team-box {
        font-size: 1.15rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 10px;
        color: #f8fafc;
    }
    .score-box {
        background: rgba(14, 165, 233, 0.3);
        border: 1px solid #38bdf8;
        padding: 4px 16px;
        border-radius: 20px;
        font-size: 1.2rem;
        font-weight: 700;
        color: #fff;
        text-shadow: 0 0 8px #38bdf8;
    }
    .stButton>button {
        background: linear-gradient(180deg, #4ade80 0%, #22c55e 50%, #15803d 100%) !important;
        color: white !important;
        border: 1px solid #86efac !important;
        border-radius: 25px !important;
        padding: 10px 24px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 15px rgba(34, 197, 94, 0.4), inset 0 2px 2px rgba(255,255,255,0.4) !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) scale(1.01);
        box-shadow: 0 6px 20px rgba(34, 197, 94, 0.6), inset 0 3px 3px rgba(255,255,255,0.5) !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='frutiger-title'>⚽ Plataforma Predictiva Híbrida - Mundial 2026</h1>", unsafe_allow_html=True)

# ==========================================
# 2. DICCIONARIO MAESTRO DE BANDERAS (ULTRA EXPANDIDO)
# ==========================================
DICT_BANDERAS = {
    # Los que ya teníamos
    'Scotland': '🏴󠁧󠁢󠁳󠁣󠁴󠁿', 'Morocco': '🇲🇦', 'Mexico': '🇲🇽', 'South Korea': '🇰🇷',
    'Argentina': '🇦🇷', 'Brazil': '🇧🇷', 'France': '🇫🇷', 'Spain': '🇪🇸',
    'Germany': '🇩🇪', 'England': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'Canada': '🇨🇦', 'USA': '🇺🇸',
    'Colombia': '🇨🇴', 'Qatar': '🇶🇦', 'Ghana': '🇬🇭', 'Panama': '🇵🇦',
    'Uzbekistan': '🇺🇿', 'Czechia': '🇨🇿', 'South Africa': '🇿🇦', 'Switzerland': '🇨🇭',
    'Bosnia and Herzegovina': '🇧🇦', 'Netherlands': '🇳🇱', 'Sweden': '🇸🇪', 
    'Ivory Coast': '🇨🇮', "Côte d'Ivoire": '🇨🇮', 'Haiti': '🇭🇹', 'Türkiye': '🇹🇷', 
    'Turkey': '🇹🇷', 'Paraguay': '🇵🇾', 'Japan': '🇯🇵', 'Croatia': '🇭🇷', 
    'Cabo Verde': '🇨🇻', 'Cape Verde': '🇨🇻', 'DR Congo': '🇨🇩', 'Tunisia': '🇹🇳', 
    'Australia': '🇦🇺', 'Portugal': '🇵🇹', 'Italy': '🇮🇹', 'Uruguay': '🇺🇾', 
    'Belgium': '🇧🇪', 'Senegal': '🇸🇳', 'Cameroon': '🇨🇲', 'Nigeria': '🇳🇬', 
    'Iran': '🇮🇷', 'Saudi Arabia': '🇸🇦', 'Ecuador': '🇪🇨', 'Chile': '🇨🇱', 'Peru': '🇵🇪',
    
    # --- LOS NUEVOS DE TU CAPTURA ---
    'Austria': '🇦🇹', 'Jordan': '🇯🇴', 'Algeria': '🇩🇿', 'Iraq': '🇮🇶',
    'Norway': '🇳🇴', 'New Zealand': '🇳🇿', 'Egypt': '🇪🇬',
    
    # --- OTROS POSIBLES DE ELIMINATORIAS / MUNDIAL ---
    'Wales': '🏴󠁧󠁢󠁷󠁬󠁳󠁿', 'Denmark': '🇩🇰', 'Serbia': '🇷🇸', 'Poland': '🇵🇱',
    'Ukraine': '🇺🇦', 'Mali': '🇲🇱', 'Costa Rica': '🇨🇷', 'Jamaica': '🇯🇲',
    'Honduras': '🇭🇳', 'Venezuela': '🇻🇪', 'Bolivia': '🇧🇴', 'Greece': '🇬🇷',
    'Hungary': '🇭🇺', 'Romania': '🇷🇴', 'Slovakia': '🇸🇰', 'Slovenia': '🇸🇮',
    'Albania': '🇦🇱', 'Georgia': '🇬🇪', 'China PR': '🇨🇳', 'China': '🇨🇳', 
    'UAE': '🇦🇪', 'Oman': '🇴🇲', 'Bahrain': '🇧🇭', 'Syria': '🇸🇾',
    'Curaçao': '🇨🇼', 'Curacao': '🇨🇼',
    'North Macedonia': '🇲🇰', 'Macedonia': '🇲🇰', 'Republic of Ireland': '🇮🇪'
}

def obtener_bandera(equipo):
    return DICT_BANDERAS.get(equipo, '⚽')

# ==========================================
# 3. MOTOR DE POWER RANKING
# ==========================================
@st.cache_data(ttl=3600)
def calcular_power_ranking():
    ranking = []
    stats_df = mh.estadisticas.set_index('equipo')
    
    # --- NUEVO FILTRO: TU LISTA MANUAL ---
    try:
        # Leemos exclusivamente los partidos que tú has registrado
        df_manuales = pd.read_csv('partidos_manuales.csv')
        # Unimos las columnas de local y visita para sacar la lista única de participantes reales
        equipos_clasificados = pd.concat([df_manuales['local'], df_manuales['visita']]).unique()
    except FileNotFoundError:
        # Fallback de seguridad en caso de que el archivo no exista
        equipos_clasificados = mh.dict_fa.keys()
    # -------------------------------------
    
    for equipo in mh.dict_fa.keys():
        # El muro: Si el equipo no está en tu lista manual de partidos, lo ignoramos
        if equipo not in equipos_clasificados:
            continue
            
        try:
            partidos_jugados = stats_df.loc[equipo, 'partidos']
        except KeyError:
            partidos_jugados = 0
            
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
# 4. MAQUETACIÓN PRINCIPAL
# ==========================================
col_principal, col_ranking = st.columns([2, 1])

with col_ranking:
    st.markdown("<div class='frutiger-card'>", unsafe_allow_html=True)
    st.subheader("🏆 Power Ranking Top 5")
    st.caption("Algoritmo híbrido FA/FD con suavizado de Laplace")
    df_ranking = calcular_power_ranking()
    
    df_ranking_visual = df_ranking.copy()
    df_ranking_visual['Equipo'] = df_ranking_visual['Equipo'].apply(lambda x: f"{obtener_bandera(x)} {x}")
    st.dataframe(df_ranking_visual, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_principal:
    tab1, tab2, tab3 = st.tabs(["🔮 Simulador", "📊 Partidos Recientes", "📅 Próxima Jornada"])

    # --- PESTAÑA 1: SIMULADOR MANUAL ---
    with tab1:
        st.markdown("<div class='frutiger-card'>", unsafe_allow_html=True)
        st.subheader("Simulador de Enfrentamientos Directos")
        equipos = sorted(list(mh.dict_fa.keys()))
        
        c1, c2 = st.columns(2)
        with c1:
            idx_local = equipos.index('Scotland') if 'Scotland' in equipos else 0
            local = st.selectbox("Equipo Local:", equipos, index=idx_local)
        with c2:
            idx_visita = equipos.index('Morocco') if 'Morocco' in equipos else 1
            visitante = st.selectbox("Equipo Visitante:", equipos, index=idx_visita)
            
        if st.button("PREDECIR", use_container_width=True):
            xg_l, xg_v, paquete_probs = mh.predecir_partido(local, visitante)
            probs_flat = np.array(paquete_probs).flatten()
            
            p_visita = float(probs_flat[0]) 
            p_empate = float(probs_flat[1])
            p_local = float(probs_flat[2])
            
            st.success("Cómputo Neuronal Exitoso")
            
            bandera_l = obtener_bandera(local)
            bandera_v = obtener_bandera(visitante)
            
            st.markdown(f"""
            <div style='background: rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); margin: 15px 0; text-align: center;'>
                <div style='font-size: 2.2rem; margin-bottom: 5px;'>
                    {bandera_l} <span style='font-weight: 800; color: #fff;'>{local}</span> 
                    <span style='color: #4ade80;'>vs</span> 
                    <span style='font-weight: 800; color: #fff;'>{visitante}</span> {bandera_v}
                </div>
                <div style='font-size: 1.3rem; color: #38bdf8; font-weight: 600; font-family: monospace;'>
                    xG Estimado: {float(xg_l):.2f} - {float(xg_v):.2f}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.write(f"**Probabilidad Gana {local} {bandera_l}: {p_local*100:.1f}%**")
            st.progress(p_local)
            
            st.write(f"**Probabilidad de Empate 🤝: {p_empate*100:.1f}%**")
            st.progress(p_empate)
            
            st.write(f"**Probabilidad Gana {visitante} {bandera_v}: {p_visita*100:.1f}%**")
            st.progress(p_visita)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- PESTAÑA 2: RESULTADOS RECIENTES ---
    with tab2:
        st.markdown("<div class='frutiger-card'>", unsafe_allow_html=True)
        st.subheader("🏁 Historial de Partidos Jugados (Control Manual)")
        try:
            df_partidos = pd.read_csv('partidos_manuales.csv')
            df_recientes = df_partidos.iloc[::-1]
            
            for _, row in df_recientes.iterrows():
                loc = row['local']
                vis = row['visita']
                gl = row['goles_local']
                gv = row['goles_visita']
                
                st.markdown(f"""
                <div class='match-row'>
                    <div class='team-box'>{obtener_bandera(loc)} {loc}</div>
                    <div class='score-box'>{gl} - {gv}</div>
                    <div class='team-box' style='justify-content: flex-end;'>{vis} {obtener_bandera(vis)}</div>
                </div>
                """, unsafe_allow_html=True)
                
        except FileNotFoundError:
            st.warning("Aún no hay registros en 'partidos_manuales.csv'.")
        except KeyError:
            st.error("Error leyendo las columnas del CSV. Verifica los nombres 'local', 'visita', 'goles_local', 'goles_visita'.")
        st.markdown("</div>", unsafe_allow_html=True)

# --- PESTAÑA 3: PRÓXIMA JORNADA ---
    with tab3:
        st.markdown("<div class='frutiger-card'>", unsafe_allow_html=True)
        st.subheader("📅 Predicciones automáticas para Mañana")
        st.caption("Análisis avanzado y contexto histórico de los contendientes.")
        
        partidos_manana = [
            ('Netherlands', 'Sweden'), 
            ('Germany', 'Ivory Coast'),     
            ('Tunisia', 'Japan'),
            ('Ecuador', 'Curaçao')
        ]
        
      # --- FUNCIÓN AUXILIAR: HISTORIAL RECIENTE (10 Partidos + Fecha Estandarizada) ---
        def obtener_historial_reciente(equipo, limite=10):
            try:
                # 1. Cargamos el pasado
                df_historico = pd.read_csv('historial_selecciones_combinado.csv')
                
                # 2. Cargamos el presente
                try:
                    df_manual = pd.read_csv('partidos_manuales.csv')
                    df_combinado = pd.concat([df_historico, df_manual], ignore_index=True)
                except FileNotFoundError:
                    df_combinado = df_historico
                
                # 3. LIMPIEZA TOTAL DE COLUMNAS (Adiós errores por Mayúsculas o Espacios)
                df_combinado.columns = df_combinado.columns.str.strip().str.lower()
                
                # 4. Mapeo dinámico de columnas clave por si cambian de nombre
                col_local = [c for c in df_combinado.columns if 'local' in c or 'home' in c][0]
                col_visita = [c for c in df_combinado.columns if 'visit' in c or 'away' in c][0]
                col_g_loc = [c for c in df_combinado.columns if 'goles_local' in c or 'score' in c or 'goles_l' in c][0]
                col_g_vis = [c for c in df_combinado.columns if 'goles_visita' in c or 'score' in c or 'goles_v' in c][0]
                
                # Buscador elástico de fecha (detecta 'date', 'fecha', 'fecha_partido', etc.)
                col_fecha = [c for c in df_combinado.columns if 'dat' in c or 'fech' in c]
                col_fecha = col_fecha[0] if col_fecha else None
                
                # 5. Filtramos al equipo utilizando las columnas normalizadas
                partidos_equipo = df_combinado[(df_combinado[col_local] == equipo) | (df_combinado[col_visita] == equipo)].copy()
                
                # 6. ORDEN CRONOLÓGICO SEGURO
                if col_fecha:
                    partidos_equipo[col_fecha] = pd.to_datetime(partidos_equipo[col_fecha], errors='coerce')
                    partidos_equipo = partidos_equipo.sort_values(by=col_fecha, ascending=True)
                
                # 7. Tomamos los últimos 10 y los invertimos para que el más nuevo salga arriba
                ultimos = partidos_equipo.tail(limite).iloc[::-1]
                
                resultados = []
                for _, p in ultimos.iterrows():
                    es_local = (p[col_local] == equipo)
                    rival = p[col_visita] if es_local else p[col_local]
                    
                    gf = int(p[col_g_loc] if es_local else p[col_g_vis])
                    gc = int(p[col_g_vis] if es_local else p[col_g_loc])
                    
                    if gf > gc: res = "✅ Victoria"
                    elif gf < gc: res = "❌ Derrota "
                    else: res = "➖ Empate "
                    
                    # Formateo de fecha ultra-limpio sin importar el formato origen
                    if col_fecha and not pd.isna(p[col_fecha]):
                        fecha_str = str(p[col_fecha]).split(' ')[0] # Corta a "YYYY-MM-DD"
                    else:
                        fecha_str = "Fecha N/D"
                        
                    resultados.append(f"📅 {fecha_str} | {res} vs **{rival}** ({gf} - {gc})")
                    
                if not resultados:
                    return ["Aún no hay historial registrado."]
                return resultados
            except Exception as e:
                return [f"Error al cargar historial: {e}"]

        # --- FUNCIÓN AUXILIAR: TOP JUGADORES (Búsqueda Blindada) ---
        def obtener_top_jugadores(equipo, top=3):
            try:
                df_jugadores = pd.read_csv('rendimiento_jugadores.csv')
                
                # Limpiamos todos los nombres de columnas (quitar espacios invisibles y mayúsculas)
                df_jugadores.columns = df_jugadores.columns.str.strip().str.lower()
                
                # Encontramos las columnas sin importar cómo se llamen (usamos índices si fallan los nombres)
                col_eq = [c for c in df_jugadores.columns if 'equip' in c or 'team' in c]
                col_eq = col_eq[0] if col_eq else df_jugadores.columns[0]
                
                col_nom = [c for c in df_jugadores.columns if 'nom' in c or 'jug' in c or 'play' in c]
                col_nom = col_nom[0] if col_nom else df_jugadores.columns[1]
                
                col_rat = [c for c in df_jugadores.columns if 'rat' in c or 'cal' in c or 'pun' in c]
                col_rat = col_rat[0] if col_rat else df_jugadores.columns[2]
                
                col_pos = [c for c in df_jugadores.columns if 'pos' in c]
                col_pos = col_pos[0] if col_pos else df_jugadores.columns[3]
                
                # Filtramos el equipo (ignoramos mayúsculas/minúsculas para que sea perfecto)
                plantilla = df_jugadores[df_jugadores[col_eq].astype(str).str.contains(equipo, case=False, na=False)].copy()
                
                if plantilla.empty:
                    return [f"Sin datos registrados para {equipo}"]
                
                # Convertimos calificaciones a números forzosamente y ordenamos
                plantilla[col_rat] = pd.to_numeric(plantilla[col_rat], errors='coerce').fillna(0)
                plantilla = plantilla.sort_values(by=col_rat, ascending=False).head(top)
                
                top_str = []
                for _, j in plantilla.iterrows():
                    top_str.append(f"⭐ {j[col_nom]} ({j[col_pos]}): **{j[col_rat]}**")
                return top_str
            except Exception as e:
                # Si llega a fallar, te mostrará el error exacto en pantalla para debuggear
                return [f"Error leyendo jugadores: {str(e)[:40]}"]

        # --- RENDERIZADO DE PARTIDOS ---
        for eq_l, eq_v in partidos_manana:
            if eq_l in equipos and eq_v in equipos:
                b_l = obtener_bandera(eq_l)
                b_v = obtener_bandera(eq_v)
                
                with st.expander(f"🏟️ {b_l} {eq_l} vs {eq_v} {b_v}"):
                    xg_l, xg_v, paquete_probs = mh.predecir_partido(eq_l, eq_v)
                    probs_flat = np.array(paquete_probs).flatten()
                    
                    p_v = float(probs_flat[0])
                    p_e = float(probs_flat[1])
                    p_l = float(probs_flat[2])
                    
                    st.markdown(f"""
                    <div style='text-align: center; margin-bottom: 15px; font-family: monospace; font-size: 1.1rem; color: #4ade80;'>
                        <b>xG Esperado de Poisson:</b> {float(xg_l):.2f} - {float(xg_v):.2f}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric(label=f"Gana {eq_l} {b_l}", value=f"{p_l*100:.1f}%")
                    m2.metric(label="Empate 🤝", value=f"{p_e*100:.1f}%")
                    m3.metric(label=f"Gana {eq_v} {b_v}", value=f"{p_v*100:.1f}%")
                    
                    st.divider()
                    
                    st.markdown("##### 🔍 Justificación Estadística en Vivo")
                    
                    col_info_l, col_info_v = st.columns(2)
                    
                    with col_info_l:
                        st.markdown(f"**{b_l} Estado de {eq_l}**")
                        
                        st.caption("🌟 MVPs del Torneo:")
                        for j in obtener_top_jugadores(eq_l):
                            st.write(f"<small>{j}</small>", unsafe_allow_html=True)
                        
                        st.write("") 
                        st.caption("📈 Últimos 10 Partidos:") # <- ¡Ya dice 10!
                        for h in obtener_historial_reciente(eq_l):
                            st.write(f"<small>{h}</small>", unsafe_allow_html=True)

                    with col_info_v:
                        st.markdown(f"**{b_v} Estado de {eq_v}**")
                        
                        st.caption("🌟 MVPs del Torneo:")
                        for j in obtener_top_jugadores(eq_v):
                            st.write(f"<small>{j}</small>", unsafe_allow_html=True)
                        
                        st.write("") 
                        st.caption("📈 Últimos 10 Partidos:") # <- ¡Ya dice 10!
                        for h in obtener_historial_reciente(eq_v):
                            st.write(f"<small>{h}</small>", unsafe_allow_html=True)

            else:
                st.warning(f"Error de nombre en la base: {eq_l} vs {eq_v}")
        st.markdown("</div>", unsafe_allow_html=True)

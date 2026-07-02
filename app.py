import streamlit as st
import pandas as pd
import numpy as np
import motor_hibrido as mh
import re

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILO WINDOWS VISTA AERO
# ==========================================
st.set_page_config(page_title="AI Football Predictor 2026", layout="wide", page_icon="⚽")

st.markdown("""
<style>
    .stApp { 
        background: radial-gradient(circle at 15% 50%, rgba(31, 143, 166, 0.4), transparent 40%),
                    radial-gradient(circle at 85% 30%, rgba(74, 222, 128, 0.25), transparent 50%),
                    linear-gradient(135deg, #02111d 0%, #032b38 50%, #000000 100%);
        background-attachment: fixed;
    }
    html, body, [class*="css"] { font-family: Tahoma, 'Trebuchet MS', Arial, sans-serif !important; }
    .frutiger-title { font-weight: bold; color: #ffffff; text-shadow: 0px 0px 10px rgba(255,255,255,0.4), 2px 4px 5px rgba(0,0,0,0.8); margin-bottom: 20px; letter-spacing: 0.5px; }
    .frutiger-card { background: rgba(20, 30, 40, 0.45); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.15); border-top: 1px solid rgba(255, 255, 255, 0.5); border-left: 1px solid rgba(255, 255, 255, 0.25); border-radius: 8px; padding: 20px; box-shadow: 0 15px 30px rgba(0,0,0,0.6), inset 0 1px 2px rgba(255,255,255,0.2); margin-bottom: 15px; color: #f8fafc; }
    .match-row { display: flex; justify-content: space-between; align-items: center; background: rgba(0, 0, 0, 0.35); border: 1px solid rgba(255, 255, 255, 0.05); border-bottom: 1px solid rgba(255, 255, 255, 0.2); border-radius: 6px; padding: 12px 25px; margin-bottom: 10px; box-shadow: inset 0 3px 8px rgba(0,0,0,0.5); }
    .team-box { font-size: 1.15rem; font-weight: bold; display: flex; align-items: center; gap: 10px; color: #ffffff; text-shadow: 1px 1px 3px black; }
    .score-box { background: linear-gradient(to bottom, #59c0ea 0%, #2098d3 49%, #0570b0 50%, #0087ce 100%); border: 1px solid #002244; padding: 4px 16px; border-radius: 12px; font-size: 1.2rem; font-weight: bold; color: #fff; box-shadow: inset 0 2px 2px rgba(255, 255, 255, 0.6), 0 2px 5px rgba(0,0,0,0.5); text-shadow: 0 -1px 1px rgba(0,0,0,0.6); }
    .stButton>button { background: linear-gradient(to bottom, #8fde62 0%, #57b32c 49%, #368a12 50%, #46a31d 100%) !important; color: white !important; border: 1px solid #1a4d04 !important; border-radius: 20px !important; padding: 10px 24px !important; font-weight: bold !important; box-shadow: inset 0 2px 3px rgba(255, 255, 255, 0.7), 0 4px 8px rgba(0,0,0,0.5) !important; transition: all 0.2s ease-in-out !important; text-shadow: 0 -1px 1px rgba(0,0,0,0.6) !important; }
    .stButton>button:hover { background: linear-gradient(to bottom, #bdf09e 0%, #7ce053 49%, #58b82a 50%, #76d640 100%) !important; box-shadow: inset 0 0 10px rgba(255, 255, 255, 0.9), 0 0 15px rgba(164, 230, 125, 0.9), 0 4px 10px rgba(0,0,0,0.5) !important; border: 1px solid #c2f59d !important; }
    div[data-baseweb="tab-highlight"] { display: none !important; }
    button[data-baseweb="tab"] { background: linear-gradient(to bottom, #fcfcfc 0%, #e6e6e6 49%, #d4d4d4 50%, #e2e2e2 100%) !important; border: 1px solid #8e8f8f !important; border-radius: 5px !important; color: #333333 !important; padding: 6px 18px !important; margin-right: 8px !important; font-weight: bold !important; box-shadow: inset 0 1px 2px #ffffff, 0 2px 4px rgba(0,0,0,0.3) !important; transition: all 0.2s ease !important; }
    button[data-baseweb="tab"]:hover { background: linear-gradient(to bottom, #f2fafe 0%, #ccedfb 49%, #aedef7 50%, #cdeaf8 100%) !important; border: 1px solid #75b4e3 !important; box-shadow: inset 0 0 8px rgba(255,255,255,1), 0 0 12px rgba(117, 180, 227, 0.8) !important; }
    button[data-baseweb="tab"][aria-selected="true"] { background: linear-gradient(to bottom, #dcedf8 0%, #8ebce3 49%, #5c9cdb 50%, #85bce4 100%) !important; border: 1px solid #1a3b5c !important; color: #ffffff !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.7) !important; box-shadow: inset 0 1px 3px rgba(255,255,255,0.6), 0 3px 6px rgba(0,0,0,0.4) !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1.5 MOTOR DE ICONOS 3D SKEUOMORPHIC
# ==========================================
ICONS = {
    "balon": "https://img.icons8.com/3d-fluency/96/soccer-ball.png",
    "check": "https://img.icons8.com/3d-fluency/96/ok.png",
    "cross": "https://img.icons8.com/3d-fluency/96/cancel.png",
    "empate": "https://img.icons8.com/3d-fluency/96/minus.png",
    "star": "https://img.icons8.com/3d-fluency/96/star.png",
    "calendar": "https://img.icons8.com/3d-fluency/96/calendar.png",
    "chart": "https://img.icons8.com/3d-fluency/96/bar-chart.png",
    "search": "https://img.icons8.com/3d-fluency/96/search.png",
    "trophy": "https://img.icons8.com/3d-fluency/96/trophy.png",
    "simulador": "https://img.icons8.com/3d-fluency/96/idea.png",
    "historial": "https://img.icons8.com/3d-fluency/96/time.png",
    "handshake": "https://img.icons8.com/3d-fluency/96/handshake.png",
    "robot": "https://img.icons8.com/3d-fluency/96/bot.png"
}

def icon(name, size=24):
    url = ICONS.get(name, ICONS["balon"])
    return f"<img src='{url}' width='{size}' height='{size}' style='vertical-align: text-bottom; margin-right: 8px; filter: drop-shadow(2px 5px 6px rgba(0,0,0,0.8));'>"

st.markdown(f"<h1 class='frutiger-title'>{icon('balon', 48)} Plataforma Predictiva Híbrida - Mundial 2026</h1>", unsafe_allow_html=True)

# ==========================================
# 2. DICCIONARIO MAESTRO DE BANDERAS
# ==========================================
DICT_BANDERAS = {
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
    'Austria': '🇦🇹', 'Jordan': '🇯🇴', 'Algeria': '🇩🇿', 'Iraq': '🇮🇶',
    'Norway': '🇳🇴', 'New Zealand': '🇳🇿', 'Egypt': '🇪🇬', 'Wales': '🏴󠁧󠁢󠁷󠁬󠁳󠁿', 
    'Denmark': '🇩🇰', 'Serbia': '🇷🇸', 'Poland': '🇵🇱', 'Ukraine': '🇺🇦', 
    'Mali': '🇲🇱', 'Costa Rica': '🇨🇷', 'Jamaica': '🇯🇲', 'Honduras': '🇭🇳', 
    'Venezuela': '🇻🇪', 'Bolivia': '🇧🇴', 'Greece': '🇬🇷', 'Hungary': '🇭🇺', 
    'Romania': '🇷🇴', 'Slovakia': '🇸🇰', 'Slovenia': '🇸🇮', 'Albania': '🇦🇱', 
    'Georgia': '🇬🇪', 'China PR': '🇨🇳', 'China': '🇨🇳', 'UAE': '🇦🇪', 
    'Oman': '🇴🇲', 'Bahrain': '🇧🇭', 'Syria': '🇸🇾', 'Curaçao': '🇨🇼', 
    'Curacao': '🇨🇼', 'North Macedonia': '🇲🇰', 'Macedonia': '🇲🇰', 'Republic of Ireland': '🇮🇪'
}

def obtener_bandera(equipo):
    return DICT_BANDERAS.get(equipo, '⚽')

# ==========================================
# 3. MOTOR DE POWER RANKING (HÍBRIDO VERDADERO - ANCLADO A ELO)
# ==========================================
@st.cache_data(ttl=3600)
def calcular_power_ranking():
    ranking = []
    stats_df = mh.estadisticas.set_index('equipo')
    
    # 1. Lectura blindada del CSV de ELO
    try:
        df_elo = pd.read_csv('ranking_elo_vivo.csv')
        df_elo.columns = df_elo.columns.str.strip().str.lower()
        col_eq_elo = [c for c in df_elo.columns if 'equip' in c or 'team' in c or 'selec' in c][0]
        col_val_elo = [c for c in df_elo.columns if 'elo' in c or 'punt' in c or 'score' in c or 'rank' in c][0]
        df_elo = df_elo.set_index(col_eq_elo)
    except Exception:
        df_elo = pd.DataFrame()
        col_val_elo = 'elo'
        
    try:
        df_manuales = pd.read_csv('partidos_manuales.csv')
        equipos_clasificados = pd.concat([df_manuales['local'], df_manuales['visita']]).unique()
    except FileNotFoundError:
        equipos_clasificados = mh.dict_fa.keys()
    
    for equipo in mh.dict_fa.keys():
        if equipo not in equipos_clasificados:
            continue
        try:
            partidos_jugados = stats_df.loc[equipo, 'partidos']
        except KeyError:
            partidos_jugados = 0
            
        if partidos_jugados < 10:
            continue
            
        # 2. EL ANCLA (Jerarquía ELO - Escala base 0 a 100)
        if not df_elo.empty and equipo in df_elo.index:
            val = df_elo.loc[equipo, col_val_elo]
            elo_actual = float(val.iloc[0]) if isinstance(val, pd.Series) else float(val)
        else:
            elo_actual = 1500
            
        # Convertimos el ELO (ej. 1000 - 2000) a una escala manejable de 10 a 110 puntos
        base_elo = (elo_actual - 900) / 10.0 
        
        # 3. LA CALIDAD DE PLANTILLA (Ratings de jugadores extraídos de FIFA)
        atq = mh.dict_plantilla_atq.get(equipo, 50.0)
        dfn = mh.dict_plantilla_def.get(equipo, 50.0)
        calidad_plantilla = (atq + dfn) / 2.0
        
        # 4. EL FRENO DE GOLEADAS (Modificador Poisson estrictamente controlado)
        fa_crudo = mh.dict_fa.get(equipo, 1.0)
        fd_crudo = mh.dict_fd.get(equipo, 1.0)
        
        # Relación de dominio (maximizamos FD a 0.5 para jamás dividir entre cero)
        ratio_forma = fa_crudo / max(fd_crudo, 0.5)
        
        # Mapeamos el ratio a un multiplicador estricto (de 0.85x a 1.15x)
        # Un 5-0 contra Irak solo te dará un +15% extra como máximo, no multiplicará tu puntaje
        multiplicador_momento = 1.0 + (min(max(ratio_forma, 0.5), 2.5) - 1.0) * 0.1
        
        # 5. CÁLCULO FINAL ESTRUCTURADO
        # 75% del peso es la jerarquía ELO histórica
        # 25% del peso es la calidad en cancha
        # Todo se multiplica por el momento actual para dar el toque final
        true_power_index = ((base_elo * 0.75) + (calidad_plantilla * 0.25)) * multiplicador_momento
        
        ranking.append({'Equipo': equipo, 'Power Index': round(true_power_index, 2)})
        
    df_ranking = pd.DataFrame(ranking).sort_values(by='Power Index', ascending=False).head(5)
    df_ranking.reset_index(drop=True, inplace=True)
    df_ranking.index += 1
    return df_ranking

# ==========================================
# 3.5 FUNCIONES AUXILIARES DE ESTADÍSTICAS (ÚNICAS Y GLOBALES)
# ==========================================
def obtener_historial_reciente(equipo, limite=10):
    try:
        df_historico = pd.read_csv('historial_selecciones_combinado.csv')
        try:
            df_manual = pd.read_csv('partidos_manuales.csv')
            df_combinado = pd.concat([df_historico, df_manual], ignore_index=True)
        except FileNotFoundError:
            df_combinado = df_historico
            
        df_combinado.columns = df_combinado.columns.str.strip().str.lower()
        col_local = [c for c in df_combinado.columns if 'local' in c or 'home' in c][0]
        col_visita = [c for c in df_combinado.columns if 'visit' in c or 'away' in c][0]
        col_g_loc = [c for c in df_combinado.columns if 'goles_local' in c or 'score' in c or 'goles_l' in c][0]
        col_g_vis = [c for c in df_combinado.columns if 'goles_visita' in c or 'score' in c or 'goles_v' in c][0]
        
        mapeo_naciones = {
            'Cape Verde': 'Cabo Verde', 'Cape Verde Islands': 'Cabo Verde', 
            'United States': 'USA', 'Korea Republic': 'South Korea', 
            'Korea DPR': 'North Korea', "Côte d'Ivoire": 'Ivory Coast', 
            'Czech Republic': 'Czechia', 'Turkey': 'Türkiye', 
            'IR Iran': 'Iran', 'Republic of Ireland': 'Ireland',
            'Bosnia-Herzegovina': 'Bosnia and Herzegovina'
        }
        
        df_combinado[col_local] = df_combinado[col_local].astype(str).str.strip().replace(mapeo_naciones)
        df_combinado[col_visita] = df_combinado[col_visita].astype(str).str.strip().replace(mapeo_naciones)
        
        partidos_equipo = df_combinado[(df_combinado[col_local] == equipo) | (df_combinado[col_visita] == equipo)].copy()
        
        def escudrinar_fecha(fila):
            for valor in fila.values:
                match_full = re.search(r'\d{4}[-/]\d{2}[-/]\d{2}', str(valor))
                if match_full: return match_full.group(0)
            for valor in fila.values:
                match_year = re.search(r'\b(19|20)\d{2}\b', str(valor))
                if match_year: return match_year.group(0)
            return '1900'
        
        partidos_equipo['fecha_exacta'] = partidos_equipo.apply(escudrinar_fecha, axis=1)
        partidos_equipo = partidos_equipo.sort_values(by='fecha_exacta', ascending=True)
        ultimos = partidos_equipo.tail(limite).iloc[::-1]
        
        resultados = []
        for _, p in ultimos.iterrows():
            es_local = (p[col_local] == equipo)
            rival = p[col_visita] if es_local else p[col_local]
            gf = int(p[col_g_loc] if es_local else p[col_g_vis])
            gc = int(p[col_g_vis] if es_local else p[col_g_loc])
            
            if gf > gc: res = f"{icon('check', 18)} <span style='color:#a4e67d; font-weight:bold;'>Victoria</span>"
            elif gf < gc: res = f"{icon('cross', 18)} <span style='color:#ff8a8a; font-weight:bold;'>Derrota</span>"
            else: res = f"{icon('empate', 18)} <span style='color:#cdeaf8; font-weight:bold;'>Empate</span>"
            
            fecha_str = p['fecha_exacta']
            if fecha_str == '1900': fecha_str = "N/D"
            resultados.append(f"<div style='margin-bottom: 5px; font-size: 0.95rem;'>{icon('calendar', 16)} <span style='color:#8ebce3;'>{fecha_str}</span> | {res} vs <b>{rival}</b> ({gf} - {gc})</div>")
            
        if not resultados:
            return ["Aún no hay historial registrado."]
        return resultados
    except Exception as e:
        return [f"Error al cargar historial: {e}"]

def obtener_top_jugadores(equipo, top=3):
    # 1. El normalizador ahora es el cadenero principal
    def normalizar_texto(t):
        reemplazos = {'á':'a', 'é':'e', 'í':'i', 'ó':'o', 'ú':'u', 'ñ':'n', 'ç':'c'}
        t = str(t).strip().lower()
        for a, b in reemplazos.items(): t = t.replace(a, b)
        
        if 'dr congo' in t or 'congo dr' in t: return 'congo dr'
        if 'curaçao' in t or 'curacao' in t: return 'curacao'
        return t

    try:
        df_jugadores = pd.read_csv('rendimiento_jugadores.csv')
        df_jugadores.columns = df_jugadores.columns.str.strip().str.lower()
        
        col_eq = [c for c in df_jugadores.columns if 'equip' in c or 'team' in c][0]
        col_nom = [c for c in df_jugadores.columns if 'nom' in c or 'jug' in c or 'play' in c][0]
        col_pos = [c for c in df_jugadores.columns if 'pos' in c][0]
        col_rat_atq = [c for c in df_jugadores.columns if 'ataque' in c or 'atq' in c][0]
        col_rat_def = [c for c in df_jugadores.columns if 'defensa' in c or 'def' in c][0]
        
        # 2. Limpiamos el nombre del equipo y toda la columna del CSV antes de buscar
        equipo_norm = normalizar_texto(equipo)
        df_jugadores['equipo_limpio'] = df_jugadores[col_eq].apply(normalizar_texto)
        
        # 3. Búsqueda infalible (curacao == curacao)
        plantilla = df_jugadores[df_jugadores['equipo_limpio'] == equipo_norm].copy()
        
        if plantilla.empty:
            return [f"Sin datos registrados para {equipo}"]

        # --- FILTRO 100% AUTOMÁTICO DE LA FIFA ---
        try:
            df_oficial = pd.read_csv('convocados_oficiales.csv')
            df_oficial['Equipo_Norm'] = df_oficial['Equipo'].apply(normalizar_texto)
            plantilla_oficial = df_oficial[df_oficial['Equipo_Norm'] == equipo_norm]
            
            if not plantilla_oficial.empty:
                nombres_oficiales = [normalizar_texto(n) for n in plantilla_oficial['Jugador_Oficial'].tolist()]
                
                def es_convocado(nombre_db):
                    nom_db_limpio = normalizar_texto(nombre_db)
                    for nom_oficial in nombres_oficiales:
                        if re.search(rf'\b{re.escape(nom_oficial)}\b', nom_db_limpio): return True
                    return False
                
                plantilla_filtrada = plantilla[plantilla[col_nom].apply(es_convocado)]
                
                if not plantilla_filtrada.empty:
                    plantilla = plantilla_filtrada
                else:
                    return [f"<div style='color:#ff8a8a; font-size:0.9rem;'>{icon('cross', 16)} No se encontraron convocados oficiales para {equipo} en la BD.</div>"]
            else:
                return [f"<div style='color:#ff8a8a; font-size:0.9rem;'>{icon('cross', 16)} {equipo} no aparece en el PDF oficial de la FIFA.</div>"]
                
        except FileNotFoundError:
            return ["⚠️ Error: Archivo 'convocados_oficiales.csv' no encontrado."]
        # -------------------------------------------
        
        def calcular_rating_real(fila):
            pos = str(fila[col_pos]).upper()
            atq = pd.to_numeric(fila[col_rat_atq], errors='coerce')
            dfn = pd.to_numeric(fila[col_rat_def], errors='coerce')
            if pos == 'DEL': return atq
            elif pos in ['DEF', 'POR']: return dfn
            else: return (atq + dfn) / 2
        
        plantilla['rating_real'] = plantilla.apply(calcular_rating_real, axis=1).fillna(0)
        plantilla = plantilla.sort_values(by='rating_real', ascending=False).head(top)
        
        top_str = []
        for _, j in plantilla.iterrows():
            rating_final = int(j['rating_real'])
            color_rat = "#a4e67d" if rating_final >= 70 else "#ff8a8a"
            top_str.append(f"<div style='margin-bottom: 4px; font-size: 1rem;'>{icon('star', 20)} {j[col_nom]} ({j[col_pos]}): <b style='color:{color_rat};'>{rating_final}</b></div>")
        return top_str
    except Exception as e:
        return [f"Error leyendo jugadores: {str(e)[:40]}"]

# ==========================================
# 4. MAQUETACIÓN PRINCIPAL
# ==========================================
col_principal, col_ranking = st.columns([2, 1])

with col_ranking:
    st.markdown("<div class='frutiger-card'>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: white; margin-bottom: 5px;'>{icon('trophy', 32)} Power Ranking Top 5</h3>", unsafe_allow_html=True)
    st.caption("Algoritmo híbrido FA/FD con suavizado de Laplace")
    df_ranking = calcular_power_ranking()
    
    df_ranking_visual = df_ranking.copy()
    df_ranking_visual['Equipo'] = df_ranking_visual['Equipo'].apply(lambda x: f"{obtener_bandera(x)} {x}")
    st.dataframe(df_ranking_visual, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_principal:
    tab1, tab2, tab3, tab4 = st.tabs(["Simulador Aero", "Partidos Recientes", "Próxima Jornada", "Fase Final"])

    # --- PESTAÑA 1: SIMULADOR MANUAL ---
    with tab1:
        st.markdown("<div class='frutiger-card'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color: white; margin-bottom: 20px;'>{icon('simulador', 32)} Simulador de Enfrentamientos Directos</h3>", unsafe_allow_html=True)
        equipos = sorted(list(mh.dict_fa.keys()))
        
        c1, c2 = st.columns(2)
        with c1:
            idx_local = equipos.index('Scotland') if 'Scotland' in equipos else 0
            local = st.selectbox("Equipo Local:", equipos, index=idx_local)
        with c2:
            idx_visita = equipos.index('Morocco') if 'Morocco' in equipos else 1
            visitante = st.selectbox("Equipo Visitante:", equipos, index=idx_visita)
            
        if st.button("CALCULAR PREDICCIÓN AI", width='stretch'):
            # 1. ACTUALIZADO: Ahora recibe 7 variables en lugar de 4
            xg_l, xg_v, paquete_probs, top_marcadores, hay_alargue, p_pen_l, p_pen_v = mh.predecir_partido(local, visitante)
            probs_flat = np.array(paquete_probs).flatten()
            
            p_visita = float(probs_flat[0]) 
            p_empate = float(probs_flat[1])
            p_local = float(probs_flat[2])
            
            st.markdown(f"<div style='background-color: #2e4a23; padding: 10px; border-radius: 5px; border: 1px solid #a4e67d; color: white;'>{icon('robot', 20)} <b>Cómputo Neuronal Exitoso</b></div>", unsafe_allow_html=True)
            
            bandera_l = obtener_bandera(local)
            bandera_v = obtener_bandera(visitante)
            
            st.markdown(f"""
            <div style='background: rgba(0,0,0,0.3); box-shadow: inset 0 3px 8px rgba(0,0,0,0.5); padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); margin: 15px 0; text-align: center;'>
                <div style='font-size: 2.2rem; margin-bottom: 5px;'>
                    {bandera_l} <span style='font-weight: 800; color: #fff;'>{local}</span> 
                    <span style='color: #a4e67d;'>vs</span> 
                    <span style='font-weight: 800; color: #fff;'>{visitante}</span> {bandera_v}
                </div>
                <div style='font-size: 1.3rem; color: #8ebce3; font-weight: 600; font-family: Tahoma;'>
                    xG Estimado: {float(xg_l):.2f} - {float(xg_v):.2f}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"<p style='margin-bottom: 5px;'><b>Probabilidad Gana {local} {bandera_l}: {p_local*100:.1f}%</b></p>", unsafe_allow_html=True)
            st.progress(p_local)
            
            st.markdown(f"<p style='margin-bottom: 5px; margin-top: 10px;'>{icon('handshake', 20)} <b>Probabilidad de Empate: {p_empate*100:.1f}%</b></p>", unsafe_allow_html=True)
            st.progress(p_empate)
            
            st.markdown(f"<p style='margin-bottom: 5px; margin-top: 10px;'><b>Probabilidad Gana {visitante} {bandera_v}: {p_visita*100:.1f}%</b></p>", unsafe_allow_html=True)
            st.progress(p_visita)
            
            # 2. NUEVO: ALERTA DE PENALES
            if hay_alargue:
                st.markdown(f"""
                <div style='background: rgba(255, 138, 138, 0.15); border-left: 4px solid #ff8a8a; padding: 12px; border-radius: 4px; margin-top: 15px; box-shadow: inset 0 1px 3px rgba(0,0,0,0.5);'>
                    <b style='color: #ff8a8a; font-size: 1.05rem;'>⚠️ Alta Probabilidad de Prórroga / Penales</b><br>
                    <span style='font-size: 0.95rem; color: #f8fafc;'>
                        Probabilidad calculada en tanda de penales (Vía ELO):<br>
                        <b>{local}:</b> <span style='color: #a4e67d;'>{p_pen_l*100:.1f}%</span> | <b>{visitante}:</b> <span style='color: #a4e67d;'>{p_pen_v*100:.1f}%</span>
                    </span>
                </div>
                """, unsafe_allow_html=True)
                
            st.divider()

# --- NUEVO: TOP 10 MARCADORES ---
            with st.expander("🎯 Ver Top 10 Marcadores Más Probables"):
                col1, col2 = st.columns(2)
                for i, resultado in enumerate(top_marcadores):
                    marcador = resultado['marcador']
                    prob = resultado['probabilidad']
                    
                    # Top 3 con brillo especial Aero
                    if i < 3:
                        html_marcador = f"<div style='font-size: 1.1rem; margin-bottom: 5px;'><b>#{i+1}</b> | <b>{marcador}</b> ➔ <span style='color: #a4e67d;'>{prob:.1f}%</span></div>"
                    else:
                        html_marcador = f"<div style='font-size: 0.95rem; margin-bottom: 5px; color: #8ebce3;'>#{i+1} | {marcador} ➔ {prob:.1f}%</div>"
                        
                    if i < 5:
                        col1.markdown(html_marcador, unsafe_allow_html=True)
                    else:
                        col2.markdown(html_marcador, unsafe_allow_html=True)
            # --------------------------------

            st.markdown(f"<h5 style='color:white;'>{icon('search', 24)} Justificación Estadística en Vivo</h5>", unsafe_allow_html=True)
            col_info_l, col_info_v = st.columns(2)
            
            with col_info_l:
                st.markdown(f"<strong style='font-size: 1.1rem; color: #ffffff;'>{bandera_l} Estado de {local}</strong>", unsafe_allow_html=True)
                st.markdown(f"<p style='color: #8ebce3; margin-top:10px; margin-bottom:5px; font-weight:bold;'>{icon('trophy', 16)} MVPs del Torneo:</p>", unsafe_allow_html=True)
                for j in obtener_top_jugadores(local): st.write(j, unsafe_allow_html=True)
                st.write("") 
                st.markdown(f"<p style='color: #8ebce3; margin-top:10px; margin-bottom:5px; font-weight:bold;'>{icon('chart', 16)} Últimos 10 Partidos:</p>", unsafe_allow_html=True)
                for h in obtener_historial_reciente(local): st.write(h, unsafe_allow_html=True)

            with col_info_v:
                st.markdown(f"<strong style='font-size: 1.1rem; color: #ffffff;'>{bandera_v} Estado de {visitante}</strong>", unsafe_allow_html=True)
                st.markdown(f"<p style='color: #8ebce3; margin-top:10px; margin-bottom:5px; font-weight:bold;'>{icon('trophy', 16)} MVPs del Torneo:</p>", unsafe_allow_html=True)
                for j in obtener_top_jugadores(visitante): st.write(j, unsafe_allow_html=True)
                st.write("") 
                st.markdown(f"<p style='color: #8ebce3; margin-top:10px; margin-bottom:5px; font-weight:bold;'>{icon('chart', 16)} Últimos 10 Partidos:</p>", unsafe_allow_html=True)
                for h in obtener_historial_reciente(visitante): st.write(h, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- PESTAÑA 2: RESULTADOS RECIENTES ---
    with tab2:
        st.markdown("<div class='frutiger-card'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color: white; margin-bottom: 20px;'>{icon('historial', 32)} Historial de Partidos (Control Manual)</h3>", unsafe_allow_html=True)
        try:
            df_partidos = pd.read_csv('partidos_manuales.csv')
            df_recientes = df_partidos.iloc[::-1]
            for _, row in df_recientes.iterrows():
                loc = row['local']
                vis = row['visita']
                gl = row['goles_local']
                gv = row['goles_visita']
                
                # Leemos los penales usando .get() para evitar errores si la columna viene vacía
                pl = row.get('penales_local', 0)
                pv = row.get('penales_visita', 0)
                
                # Formateamos el marcador: Si hubo penales mayores a 0, ponemos los paréntesis
                if pd.notna(pl) and pd.notna(pv) and (pl > 0 or pv > 0):
                    marcador_texto = f"{int(gl)} ({int(pl)}) - {int(gv)} ({int(pv)})"
                else:
                    marcador_texto = f"{int(gl)} - {int(gv)}"

                st.markdown(f"""
                <div class='match-row'>
                    <div class='team-box'>{obtener_bandera(loc)} {loc}</div>
                    <div class='score-box'>{marcador_texto}</div>
                    <div class='team-box' style='justify-content: flex-end;'>{vis} {obtener_bandera(vis)}</div>
                </div>
                """, unsafe_allow_html=True)
        except FileNotFoundError:
            st.warning("Aún no hay registros en 'partidos_manuales.csv'.")
        except KeyError:
            st.error("Error leyendo las columnas del CSV.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    # --- PESTAÑA 3: PRÓXIMA JORNADA ---
    with tab3:
        st.markdown("<div class='frutiger-card'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color: white; margin-bottom: 5px;'>{icon('calendar', 32)} Predicciones automáticas para Mañana</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #aedef7; font-size: 0.9rem; margin-bottom: 20px;'>Análisis avanzado y contexto histórico de los contendientes.</p>", unsafe_allow_html=True)
        
        partidos_manana = [
            ('Spain', 'Austria'),
            ('Portugal', 'Croatia'),
            ('Switzerland', 'Argelia')
        ]
        
        # ELIMINAMOS LAS FUNCIONES DUPLICADAS AQUÍ ADENTRO. AHORA USA LAS DE ARRIBA.
        
        # --- RENDERIZADO DE PARTIDOS ---
        for eq_l, eq_v in partidos_manana:
            # Quitamos la restricción de que deban existir en 'equipos' por si no tienen partidos previos
            b_l = obtener_bandera(eq_l)
            b_v = obtener_bandera(eq_v)
            
            with st.expander(f"🏟️ {b_l} {eq_l} vs {eq_v} {b_v}"):
                # 1. ACTUALIZADO: Ahora recibe 7 variables
                xg_l, xg_v, paquete_probs, top_marcadores, hay_alargue, p_pen_l, p_pen_v = mh.predecir_partido(eq_l, eq_v) 
                probs_flat = np.array(paquete_probs).flatten()
                
                p_v = float(probs_flat[0])
                p_e = float(probs_flat[1])
                p_l = float(probs_flat[2])
                
                st.markdown(f"""
                <div style='text-align: center; margin-bottom: 15px; font-family: Tahoma; font-size: 1.1rem; color: #a4e67d; text-shadow: 1px 1px 2px black;'>
                    <b>xG Esperado de Poisson:</b> {float(xg_l):.2f} - {float(xg_v):.2f}
                </div>
                """, unsafe_allow_html=True)
                
                m1, m2, m3 = st.columns(3)
                m1.metric(label=f"Gana {eq_l} {b_l}", value=f"{p_l*100:.1f}%")
                m2.metric(label="Empate 🤝", value=f"{p_e*100:.1f}%")
                m3.metric(label=f"Gana {eq_v} {b_v}", value=f"{p_v*100:.1f}%")
                
                # 2. NUEVO: ALERTA DE PENALES
                if hay_alargue:
                    st.markdown(f"""
                    <div style='background: rgba(255, 138, 138, 0.15); border-left: 4px solid #ff8a8a; padding: 10px; border-radius: 4px; margin-top: 10px;'>
                        <b style='color: #ff8a8a;'>⚠️ Alta Probabilidad de Prórroga / Penales</b><br>
                        <span style='font-size: 0.9rem; color: #e2e2e2;'>
                            <b>{eq_l}:</b> {p_pen_l*100:.1f}% | <b>{eq_v}:</b> {p_pen_v*100:.1f}%
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                st.divider()

# --- NUEVO: TOP 10 MARCADORES PARA JORNADAS AUTOMÁTICAS ---
                st.write("") # Espacio
                with st.expander("🎯 Ver Top 10 Marcadores Más Probables"):
                    col1, col2 = st.columns(2)
                    for i, resultado in enumerate(top_marcadores):
                        marcador = resultado['marcador']
                        prob = resultado['probabilidad']
                        
                        if i < 3:
                            html_marcador = f"<div style='font-size: 1.05rem; margin-bottom: 5px;'><b>#{i+1}</b> | <b>{marcador}</b> ➔ <span style='color: #a4e67d;'>{prob:.1f}%</span></div>"
                        else:
                            html_marcador = f"<div style='font-size: 0.9rem; margin-bottom: 5px; color: #8ebce3;'>#{i+1} | {marcador} ➔ {prob:.1f}%</div>"
                            
                        if i < 5:
                            col1.markdown(html_marcador, unsafe_allow_html=True)
                        else:
                            col2.markdown(html_marcador, unsafe_allow_html=True)
                # ----------------------------------------------------------

                st.markdown(f"<h5 style='color:white;'>{icon('search', 24)} Justificación Estadística en Vivo</h5>", unsafe_allow_html=True)
                
                col_info_l, col_info_v = st.columns(2)
                
                with col_info_l:
                    st.markdown(f"<strong style='font-size: 1.1rem; color: #ffffff;'>{b_l} Estado de {eq_l}</strong>", unsafe_allow_html=True)
                    st.markdown(f"<p style='color: #8ebce3; margin-top:10px; margin-bottom:5px; font-weight:bold;'>{icon('trophy', 16)} MVPs del Torneo:</p>", unsafe_allow_html=True)
                    for j in obtener_top_jugadores(eq_l):
                        st.write(j, unsafe_allow_html=True)
                    st.write("") 
                    st.markdown(f"<p style='color: #8ebce3; margin-top:10px; margin-bottom:5px; font-weight:bold;'>{icon('chart', 16)} Últimos 10 Partidos:</p>", unsafe_allow_html=True)
                    for h in obtener_historial_reciente(eq_l):
                        st.write(h, unsafe_allow_html=True)

                with col_info_v:
                    st.markdown(f"<strong style='font-size: 1.1rem; color: #ffffff;'>{b_v} Estado de {eq_v}</strong>", unsafe_allow_html=True)
                    st.markdown(f"<p style='color: #8ebce3; margin-top:10px; margin-bottom:5px; font-weight:bold;'>{icon('trophy', 16)} MVPs del Torneo:</p>", unsafe_allow_html=True)
                    for j in obtener_top_jugadores(eq_v):
                        st.write(j, unsafe_allow_html=True)
                    st.write("") 
                    st.markdown(f"<p style='color: #8ebce3; margin-top:10px; margin-bottom:5px; font-weight:bold;'>{icon('chart', 16)} Últimos 10 Partidos:</p>", unsafe_allow_html=True)
                    for h in obtener_historial_reciente(eq_v):
                        st.write(h, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

# --- PESTAÑA 4: BRACKET DE ELIMINATORIAS COMPLETO (32 EQUIPOS) ---
    with tab4:
        st.markdown(f"<h3 style='color: white; margin-bottom: 10px;'>{icon('trophy', 32)} Cuadro de Eliminatorias (Fase Final)</h3>", unsafe_allow_html=True)
        
        st.markdown("""
        <style>
            .bracket-wrapper { width: 100%; overflow-x: auto; padding-bottom: 20px; }
            .bracket-container { display: flex; justify-content: space-between; align-items: stretch; min-width: 1300px; min-height: 850px; padding: 10px 0; font-family: Tahoma, sans-serif; }
            .bracket-col { display: flex; flex-direction: column; justify-content: space-around; flex: 1; padding: 0 4px; }
            .bracket-center { display: flex; flex-direction: column; justify-content: center; align-items: center; flex: 1.2; padding: 0 10px; }
            .b-match { background: rgba(0, 0, 0, 0.45); border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 6px; padding: 6px 8px; margin: 2px 0; box-shadow: inset 0 2px 5px rgba(0,0,0,0.5), 0 4px 6px rgba(0,0,0,0.3); }
            .b-team { display: flex; justify-content: space-between; align-items: center; margin: 3px 0; font-size: 0.85rem; white-space: nowrap; }
            .b-score { background: linear-gradient(to bottom, #2098d3, #0570b0); padding: 2px 6px; border-radius: 4px; border: 1px solid #002244; font-weight: bold; font-size: 0.8rem; box-shadow: inset 0 1px 1px rgba(255,255,255,0.4); margin-left: 5px; }
            .win-text { color: #ffffff; font-weight: bold; text-shadow: 0 0 5px rgba(255,255,255,0.3); }
            .lose-text { color: #888888; }
            .pend-text { color: #cccccc; }
            .score-win { color: #a4e67d; }
            .score-pend { color: #8ebce3; background: #333333; }
        </style>
        """, unsafe_allow_html=True)

# NUEVA FUNCIÓN RENDER CAJA (Soporta penales)
        def render_caja(eq1, eq2, g1=0, g2=0, p1=None, p2=None, estado="Pendiente", etiqueta=""):
            b1, b2 = obtener_bandera(eq1) if eq1 != "TBD" else "❔", obtener_bandera(eq2) if eq2 != "TBD" else "❔"
            
            if estado == "Finalizado":
                # Si hubo penales, decidimos al ganador por los penales
                if p1 is not None and p2 is not None:
                    c1 = "win-text" if p1 > p2 else "lose-text"
                    c2 = "win-text" if p2 > p1 else "lose-text"
                    score_text = f"{g1}({p1}) - {g2}({p2})"
                else: # Si ganaron en 90 mins
                    c1 = "win-text" if g1 > g2 else "lose-text"
                    c2 = "win-text" if g2 > g1 else "lose-text"
                    score_text = f"{g1} - {g2}"
                score_class = "score-win"
            else:
                c1 = c2 = "pend-text"
                score_class = "score-pend"
                score_text = "vs"

            header = f"<div style='text-align: center; font-size: 0.7rem; color: #8ebce3; margin-bottom: 2px;'>{etiqueta}</div>" if etiqueta else ""
            return f"<div class='b-match'>{header}<div class='b-team'><span class='{c1}'>{b1} {eq1}</span> <span class='b-score {score_class}'>{score_text}</span></div><div class='b-team'><span class='{c2}'>{b2} {eq2}</span></div></div>"

# ACTUALIZACIÓN DE DIECISEISAVOS Y OCTAVOS (Izquierda)
        r32_izq = [
            render_caja('Germany', 'Paraguay', 1, 1, 3, 4, 'Finalizado'),
            render_caja('France', 'Sweden', 3, 0, None, None, 'Finalizado'),
            render_caja('South Africa', 'Canada', 0, 1, None, None, 'Finalizado'),
            render_caja('Netherlands', 'Morocco', 1, 1, 2, 3, 'Finalizado'),
            render_caja('Portugal', 'Croatia'), render_caja('Spain', 'Austria'),
            render_caja('USA', 'Bosnia and Herzegovina', 2, 0, None, None, 'Finalizado'), render_caja('Belgium', 'Senegal', 3, 2, None, None, 'Finalizado') # ¡USA Avanza!
        ]

        # 16vos Derecha (R32) (Ovo ostaje isto, ali ga ostavi radi poravnanja)
        r32_der = [
            render_caja('Brazil', 'Japan', 2, 1, None, None, 'Finalizado'), render_caja('Ivory Coast', 'Norway', 1, 2, None, None, 'Finalizado'),
            render_caja('Mexico', 'Ecuador', 2, 0, None, None, 'Finalizado'), render_caja('England', 'DR Congo', 2, 1, None, None, 'Finalizado'),
            render_caja('Argentina', 'Cabo Verde'), render_caja('Australia', 'Egypt'),
            render_caja('Switzerland', 'Algeria'), render_caja('Colombia', 'Ghana')
        ]

        # Octavos Izquierda (R16)
        r16_izq = [
            render_caja('Paraguay', 'France', etiqueta="Octavos 1"),
            render_caja('Canada', 'Morocco', etiqueta="Octavos 2"),
            render_caja('TBD', 'TBD', etiqueta="Octavos 3"),
            render_caja('USA', 'Belgium', etiqueta="Octavos 4") # ¡Se armó el USA vs Belgium!
        ]

        # Octavos Derecha (R16)
        r16_der = [
            render_caja('Brazil', 'Norway', etiqueta="Octavos 5"),
            render_caja('Mexico', 'England', etiqueta="Octavos 6"),
            render_caja('TBD', 'TBD', etiqueta="Octavos 7"),
            render_caja('TBD', 'TBD', etiqueta="Octavos 8")
        ]

        # Cuartos Izquierda (QF)
        qf_izq = [render_caja('TBD', 'TBD', etiqueta="Cuartos 1"), render_caja('TBD', 'TBD', etiqueta="Cuartos 2")]

        # Cuartos Derecha (QF)
        qf_der = [render_caja('TBD', 'TBD', etiqueta="Cuartos 3"), render_caja('TBD', 'TBD', etiqueta="Cuartos 4")]

        # Semis Izquierda/Derecha (SF)
        sf_izq = [render_caja('TBD', 'TBD', etiqueta="Semifinal 1")]
        sf_der = [render_caja('TBD', 'TBD', etiqueta="Semifinal 2")]

        # Final (Centro)
        final = render_caja('TBD', 'TBD', etiqueta="🏆 GRAN FINAL")

        # CONTENEDOR FLEXBOX COMPRIMIDO CON TODAS LAS FASES
        html_bracket = f"<div class='bracket-wrapper'><div class='bracket-container'><div class='bracket-col'>{''.join(r32_izq)}</div><div class='bracket-col' style='padding: 20px 2px;'>{''.join(r16_izq)}</div><div class='bracket-col' style='padding: 80px 2px;'>{''.join(qf_izq)}</div><div class='bracket-col' style='padding: 180px 2px;'>{''.join(sf_izq)}</div><div class='bracket-center'><img src='https://img.icons8.com/3d-fluency/96/trophy.png' width='80' style='margin-bottom: 20px;'>{final}</div><div class='bracket-col' style='padding: 180px 2px;'>{''.join(sf_der)}</div><div class='bracket-col' style='padding: 80px 2px;'>{''.join(qf_der)}</div><div class='bracket-col' style='padding: 20px 2px;'>{''.join(r16_der)}</div><div class='bracket-col'>{''.join(r32_der)}</div></div></div>"
        
        st.markdown(html_bracket, unsafe_allow_html=True)

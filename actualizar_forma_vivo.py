import pandas as pd
import re

try:
    df = pd.read_csv('rendimiento_jugadores.csv')
except FileNotFoundError:
    print("Error: No se encontró 'rendimiento_jugadores.csv'.")
    exit()

calificaciones_mundial = [
    # --- URUGUAY (Empate 2-2) ---
    ('Uruguay', 'Muslera', 5.2, 'POR'),
    ('Uruguay', 'Varela', 6.4, 'DEF'),
    ('Uruguay', 'Cáceres', 7.4, 'DEF'),
    ('Uruguay', 'Olivera', 6.2, 'DEF'),
    ('Uruguay', 'Sanabria', 6.2, 'MED'),
    ('Uruguay', 'Ugarte', 6.6, 'MED'),
    ('Uruguay', 'Bentancur', 6.4, 'MED'),
    ('Uruguay', 'Valverde', 6.3, 'MED'),
    ('Uruguay', 'Canobbio', 7.5, 'DEL'),
    ('Uruguay', 'Araújo', 7.4, 'DEL'),
    ('Uruguay', 'Viñas', 6.5, 'DEL'),

    # --- CABO VERDE (Empate 2-2) ---
    ('Cabo Verde', 'Vozinha', 4.5, 'POR'),
    ('Cabo Verde', 'Moreira', 5.7, 'DEF'),
    ('Cabo Verde', 'R. Lopes', 7.6, 'DEF'),
    ('Cabo Verde', 'Diney', 5.9, 'DEF'),
    ('Cabo Verde', 'S. Lopes Cabral', 6.0, 'DEF'),
    ('Cabo Verde', 'K. Pina', 7.5, 'MED'),
    ('Cabo Verde', 'T. Arcanjo', 6.7, 'MED'),
    ('Cabo Verde', 'R. Mendes', 6.4, 'MED'),
    ('Cabo Verde', 'J. Monteiro', 6.3, 'DEL'),
    ('Cabo Verde', 'G. Rodrigues', 6.8, 'DEL'),
    ('Cabo Verde', 'G. Tavares', 6.2, 'DEL'),

    # --- NEW ZEALAND (Derrota 1-3) ---
    ('New Zealand', 'Crocombe', 4.7, 'POR'),
    ('New Zealand', 'Payne', 5.8, 'DEF'),
    ('New Zealand', 'Surman', 6.7, 'DEF'),
    ('New Zealand', 'Boxall', 5.5, 'DEF'),
    ('New Zealand', 'Cacace', 6.1, 'DEF'),
    ('New Zealand', 'Singh', 4.7, 'MED'),
    ('New Zealand', 'Bell', 5.4, 'MED'),
    ('New Zealand', 'Stamenić', 6.4, 'MED'),
    ('New Zealand', 'Just', 6.0, 'DEL'),
    ('New Zealand', 'Wood', 5.6, 'DEL'),
    ('New Zealand', 'McCowatt', 5.4, 'DEL'),

    # --- EGYPT (Victoria 3-1) ---
    ('Egypt', 'Shobeir', 7.2, 'POR'),
    ('Egypt', 'Hany', 7.3, 'DEF'),
    ('Egypt', 'Y. Ibrahim', 6.9, 'DEF'),
    ('Egypt', 'H. Fathy', 6.6, 'DEF'),
    ('Egypt', 'Fotouh', 7.2, 'DEF'),
    ('Egypt', 'Attia', 6.2, 'MED'),
    ('Egypt', 'Lasheen', 7.3, 'MED'),
    ('Egypt', 'Ashour', 6.2, 'MED'),
    ('Egypt', 'Marmoush', 6.3, 'DEL'),
    ('Egypt', 'Ziko', 7.2, 'DEL'),
    ('Egypt', 'Salah', 7.8, 'DEL')
]

print("Inyectando métricas con asignación dinámica de posición...")
actualizados = 0
nuevos = 0

# Ahora desempacamos 4 variables en el ciclo
for equipo, apellido, calificacion_pdf, posicion_real in calificaciones_mundial:
    nuevo_rating = int(calificacion_pdf * 10)
    
    patron = rf"\b{apellido}\b"
    filtro_nombre = df['jugador'].str.contains(patron, flags=re.IGNORECASE, regex=True, na=False)
    filtro_equipo = df['equipo'] == equipo
    filtro_combinado = filtro_nombre & filtro_equipo
    
    if df[filtro_combinado].empty:
        # === LÓGICA DE INSERCIÓN CON POSICIÓN REAL ===
        # El jugador nuevo se crea respetando su rol exacto en la cancha
        rat_atq = nuevo_rating if posicion_real in ['DEL', 'MED'] else 50
        rat_def = nuevo_rating if posicion_real in ['DEF', 'POR', 'MED'] else 50
        
        nuevo_jugador = pd.DataFrame([{
            'equipo': equipo,
            'jugador': apellido,
            'posicion': posicion_real,
            'rating_ataque': rat_atq,
            'rating_defensa': rat_def,
            'fisco': 75
        }])
        
        df = pd.concat([df, nuevo_jugador], ignore_index=True)
        print(f" [+] NUEVO CRACK ({posicion_real}): {apellido} ({equipo}) | Rating: {nuevo_rating}")
        nuevos += 1
        
    else:
        # === LÓGICA DE ACTUALIZACIÓN (CORREGIDA) ===
        for index, row in df[filtro_combinado].iterrows():
            
            # ¡EL FIX!: Forzamos a que la base de datos olvide la posición vieja 
            # y adopte la posición real de la tupla.
            df.at[index, 'posicion'] = posicion_real
            
            # Ahora calculamos los ratings basados en su posición real
            if posicion_real == 'DEL':
                df.at[index, 'rating_ataque'] = nuevo_rating
            elif posicion_real in ['DEF', 'POR']:
                df.at[index, 'rating_defensa'] = nuevo_rating
            elif posicion_real == 'MED':
                df.at[index, 'rating_ataque'] = nuevo_rating
                df.at[index, 'rating_defensa'] = nuevo_rating
                
            print(f" -> Re-calibrado: {row['jugador']} ({row['equipo']}) | Forma: {nuevo_rating} | Nueva Pos: {posicion_real}")
            actualizados += 1

df.to_csv('rendimiento_jugadores.csv', index=False, encoding='utf-8')
print(f"\n¡Listo! Sincronización terminada. {actualizados} actualizaciones y {nuevos} inserciones limpias.")
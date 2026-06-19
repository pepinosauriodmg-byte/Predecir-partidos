import pandas as pd
import re

try:
    df = pd.read_csv('rendimiento_jugadores.csv')
except FileNotFoundError:
    print("Error: No se encontró 'rendimiento_jugadores.csv'.")
    exit()

# MATRIZ DE ALTA RESOLUCIÓN: (País, Apellido, Calificación)
calificaciones_mundial = [
    # --- MÉXICO VS SUDÁFRICA ---
    ('Mexico', 'Rangel', 6.9), ('Mexico', 'Montes', 5.6), ('Mexico', 'Vásquez', 6.5), ('Mexico', 'Lira', 6.7), ('Mexico', 'Gallardo', 5.4), ('Mexico', 'Gutiérrez', 5.5), ('Mexico', 'Alvarado', 6.7), ('Mexico', 'Jiménez', 7.2), ('Mexico', 'Quiñones', 7.8), ('Mexico', 'Reyes', 6.6), ('Mexico', 'Fidalgo', 6.5),
    ('South Africa', 'Williams', 5.9), ('South Africa', 'Mokoena', 5.1), ('South Africa', 'Sithole', 4.5), ('South Africa', 'Adams', 5.5), ('South Africa', 'Modiba', 5.6), ('South Africa', 'Mbokazi', 5.4), ('South Africa', 'Sibisi', 4.5), ('South Africa', 'Okon', 5.1), ('South Africa', 'Mudau', 6.3),
    
    # --- COREA DEL SUR VS CHEQUIA ---
    ('South Korea', 'Lee', 6.2), ('South Korea', 'Seol', 5.2), ('South Korea', 'Hwang', 7.3), ('South Korea', 'Kim', 6.4), ('South Korea', 'Kim', 6.7), ('South Korea', 'Gi-Hyuk', 6.3), ('South Korea', 'Lee', 7.0), ('South Korea', 'Son', 5.2), ('South Korea', 'Paik', 5.2),
    ('Czechia', 'Lee', 5.8), ('Czechia', 'Schick', 5.4), ('Czechia', 'Provod', 4.9), ('Czechia', 'Zeleny', 5.0), ('Czechia', 'Sojka', 5.6), ('Czechia', 'Soucek', 5.0), ('Czechia', 'Coufal', 4.6), ('Czechia', 'Krejci', 5.0), ('Czechia', 'Hranac', 4.8), ('Czechia', 'Kovar', 5.0), ('Czechia', 'Chaloupek', 4.5),

    # --- CANADÁ VS BOSNIA ---
    ('Canada', 'Crepeau', 5.2), ('Canada', 'Johnston', 5.4), ('Canada', 'de Fougerolles', 6.5), ('Canada', 'Cornelius', 6.0), ('Canada', 'Laryea', 6.4), ('Canada', 'Buchanan', 5.2), ('Canada', 'Eustaquio', 6.1), ('Canada', 'Kone', 5.1), ('Canada', 'Millar', 5.8), ('Canada', 'David', 5.4), ('Canada', 'Oluwaseyi', 5.8),
    ('Bosnia and Herzegovina', 'Lukic', 6.3), ('Bosnia and Herzegovina', 'Demirovic', 4.8), ('Bosnia and Herzegovina', 'Memic', 4.7), ('Bosnia and Herzegovina', 'Tahirovic', 5.5), ('Bosnia and Herzegovina', 'Basic', 6.3), ('Bosnia and Herzegovina', 'Bajraktarevic', 5.4), ('Bosnia and Herzegovina', 'Kolasinac', 4.7), ('Bosnia and Herzegovina', 'Muharemovic', 6.8), ('Bosnia and Herzegovina', 'Katic', 7.0), ('Bosnia and Herzegovina', 'Dedic', 6.2), ('Bosnia and Herzegovina', 'Vasilj', 4.5),

    # --- USA VS PARAGUAY ---
    ('USA', 'Freese', 6.1), ('USA', 'Freeman', 7.2), ('USA', 'Richards', 7.5), ('USA', 'Ream', 7.6), ('USA', 'Adams', 7.6), ('USA', 'Robinson', 6.9), ('USA', 'Tillman', 7.6), ('USA', 'Dest', 6.5), ('USA', 'McKennie', 6.8), ('USA', 'Pulisic', 7.4), ('USA', 'Balogun', 8.7),
    ('Paraguay', 'Almiron', 6.0), ('Paraguay', 'Enciso', 6.8), ('Paraguay', 'Bobadilla', 5.9), ('Paraguay', 'Sanabria', 6.4), ('Paraguay', 'Cubas', 6.5), ('Paraguay', 'Gomez', 5.8), ('Paraguay', 'Alonso', 6.2), ('Paraguay', 'Alderete', 6.1), ('Paraguay', 'Caceres', 5.9), ('Paraguay', 'Gill', 4.5),

    # --- QATAR VS SUIZA ---
    ('Qatar', 'Abunada', 6.7), ('Qatar', 'Al-Oui', 5.2), ('Qatar', 'Miguel', 6.4), ('Qatar', 'Khoukhi', 5.8), ('Qatar', 'Ahmed', 5.2), ('Qatar', 'Gaber', 4.5), ('Qatar', 'Laye', 5.9), ('Qatar', 'Junior', 5.3), ('Qatar', 'Madibo', 5.4), ('Qatar', 'Afif', 5.8), ('Qatar', 'Abdurisag', 5.4),
    ('Switzerland', 'Ndoye', 5.9), ('Switzerland', 'Embolo', 6.9), ('Switzerland', 'Vargas', 6.9), ('Switzerland', 'Rodriguez', 6.3), ('Switzerland', 'Xhaka', 5.8), ('Switzerland', 'Freuler', 6.3), ('Switzerland', 'Aebischer', 6.4), ('Switzerland', 'Elvedi', 6.3), ('Switzerland', 'Akanji', 6.6), ('Switzerland', 'Zakaria', 5.5), ('Switzerland', 'Kobel', 6.0),

    # --- BRASIL VS MARRUECOS ---
    ('Brazil', 'Ibanez', 5.0), ('Brazil', 'Casemiro', 5.5), ('Brazil', 'Becker', 5.8), ('Brazil', 'Marquinhos', 5.9), ('Brazil', 'Magalhaes', 5.9), ('Brazil', 'Raphinha', 5.7), ('Brazil', 'Paqueta', 6.1), ('Brazil', 'Thiago', 5.6), ('Brazil', 'Santos', 6.6), ('Brazil', 'Guimaraes', 5.4), ('Brazil', 'Júnior', 5.9),
    ('Morocco', 'Saibari', 6.1), ('Morocco', 'El Khannouss', 5.8), ('Morocco', 'Ounahi', 4.9), ('Morocco', 'Diaz', 5.1), ('Morocco', 'El Aynaoui', 5.7), ('Morocco', 'Mazraoui', 5.6), ('Morocco', 'Riad', 5.7), ('Morocco', 'Bounou', 6.3), ('Morocco', 'Diop', 5.0), ('Morocco', 'Bouaddi', 5.4), ('Morocco', 'Hakimi', 6.1),

    # --- HAITÍ VS ESCOCIA ---
    ('Haiti', 'Arcus', 5.2), ('Haiti', 'Ade', 6.5), ('Haiti', 'Placide', 5.5), ('Haiti', 'Delcroix', 6.6), ('Haiti', 'Experience', 5.3), ('Haiti', 'Deedson', 5.6), ('Haiti', 'Bellegarde', 5.6), ('Haiti', 'Jean Jacques', 5.9), ('Haiti', 'Providence', 4.7), ('Haiti', 'Pierrot', 4.8),
    ('Scotland', 'McGinn', 6.3), ('Scotland', 'Isidor', 4.5), ('Scotland', 'Adams', 5.1), ('Scotland', 'Shankland', 4.9), ('Scotland', 'Ferguson', 6.4), ('Scotland', 'McTominay', 5.1), ('Scotland', 'Gannon-Doak', 5.9), ('Scotland', 'Robertson', 5.3), ('Scotland', 'Hendry', 5.5), ('Scotland', 'Hanley', 6.4), ('Scotland', 'Hickey', 5.8), ('Scotland', 'Gunn', 6.5),

    # --- AUSTRALIA VS TURQUÍA ---
    ('Australia', 'Beach', 8.4), ('Australia', 'Italiano', 5.8), ('Australia', 'Circati', 6.4), ('Australia', 'Souttar', 7.1), ('Australia', 'Burgess', 6.4), ('Australia', 'Bos', 5.4), ('Australia', 'Metcalfe', 7.2), ('Australia', 'Okon-Engstler', 6.1), ('Australia', 'O\'Neill', 6.5), ('Australia', 'Irankunda', 6.9), ('Australia', 'Toure', 5.2),
    ('Türkiye', 'Akturkoglu', 5.6), ('Türkiye', 'Yilmaz', 5.2), ('Türkiye', 'Kokcu', 5.4), ('Türkiye', 'Guler', 5.3), ('Türkiye', 'Kadioglu', 5.5), ('Türkiye', 'Yuksek', 5.8), ('Türkiye', 'Bardakci', 5.7), ('Türkiye', 'Cakir', 4.5), ('Türkiye', 'Calhanoglu', 6.1), ('Türkiye', 'Demiral', 6.4), ('Türkiye', 'Celik', 4.9),

    # --- ALEMANIA VS CURAZAO ---
    ('Germany', 'Neuer', 7.4), ('Germany', 'Kimmich', 8.7), ('Germany', 'Tah', 7.7), ('Germany', 'Schlotterbeck', 8.5), ('Germany', 'Brown', 8.8), ('Germany', 'Pavlovic', 8.1), ('Germany', 'Nmecha', 9.4), ('Germany', 'Sane', 8.0), ('Germany', 'Musiala', 8.5), ('Germany', 'Wirtz', 8.0), ('Germany', 'Havertz', 9.1),
    ('Curacao', 'Locadia', 7.4), ('Curacao', 'Bacuna', 6.8), ('Curacao', 'Comenencia', 7.6), ('Curacao', 'Hansen', 7.7), ('Curacao', 'Chong', 7.7), ('Curacao', 'Fonville', 6.2), ('Curacao', 'Obispo', 6.8), ('Curacao', 'Bazoer', 7.1), ('Curacao', 'Floranus', 7.0), ('Curacao', 'Room', 4.5),

    # --- PAÍSES BAJOS VS JAPÓN ---
    ('Netherlands', 'Dumfries', 6.0), ('Netherlands', 'Verbruggen', 4.5), ('Netherlands', 'van Hecke', 6.0), ('Netherlands', 'van Dijk', 6.6), ('Netherlands', 'Gravenberch', 6.2), ('Netherlands', 'de Jong', 6.9), ('Netherlands', 'Summerville', 7.0), ('Netherlands', 'Malen', 6.3), ('Netherlands', 'van de Ven', 5.6), ('Netherlands', 'Reijnders', 6.6), ('Netherlands', 'Gakpo', 6.3),
    ('Japan', 'Maeda', 5.9), ('Japan', 'Ueda', 6.0), ('Japan', 'Kubo', 6.0), ('Japan', 'Nakamura', 7.3), ('Japan', 'Kamada', 7.3), ('Japan', 'Ito', 5.5), ('Japan', 'Taniguchi', 6.0), ('Japan', 'Suzuki', 5.8), ('Japan', 'Sano', 6.0), ('Japan', 'Doan', 5.9), ('Japan', 'Watanabe', 6.1),

    # --- COSTA DE MARFIL VS ECUADOR ---
    ('Ivory Coast', 'Doue', 6.2), ('Ivory Coast', 'Singo', 6.0), ('Ivory Coast', 'Pepe', 5.5), ('Ivory Coast', 'Wahi', 6.2), ('Ivory Coast', 'Kessie', 6.3), ('Ivory Coast', 'Fofana', 6.3), ('Ivory Coast', 'Agbadou', 6.5), ('Ivory Coast', 'Konan', 5.5), ('Ivory Coast', 'Diomande', 6.6), ('Ivory Coast', 'Toure', 5.9),
    ('Ecuador', 'Yeboah', 5.9), ('Ecuador', 'Valencia', 5.8), ('Ecuador', 'Plata', 6.5), ('Ecuador', 'Vite', 6.1), ('Ecuador', 'Caicedo', 6.1), ('Ecuador', 'Franco', 6.1), ('Ecuador', 'Minda', 5.9), ('Ecuador', 'Hincapie', 4.5), ('Ecuador', 'Pacho', 5.5), ('Ecuador', 'Ordonez', 6.3), ('Ecuador', 'Galindez', 5.9),

    # --- SUECIA VS TÚNEZ ---
    ('Sweden', 'Lagerbielke', 7.5), ('Sweden', 'Bernhardsson', 8.0), ('Sweden', 'Isak', 8.5), ('Sweden', 'Nordfeldt', 7.3), ('Sweden', 'Hien', 8.0), ('Sweden', 'Karlstrom', 7.7), ('Sweden', 'Nygren', 7.6), ('Sweden', 'Lindelof', 7.5), ('Sweden', 'Gudmundsson', 7.8), ('Sweden', 'Gyokeres', 8.3), ('Sweden', 'Ayari', 8.9),
    ('Tunisia', 'Abdi', 6.6), ('Tunisia', 'Skhiri', 6.5), ('Tunisia', 'Ben Hamida', 7.4), ('Tunisia', 'Saad', 7.1), ('Tunisia', 'Mejbri', 7.1), ('Tunisia', 'Slimane', 6.5), ('Tunisia', 'Khedira', 6.6), ('Tunisia', 'Rekik', 6.9), ('Tunisia', 'Talbi', 7.0), ('Tunisia', 'Valery', 6.2), ('Tunisia', 'Chamakh', 4.5),

    # --- ESPAÑA VS CABO VERDE ---
    ('Spain', 'Llorente', 6.1), ('Spain', 'Cubarsi', 5.8), ('Spain', 'Pedri', 7.3), ('Spain', 'Simon', 5.6), ('Spain', 'Rodri', 6.4), ('Spain', 'Laporte', 5.9), ('Spain', 'Ruiz', 5.7), ('Spain', 'Cucurella', 5.6), ('Spain', 'Torres', 4.9), ('Spain', 'Oyarzabal', 5.5), ('Spain', 'Gavi', 5.1),
    ('Cabo Verde', 'Livramento', 4.8), ('Cabo Verde', 'Cabral', 5.1), ('Cabo Verde', 'Monteiro', 5.5), ('Cabo Verde', 'Mendes', 5.4), ('Cabo Verde', 'Duarte', 5.0), ('Cabo Verde', 'Pina', 5.7), ('Cabo Verde', 'Lopes', 5.8), ('Cabo Verde', 'Diney', 6.3), ('Cabo Verde', 'Moreira', 4.5), ('Cabo Verde', 'Vozinha', 8.5),

    # --- BÉLGICA VS EGIPTO ---
    ('Belgium', 'Courtois', 4.9), ('Belgium', 'Meunier', 5.2), ('Belgium', 'Ngoy', 5.9), ('Belgium', 'Mechele', 6.1), ('Belgium', 'Onana', 5.1), ('Belgium', 'Castagne', 5.3), ('Belgium', 'Tielemans', 5.6), ('Belgium', 'Trossard', 5.1), ('Belgium', 'De Bruyne', 4.8), ('Belgium', 'Doku', 4.5), ('Belgium', 'De Ketelaere', 5.4),
    ('Egypt', 'Marmoush', 4.8), ('Egypt', 'Ziko', 5.0), ('Egypt', 'Ashour', 6.6), ('Egypt', 'Salah', 5.6), ('Egypt', 'Attia', 4.7), ('Egypt', 'Fotouh', 5.2), ('Egypt', 'Fathy', 5.9), ('Egypt', 'Ibrahim', 6.0), ('Egypt', 'Shobeir', 5.5), ('Egypt', 'Lasheen', 6.1), ('Egypt', 'Hany', 5.6),

    # --- ARABIA SAUDITA VS URUGUAY ---
    ('Saudi Arabia', 'Al-Owais', 7.5), ('Saudi Arabia', 'Abdulhamid', 4.7), ('Saudi Arabia', 'Tambakti', 4.7), ('Saudi Arabia', 'Al-Amri', 6.3), ('Saudi Arabia', 'Al-Harbi', 4.9), ('Saudi Arabia', 'Abu Al-Shamat', 4.6), ('Saudi Arabia', 'Kanno', 5.1), ('Saudi Arabia', 'Al-Khaibari', 5.0), ('Saudi Arabia', 'Al-Dawsari', 4.7), ('Saudi Arabia', 'Al-Juwayr', 5.2), ('Saudi Arabia', 'Al-Buraikan', 5.2),
    ('Uruguay', 'Araujo', 7.2), ('Uruguay', 'Vina', 4.5), ('Uruguay', 'Nunez', 5.6), ('Uruguay', 'Vinas', 5.6), ('Uruguay', 'Bentancur', 6.1), ('Uruguay', 'Ugarte', 6.2), ('Uruguay', 'Valverde', 4.9), ('Uruguay', 'Olivera', 6.2), ('Uruguay', 'Caceres', 5.8), ('Uruguay', 'Varela', 6.9), ('Uruguay', 'Muslera', 5.8),

    # --- IRÁN VS NUEVA ZELANDA ---
    ('Iran', 'Beiranvand', 4.8), ('Iran', 'Rezaeian', 8.3), ('Iran', 'Khalilzadeh', 5.5), ('Iran', 'Nemati', 5.7), ('Iran', 'Mohammadi', 5.4), ('Iran', 'Mohebi', 6.2), ('Iran', 'Ghoddos', 6.0), ('Iran', 'Ezatolahi', 6.2), ('Iran', 'Yousefi', 6.1), ('Iran', 'Moghanlou', 6.1), ('Iran', 'Taremi', 6.2),
    ('New Zealand', 'Wood', 5.8), ('New Zealand', 'McCowatt', 5.7), ('New Zealand', 'Singh', 4.7), ('New Zealand', 'Just', 8.0), ('New Zealand', 'Stamenic', 5.4), ('New Zealand', 'Cacace', 5.6), ('New Zealand', 'Boxall', 5.6), ('New Zealand', 'Bell', 5.4), ('New Zealand', 'Surman', 5.9), ('New Zealand', 'Payne', 5.1), ('New Zealand', 'Crocombe', 4.5),

    # --- FRANCIA VS SENEGAL ---
    ('France', 'Kounde', 5.8), ('France', 'Maignan', 4.6), ('France', 'Upamecano', 6.8), ('France', 'Saliba', 5.5), ('France', 'Tchouameni', 6.2), ('France', 'Olise', 6.6), ('France', 'Dembele', 5.6), ('France', 'Mbappe', 7.3), ('France', 'Hernandez', 5.5), ('France', 'Rabiot', 5.9), ('France', 'Doue', 5.2),
    ('Senegal', 'Mane', 5.8), ('Senegal', 'Jackson', 5.3), ('Senegal', 'Sarr', 4.7), ('Senegal', 'Gueye', 4.9), ('Senegal', 'Diouf', 4.8), ('Senegal', 'Niakhate', 4.8), ('Senegal', 'Camara', 4.5), ('Senegal', 'Mendy', 4.7), ('Senegal', 'Koulibaly', 4.7), ('Senegal', 'Diatta', 6.1),

    # --- IRAK VS NORUEGA ---
    ('Iraq', 'Ali', 5.6), ('Iraq', 'Tahseen', 5.6), ('Iraq', 'Hasan', 4.5), ('Iraq', 'Hashim', 5.9), ('Iraq', 'Doski', 6.9), ('Iraq', 'Bayesh', 6.1), ('Iraq', 'Al-Ammari', 6.9), ('Iraq', 'Ismael', 5.7), ('Iraq', 'Jasim', 6.3), ('Iraq', 'Hussein', 6.4), ('Iraq', 'Nusa', 6.8),
    ('Norway', 'Haaland', 8.8), ('Norway', 'Aursnes', 6.8), ('Norway', 'Wolfe', 6.8), ('Norway', 'Heggem', 6.8), ('Norway', 'Berge', 7.2), ('Norway', 'Nyland', 6.9), ('Norway', 'Sorloth', 6.7), ('Norway', 'Odegaard', 7.1), ('Norway', 'Ajer', 6.9), ('Norway', 'Ryerson', 7.2),

    # --- ARGENTINA VS ARGELIA ---
    ('Argentina', 'Montiel', 7.0), ('Argentina', 'Martinez', 7.3), ('Argentina', 'Romero', 6.6), ('Argentina', 'De Paul', 7.0), ('Argentina', 'Mac Allister', 6.7), ('Argentina', 'Messi', 9.6), ('Argentina', 'Medina', 7.0), ('Argentina', 'Fernandez', 6.5), ('Argentina', 'Almada', 6.3),
    ('Algeria', 'Chaibi', 6.0), ('Algeria', 'Gouiri', 5.9), ('Algeria', 'Bentaleb', 6.1), ('Algeria', 'Maza', 5.8), ('Algeria', 'Moussa', 5.8), ('Algeria', 'Boudaoui', 5.6), ('Algeria', 'Ait-Nouri', 5.6), ('Algeria', 'Bensebaini', 5.9), ('Algeria', 'Mandi', 6.1), ('Algeria', 'Belghali', 5.3), ('Algeria', 'Zidane', 4.5),

    # --- AUSTRIA VS JORDANIA ---
    ('Austria', 'Posch', 5.9), ('Austria', 'Laimer', 6.3), ('Austria', 'Schlager', 6.2), ('Austria', 'Lienhart', 7.2), ('Austria', 'Alaba', 6.5), ('Austria', 'Seiwald', 7.0), ('Austria', 'Mwene', 6.3), ('Austria', 'Schmid', 7.2), ('Austria', 'Sabitzer', 6.4), ('Austria', 'Kalajdzic', 6.5),
    ('Jordan', 'Al-Fakhouri', 7.1), ('Jordan', 'Olwan', 7.2), ('Jordan', 'Al-Taamari', 6.0), ('Jordan', 'Abu Taha', 7.0), ('Jordan', 'Al-Rashdan', 6.7), ('Jordan', 'Al-Rawabdeh', 6.5), ('Jordan', 'Al-Arab', 6.5), ('Jordan', 'Abualnadi', 5.7), ('Jordan', 'Abulaila', 4.5), ('Jordan', 'Haddad', 5.6), ('Jordan', 'Nasib', 6.1),

    # --- PORTUGAL VS RD CONGO ---
    ('Portugal', 'Cancelo', 6.0), ('Portugal', 'Araujo', 4.7), ('Portugal', 'Neves', 7.0), ('Portugal', 'Costa', 4.7), ('Portugal', 'Veiga', 5.8), ('Portugal', 'Mendes', 5.4), ('Portugal', 'Vitinha', 5.6), ('Portugal', 'Silva', 5.2), ('Portugal', 'Fernandes', 6.3), ('Portugal', 'Neto', 5.7), ('Portugal', 'Ronaldo', 5.6),
    ('DR Congo', 'Wissa', 6.8), ('DR Congo', 'Kayembe', 5.9), ('DR Congo', 'Moutoussamy', 5.5), ('DR Congo', 'Masuaku', 6.2), ('DR Congo', 'Kapuadi', 5.7), ('DR Congo', 'Bakambu', 5.5), ('DR Congo', 'Mukau', 5.3), ('DR Congo', 'Tuanzebe', 5.7), ('DR Congo', 'Mbemba', 5.5), ('DR Congo', 'Wan-Bissaka', 6.5), ('DR Congo', 'Mpasi', 4.5),

    # --- INGLATERRA VS CROACIA ---
    ('England', 'James', 5.9), ('England', 'Anderson', 7.1), ('England', 'Madueke', 7.5), ('England', 'Pickford', 5.6), ('England', 'Stones', 6.0), ('England', 'Konsa', 5.9), ('England', 'Bellingham', 7.6), ('England', 'Kane', 8.5), ('England', 'Rice', 6.8), ('England', 'O\'Reilly', 6.3), ('England', 'Gordon', 6.6),
    ('Croatia', 'Pasalic', 5.6), ('Croatia', 'Perisic', 6.0), ('Croatia', 'Musa', 6.8), ('Croatia', 'Baturina', 6.5), ('Croatia', 'Sucic', 5.7), ('Croatia', 'Modric', 5.2), ('Croatia', 'Stanisic', 5.6), ('Croatia', 'Gvardiol', 4.5), ('Croatia', 'Vuskovic', 5.2), ('Croatia', 'Sutalo', 5.2), ('Croatia', 'Livakovic', 6.1),

    # --- GHANA VS PANAMÁ ---
    ('Ghana', 'Mensah', 6.1), ('Ghana', 'Opoku', 6.5), ('Ghana', 'Yirenkyi', 6.5), ('Ghana', 'Semenyo', 5.7), ('Ghana', 'Zigi', 6.3), ('Ghana', 'Nuamah', 5.1), ('Ghana', 'Ayew', 5.6), ('Ghana', 'Adjetey', 6.6), ('Ghana', 'Owusu', 5.8), ('Ghana', 'Senaya', 7.1), ('Ghana', 'Sulemana', 5.6),
    ('Panama', 'Rodriguez', 5.2), ('Panama', 'Waterman', 5.7), ('Panama', 'Barcenas', 5.6), ('Panama', 'Blackman', 5.6), ('Panama', 'Martinez', 5.1), ('Panama', 'Harvey', 4.8), ('Panama', 'Murillo', 6.0), ('Panama', 'Cordoba', 5.7), ('Panama', 'Andrade', 5.1), ('Panama', 'Ramos', 5.5), ('Panama', 'Mosquera', 4.5),

    # --- UZBEKISTÁN VS COLOMBIA ---
    ('Uzbekistan', 'Ashurmatov', 5.7), ('Uzbekistan', 'Karimov', 6.2), ('Uzbekistan', 'Yusupov', 4.5), ('Uzbekistan', 'Khusanov', 4.6), ('Uzbekistan', 'Mozgovoy', 5.6), ('Uzbekistan', 'Shukurov', 5.9), ('Uzbekistan', 'Abdullaev', 5.9), ('Uzbekistan', 'Nasrullaev', 5.4), ('Uzbekistan', 'Fayzullaev', 6.5), ('Uzbekistan', 'Shomurodov', 5.9), ('Uzbekistan', 'Urunov', 5.9),
    ('Colombia', 'Suarez', 6.7), ('Colombia', 'Diaz', 8.0), ('Colombia', 'Rodriguez', 6.8), ('Colombia', 'Arias', 6.4), ('Colombia', 'Mojica', 6.2), ('Colombia', 'Puerta', 6.8), ('Colombia', 'Lucumi', 6.2), ('Colombia', 'Sanchez', 7.3), ('Colombia', 'Vargas', 5.7), ('Colombia', 'Lerma', 6.4), ('Colombia', 'Munoz', 6.9)
]

print("Inyectando métricas y detectando nuevos talentos (Upsert)...")
actualizados = 0
nuevos = 0

for equipo, apellido, calificacion_pdf in calificaciones_mundial:
    nuevo_rating = int(calificacion_pdf * 10)
    
    # Filtro de Doble Seguridad: Coincide el Apellido exacto Y el Equipo exacto
    patron = rf"\b{apellido}\b"
    filtro_nombre = df['jugador'].str.contains(patron, flags=re.IGNORECASE, regex=True, na=False)
    filtro_equipo = df['equipo'] == equipo
    
    filtro_combinado = filtro_nombre & filtro_equipo
    
    if df[filtro_combinado].empty:
        # === LÓGICA DE INSERCIÓN (NUEVO JUGADOR) ===
        # Si no existe, lo creamos como Mediocampista Ofensivo (Aporta a ataque y defensa)
        nuevo_jugador = pd.DataFrame([{
            'equipo': equipo,
            'jugador': apellido,
            'posicion': 'MED', # Posición comodín para impactar el promedio general
            'rating_ataque': nuevo_rating,
            'rating_defensa': nuevo_rating,
            'fisco': 75
        }])
        
        # Lo añadimos al final de la base de datos
        df = pd.concat([df, nuevo_jugador], ignore_index=True)
        print(f" [+] NUEVO CRACK AÑADIDO: {apellido} ({equipo}) | Rating: {nuevo_rating}")
        nuevos += 1
        
    else:
        # === LÓGICA DE ACTUALIZACIÓN (JUGADOR EXISTENTE) ===
        for index, row in df[filtro_combinado].iterrows():
            pos = row['posicion']
            if pos == 'DEL':
                df.at[index, 'rating_ataque'] = nuevo_rating
            elif pos in ['DEF', 'POR']:
                df.at[index, 'rating_defensa'] = nuevo_rating
            elif pos == 'MED':
                df.at[index, 'rating_ataque'] = nuevo_rating
                df.at[index, 'rating_defensa'] = nuevo_rating
                
            print(f" -> Actualizado: {row['jugador']} ({row['equipo']}) | Forma: {nuevo_rating}")
            actualizados += 1

# Guardar la base de datos sobreescrita y expandida
df.to_csv('rendimiento_jugadores.csv', index=False, encoding='utf-8')
print(f"\n¡Listo! Se actualizaron {actualizados} jugadores y se añadieron {nuevos} nuevos talentos al catálogo.")
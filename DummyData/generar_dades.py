"""
HOSPITAL APOL·LO - Generació de Dummy Data
Autors: Pau Encinas, Damià Méndez
ASIX1 - Institut Sa Palomera - Curs 2025/2026

Genera dades fictícies per a totes les taules de la BD
amb les quantitats requerides per l'enunciat:
  - 50.000 pacients
  - 100 metges, 200 infermers, 100 neteja, 50 administratius
  - 100.000 visites
  - ~5% de registres en alfabet ciríl·lic

Requereix: pip install faker psycopg2 python-dotenv
"""

import random
import time
import string
from datetime import datetime, timedelta, date, time as dt_time

from faker import Faker
import psycopg2
from psycopg2.extras import execute_values

# ============================================================
# CONFIGURACIÓ
# ============================================================

# Connexió a la BD (modifica segons la teva configuració)
DB_CONFIG = {
    "host": "192.168.56.110",
    "port": 5432,
    "dbname": "hospitalapolo",
    "user": "posgres",
    "password": "Passw0rd",
}

# Faker amb locales
fake_es = Faker("es_ES")
fake_ru = Faker("ru_RU")
Faker.seed(42)  # Seed per resultats reproduïbles
random.seed(42)

# Percentatge de registres en ciríl·lic
PCT_CIRILIC = 0.05

# Quantitats
QTY_METGES = 100
QTY_INFERMERS = 200
QTY_NETEJA = 100
QTY_ADMIN = 50
QTY_PACIENTS = 50000
QTY_VISITES = 100000
QTY_HABITACIONS_PER_PLANTA = 10
QTY_QUIROFANS_PER_PLANTA = 2
QTY_MODELS_APARELL = 15
QTY_APARELLS = 80
QTY_DIAGNOSTICS = 50
QTY_MEDICAMENTS = 100
QTY_INGRESSOS = 10000
QTY_OPERACIONS = 5000

# Lot size per insercions massives
BATCH_SIZE = 5000


# ============================================================
# DADES PREDEFINIDES
# ============================================================

ESPECIALITATS = [
    "Cardiologia", "Traumatologia", "Pediatria", "Neurologia",
    "Dermatologia", "Oftalmologia", "Ginecologia", "Urologia",
    "Oncologia", "Pneumologia", "Psiquiatria", "Endocrinologia",
    "Nefrologia", "Reumatologia", "Otorrinolaringologia",
    "Cirurgia General", "Anestesiologia", "Medicina Interna",
    "Medicina d'Urgències", "Radiologia",
]

DIAGNOSTICS_LLISTA = [
    "Fractura de fèmur", "Pneumònia bacteriana", "Diabetis tipus 2",
    "Hipertensió arterial", "Infart agut de miocardi", "Asma bronquial",
    "Bronquitis aguda", "Gastroenteritis aguda", "Migran̈ya crònica",
    "Artritis reumatoide", "Hernia discal lumbar", "Insuficiència renal",
    "Anèmia ferropènica", "Infecció urinària", "Otitis mitjana",
    "Dermatitis atòpica", "Síndrome del túnel carpià", "Apendicitis aguda",
    "Colecistitis", "Pancreatitis aguda", "Ciàtica", "Esguince de turmell",
    "Fractura de canell", "Úlcera gàstrica", "Conjuntivitis",
    "Sinusitis", "Faringitis", "Lumbalgia", "Tendinitis", "Grip",
    "COVID-19", "Amigdalitis", "Cefalea tensional", "Vertigen",
    "Cataractes", "Glaucoma", "Arítmia cardíaca", "Trombosi venosa",
    "Embòlia pulmonar", "Epilèpsia", "Parkinson", "Alzheimer",
    "Esclerosi múltiple", "Fibromialgia", "Hipotiroidisme",
    "Hipertiroidisme", "Gota", "Osteoporosi", "Litiasi renal",
    "Hèrnia inguinal",
]

MEDICAMENTS_LLISTA = [
    "Ibuprofè 600mg", "Paracetamol 1g", "Amoxicil·lina 500mg",
    "Omeprazol 20mg", "Metformina 850mg", "Enalapril 10mg",
    "Atorvastatina 20mg", "Amlodipina 5mg", "Losartan 50mg",
    "Metoprolol 50mg", "Aspirina 100mg", "Diclofenac 50mg",
    "Ciprofloxacina 500mg", "Azitromicina 500mg", "Prednisona 5mg",
    "Insulina Lantus", "Salbutamol inhalador", "Lorazepam 1mg",
    "Sertralina 50mg", "Fluoxetina 20mg", "Tramadol 50mg",
    "Codeïna 30mg", "Ranitidina 150mg", "Pantoprazol 40mg",
    "Warfarina 5mg", "Heparina sòdica", "Furosemida 40mg",
    "Espironolactona 25mg", "Hidroclorotiazida 25mg",
    "Captopril 25mg", "Nifedipina 30mg", "Verapamil 80mg",
    "Digoxina 0.25mg", "Amiodarona 200mg", "Clopidogrel 75mg",
    "Eritromicina 500mg", "Clindamicina 300mg", "Vancomicina 500mg",
    "Gentamicina 80mg", "Cefalexina 500mg", "Ceftriaxona 1g",
    "Dexametasona 4mg", "Betametasona crema", "Mupirocina pomada",
    "Lidocaïna 2%", "Morfina 10mg", "Fentanil 50mcg",
    "Gabapentina 300mg", "Pregabalina 75mg", "Levodopa 250mg",
    "Donepezil 5mg", "Risperidona 2mg", "Olanzapina 10mg",
    "Quetiapina 100mg", "Litio 300mg", "Àcid valproic 500mg",
    "Carbamazepina 200mg", "Fenitoïna 100mg", "Clonazepam 0.5mg",
    "Alprazolam 0.25mg", "Zolpidem 10mg", "Melatonina 2mg",
    "Montelukast 10mg", "Cetirizina 10mg", "Loratadina 10mg",
    "Desloratadina 5mg", "Budesonida nasal", "Fluticasona inhalador",
    "Formoterol 12mcg", "Tiotropi 18mcg", "Albuterol 90mcg",
    "Metoclopramida 10mg", "Ondansetron 4mg", "Loperamida 2mg",
    "Bisacodil 5mg", "Lactulosa 15ml", "Mesalazina 500mg",
    "Sulfasalazina 500mg", "Metotrexat 2.5mg", "Ciclosporina 50mg",
    "Tacrolimús 1mg", "Azatioprina 50mg", "Micofenolat 500mg",
    "Tamoxifè 20mg", "Letrozol 2.5mg", "Exemestà 25mg",
    "Trastuzumab 440mg", "Cisplatí 50mg", "Paclitaxel 100mg",
    "Fluorouracil 500mg", "Imatinib 400mg", "Rituximab 500mg",
    "Bevacizumab 100mg", "Nivolumab 40mg", "Pembrolizumab 50mg",
    "Ferro oral 100mg", "Àcid fòlic 5mg", "Vitamina B12 1000mcg",
    "Calci + Vitamina D", "Bifosfonats 70mg",
]

MODELS_APARELL = [
    "Respirador mecànic", "Monitor cardíac", "Equip d'oxigen",
    "Desfibril·lador", "Bomba de perfusió", "Electrobisturí",
    "Aspirador quirúrgic", "Làmpara quirúrgica", "Monitor de signes vitals",
    "Ecògraf", "Equip de raigs X portàtil", "Pulsioxímetre",
    "Nebulitzador", "Equip d'anestèsia", "Taula quirúrgica",
]

TIPUS_FEINA_NETEJA = ["neteja"]
TIPUS_FEINA_ADMIN = ["administratiu"]
PAUTES = [
    "1 cada 8h", "1 cada 12h", "1 cada 24h", "2 cada 8h",
    "1 cada 6h", "1 al matí", "1 a la nit", "1 abans de menjar",
    "1 després de menjar", "Segons dolor",
]
DOSIS = [
    "1 comprimits", "2 comprimit", "5ml", "10ml", "1 càpsula",
    "2 càpsules", "1 sobre", "1 injecció", "2 gotes", "1 pegat",
]


# ============================================================
# FUNCIONS AUXILIARS
# ============================================================

def get_fake():
    """Retorna un objecte Faker amb locale ciríl·lic (~5%) o castellà (~95%)."""
    return fake_ru if random.random() < PCT_CIRILIC else fake_es


def generar_nif():
    """Genera un NIF espanyol fictici (8 dígits + lletra)."""
    nums = "".join([str(random.randint(0, 9)) for _ in range(8)])
    lletres = "TRWAGMYFPDXBNJZSQVHLCKE"
    lletra = lletres[int(nums) % 23]
    return nums + lletra


def generar_cip():
    """Genera un CIP (targeta sanitària) fictici: BBBB + 10 dígits."""
    prefix = random.choice(["CATS", "ANDA", "VALE", "MADX", "GALN"])
    nums = "".join([str(random.randint(0, 9)) for _ in range(10)])
    return prefix + nums


def generar_num_colegiat():
    """Genera un número de col·legiat fictici."""
    provincia = random.randint(1, 52)
    num = random.randint(10000, 99999)
    return f"{provincia:02d}/{num}"


def temps_aleatori(h_min=8, h_max=20):
    """Genera una hora aleatòria entre h_min i h_max."""
    h = random.randint(h_min, h_max - 1)
    m = random.choice([0, 15, 30, 45])
    return dt_time(h, m)


def data_aleatoria(anys_enrere=2):
    """Genera una data aleatòria dins els últims N anys."""
    avui = date.today()
    inici = avui - timedelta(days=365 * anys_enrere)
    delta = (avui - inici).days
    return inici + timedelta(days=random.randint(0, delta))


def print_progress(actual, total, nom_taula, t_inici):
    """Mostra una barra de progrés."""
    pct = actual / total * 100
    elapsed = time.time() - t_inici
    print(f"\r  [{nom_taula}] {actual:>7}/{total} ({pct:5.1f}%) - {elapsed:.1f}s", end="", flush=True)


# ============================================================
# FUNCIONS DE GENERACIÓ PER TAULA
# ============================================================

def generar_plantes(cursor):
    """Insereix les 4 plantes (si no existeixen)."""
    print("  [planta] Verificant plantes...")
    cursor.execute("SELECT COUNT(*) FROM planta")
    if cursor.fetchone()[0] == 0:
        for i in range(1, 5):
            cursor.execute("INSERT INTO planta (num_planta) VALUES (%s) ON CONFLICT DO NOTHING", (i,))
    print("  [planta] 4 plantes OK")


def generar_habitacions(cursor):
    """Genera habitacions per cada planta."""
    print(f"  [habitacio] Generant {QTY_HABITACIONS_PER_PLANTA} per planta...")
    for planta in range(1, 5):
        for hab in range(1, QTY_HABITACIONS_PER_PLANTA + 1):
            num_hab = f"H{hab:02d}"
            llits = random.choice([1, 1, 2, 2, 3])
            cursor.execute(
                "INSERT INTO habitacio (num_planta, num_habitacio, num_llits) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                (planta, num_hab, llits)
            )
    total = QTY_HABITACIONS_PER_PLANTA * 4
    print(f"  [habitacio] {total} habitacions OK")
    return [(p, f"H{h:02d}") for p in range(1, 5) for h in range(1, QTY_HABITACIONS_PER_PLANTA + 1)]


def generar_quirofans(cursor):
    """Genera quiròfans per cada planta."""
    print(f"  [quirofan] Generant {QTY_QUIROFANS_PER_PLANTA} per planta...")
    for planta in range(1, 5):
        for q in range(1, QTY_QUIROFANS_PER_PLANTA + 1):
            num_q = f"Q{q}"
            cursor.execute(
                "INSERT INTO quirofan (num_planta, num_quirofan) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (planta, num_q)
            )
    total = QTY_QUIROFANS_PER_PLANTA * 4
    print(f"  [quirofan] {total} quiròfans OK")
    return [(p, f"Q{q}") for p in range(1, 5) for q in range(1, QTY_QUIROFANS_PER_PLANTA + 1)]


def generar_models_aparell(cursor):
    """Genera models d'aparells mèdics."""
    print(f"  [model_aparell] Generant {QTY_MODELS_APARELL} models...")
    ids = []
    for nom in MODELS_APARELL[:QTY_MODELS_APARELL]:
        cursor.execute(
            "INSERT INTO model_aparell (nom, descripcio) VALUES (%s, %s) RETURNING id_model",
            (nom, f"Aparell mèdic de tipus {nom.lower()}")
        )
        ids.append(cursor.fetchone()[0])
    print(f"  [model_aparell] {len(ids)} models OK")
    return ids


def generar_aparells(cursor, quirofans, model_ids):
    """Genera aparells individuals assignats a quiròfans."""
    print(f"  [aparell] Generant {QTY_APARELLS} aparells...")
    for _ in range(QTY_APARELLS):
        planta, quirofan = random.choice(quirofans)
        model = random.choice(model_ids)
        data_rev = fake_es.date_between(start_date="-1y", end_date="today")
        cursor.execute(
            "INSERT INTO aparell (num_planta, num_quirofan, id_model, data_revisio) VALUES (%s, %s, %s, %s)",
            (planta, quirofan, model, data_rev)
        )
    print(f"  [aparell] {QTY_APARELLS} aparells OK")


def generar_diagnostics(cursor):
    """Genera el catàleg de diagnòstics."""
    print(f"  [diagnostic] Generant {QTY_DIAGNOSTICS} diagnòstics...")
    ids = []
    for desc in DIAGNOSTICS_LLISTA[:QTY_DIAGNOSTICS]:
        cursor.execute(
            "INSERT INTO diagnostic (descripcio) VALUES (%s) RETURNING id_diagnostic",
            (desc,)
        )
        ids.append(cursor.fetchone()[0])
    print(f"  [diagnostic] {len(ids)} diagnòstics OK")
    return ids


def generar_medicaments(cursor):
    """Genera el catàleg de medicaments."""
    print(f"  [medicament] Generant {QTY_MEDICAMENTS} medicaments...")
    ids = []
    for med in MEDICAMENTS_LLISTA[:QTY_MEDICAMENTS]:
        nom = med.split(" ")[0]
        cursor.execute(
            "INSERT INTO medicament (nom, descripcio) VALUES (%s, %s) RETURNING id_medicament",
            (nom, med)
        )
        ids.append(cursor.fetchone()[0])
    print(f"  [medicament] {len(ids)} medicaments OK")
    return ids


def generar_empleats_i_metges(cursor):
    """Genera 100 empleats de tipus metge + registre a la taula metge."""
    print(f"  [metge] Generant {QTY_METGES} metges...")
    metge_ids = []
    t = time.time()
    nifs_usats = set()

    for i in range(QTY_METGES):
        f = get_fake()
        nif = generar_nif()
        while nif in nifs_usats:
            nif = generar_nif()
        nifs_usats.add(nif)

        cursor.execute(
            """INSERT INTO empleat (nom, cognom1, cognom2, nif, email, telefon, salari,
               data_contractacio, adreca, tipus_feina)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'metge') RETURNING id_emp""",
            (
                f.first_name(), f.last_name(), f.last_name(),
                nif, f.email(), f.phone_number(),
                round(random.uniform(3000, 8000), 2),
                f.date_between(start_date="-15y", end_date="-1y"),
                f.address().replace("\n", ", "),
            )
        )
        id_emp = cursor.fetchone()[0]

        esp = random.choice(ESPECIALITATS)
        cursor.execute(
            """INSERT INTO metge (id_metge, cv, especialitat, num_colegiat)
               VALUES (%s, %s, %s, %s)""",
            (id_emp, f.text(max_nb_chars=200), esp, generar_num_colegiat())
        )
        metge_ids.append(id_emp)
        if (i + 1) % 20 == 0:
            print_progress(i + 1, QTY_METGES, "metge", t)

    print(f"\n  [metge] {QTY_METGES} metges OK")
    return metge_ids, nifs_usats


def generar_empleats_i_infermers(cursor, metge_ids, nifs_usats):
    """Genera 200 empleats de tipus infermer + registre a la taula infermer."""
    print(f"  [infermer] Generant {QTY_INFERMERS} infermers...")
    infermer_ids = []
    t = time.time()

    for i in range(QTY_INFERMERS):
        f = get_fake()
        nif = generar_nif()
        while nif in nifs_usats:
            nif = generar_nif()
        nifs_usats.add(nif)

        cursor.execute(
            """INSERT INTO empleat (nom, cognom1, cognom2, nif, email, telefon, salari,
               data_contractacio, adreca, tipus_feina)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'infermer') RETURNING id_emp""",
            (
                f.first_name(), f.last_name(), f.last_name(),
                nif, f.email(), f.phone_number(),
                round(random.uniform(2000, 4000), 2),
                f.date_between(start_date="-10y", end_date="-1y"),
                f.address().replace("\n", ", "),
            )
        )
        id_emp = cursor.fetchone()[0]

        # 70% assignats a metge, 30% de planta
        if random.random() < 0.7:
            id_metge = random.choice(metge_ids)
            num_planta = None
        else:
            id_metge = None
            num_planta = random.randint(1, 4)

        cursor.execute(
            """INSERT INTO infermer (id_inf, cv, especialitat, id_metge, num_planta)
               VALUES (%s, %s, %s, %s, %s)""",
            (
                id_emp,
                f.text(max_nb_chars=150),
                random.choice(ESPECIALITATS) if random.random() < 0.5 else None,
                id_metge,
                num_planta,
            )
        )
        infermer_ids.append(id_emp)
        if (i + 1) % 50 == 0:
            print_progress(i + 1, QTY_INFERMERS, "infermer", t)

    print(f"\n  [infermer] {QTY_INFERMERS} infermers OK")
    return infermer_ids


def generar_empleats_varis(cursor, nifs_usats, tipus, quantitat):
    """Genera empleats de neteja o administratius."""
    print(f"  [empleat-{tipus}] Generant {quantitat}...")
    t = time.time()

    for i in range(quantitat):
        f = get_fake()
        nif = generar_nif()
        while nif in nifs_usats:
            nif = generar_nif()
        nifs_usats.add(nif)

        cursor.execute(
            """INSERT INTO empleat (nom, cognom1, cognom2, nif, email, telefon, salari,
               data_contractacio, adreca, tipus_feina)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                f.first_name(), f.last_name(), f.last_name(),
                nif, f.email(), f.phone_number(),
                round(random.uniform(1500, 2500), 2),
                f.date_between(start_date="-10y", end_date="-1y"),
                f.address().replace("\n", ", "),
                tipus,
            )
        )
        if (i + 1) % 25 == 0:
            print_progress(i + 1, quantitat, f"empleat-{tipus}", t)

    print(f"\n  [empleat-{tipus}] {quantitat} OK")


def generar_pacients(cursor):
    """Genera 50.000 pacients per lots."""
    print(f"  [pacient] Generant {QTY_PACIENTS} pacients...")
    ids = []
    t = time.time()
    nifs_usats = set()

    for batch_start in range(0, QTY_PACIENTS, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, QTY_PACIENTS)
        dades = []

        for _ in range(batch_start, batch_end):
            f = get_fake()
            nif = generar_nif()
            while nif in nifs_usats:
                nif = generar_nif()
            nifs_usats.add(nif)

            dades.append((
                generar_cip(),
                f.first_name(),
                f.last_name(),
                f.last_name(),
                f.address().replace("\n", ", "),
                f.email(),
                f.phone_number(),
                nif,
                random.choice(["home", "dona", "altre"]),
            ))

        result = execute_values(
            cursor,
            """INSERT INTO pacient (targeta_sanitaria, nom, cognom1, cognom2,
               adreca, email, telefon, nif, sexe)
               VALUES %s RETURNING id_pacient""",
            dades,
            fetch=True,
        )
        ids.extend([r[0] for r in result])
        print_progress(len(ids), QTY_PACIENTS, "pacient", t)

    print(f"\n  [pacient] {len(ids)} pacients OK")
    return ids


def generar_receptes_i_visites(cursor, metge_ids, pacient_ids, diagnostic_ids):
    """Genera 100.000 visites amb receptes associades."""
    print(f"  [visita] Generant {QTY_VISITES} visites + receptes...")
    visita_ids = []
    recepta_ids = []
    t = time.time()

    for batch_start in range(0, QTY_VISITES, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, QTY_VISITES)

        for _ in range(batch_start, batch_end):
            dia = data_aleatoria(anys_enrere=2)
            hora = temps_aleatori(8, 20)
            id_metge = random.choice(metge_ids)
            id_pacient = random.choice(pacient_ids)
            id_diagnostic = random.choice(diagnostic_ids) if random.random() < 0.8 else None

            # 70% de visites tenen recepta
            id_recepta = None
            if random.random() < 0.7:
                data_inici = dia
                data_fi = dia + timedelta(days=random.randint(5, 30))
                cursor.execute(
                    """INSERT INTO recepta (data_inici, data_finalitzacio)
                       VALUES (%s, %s) RETURNING id_recepta""",
                    (data_inici, data_fi)
                )
                id_recepta = cursor.fetchone()[0]
                recepta_ids.append(id_recepta)

            cursor.execute(
                """INSERT INTO visita (hora, data, descripcio, id_metge, id_pacient,
                   id_recepta, id_diagnostic)
                   VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id_visita""",
                (
                    hora, dia,
                    fake_es.sentence(nb_words=10) if random.random() < 0.9 else None,
                    id_metge, id_pacient, id_recepta, id_diagnostic,
                )
            )
            visita_ids.append(cursor.fetchone()[0])

        cursor.connection.commit()
        print_progress(len(visita_ids), QTY_VISITES, "visita", t)

    print(f"\n  [visita] {len(visita_ids)} visites + {len(recepta_ids)} receptes OK")
    return visita_ids, recepta_ids


def generar_linies_recepta(cursor, recepta_ids, medicament_ids):
    """Genera línies de recepta (1-3 medicaments per recepta)."""
    total = len(recepta_ids)
    print(f"  [linia_recepta] Generant línies per {total} receptes...")
    t = time.time()
    count = 0

    for i, id_recepta in enumerate(recepta_ids):
        num_linies = random.randint(1, 3)
        meds_escollits = random.sample(medicament_ids, min(num_linies, len(medicament_ids)))

        for num_linia, id_med in enumerate(meds_escollits, 1):
            cursor.execute(
                """INSERT INTO linia_recepta (id_recepta, num_linia, pauta, dosi, id_medicament)
                   VALUES (%s, %s, %s, %s, %s)""",
                (id_recepta, num_linia, random.choice(PAUTES), random.choice(DOSIS), id_med)
            )
            count += 1

        if (i + 1) % 5000 == 0:
            cursor.connection.commit()
            print_progress(i + 1, total, "linia_recepta", t)

    cursor.connection.commit()
    print(f"\n  [linia_recepta] {count} línies OK")


def generar_ingressos(cursor, habitacions, pacient_ids):
    """Genera ingressos de pacients a habitacions."""
    print(f"  [ingres] Generant {QTY_INGRESSOS} ingressos...")
    t = time.time()

    for i in range(QTY_INGRESSOS):
        planta, hab = random.choice(habitacions)
        id_pacient = random.choice(pacient_ids)
        entrada_prev = data_aleatoria(anys_enrere=2)
        dies_ingres = random.randint(1, 15)
        sortida_prev = entrada_prev + timedelta(days=dies_ingres)

        # 80% ja han sortit
        if random.random() < 0.8:
            entrada = datetime.combine(entrada_prev, temps_aleatori(7, 12))
            sortida = datetime.combine(
                entrada_prev + timedelta(days=random.randint(1, dies_ingres)),
                temps_aleatori(10, 18)
            )
        else:
            entrada = datetime.combine(entrada_prev, temps_aleatori(7, 12))
            sortida = None

        cursor.execute(
            """INSERT INTO ingres (num_planta, num_habitacio, id_pacient,
               entrada, sortida, entrada_prevista, sortida_prevista)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (planta, hab, id_pacient, entrada, sortida, entrada_prev, sortida_prev)
        )
        if (i + 1) % 2000 == 0:
            cursor.connection.commit()
            print_progress(i + 1, QTY_INGRESSOS, "ingres", t)

    cursor.connection.commit()
    print(f"\n  [ingres] {QTY_INGRESSOS} ingressos OK")


def generar_operacions(cursor, quirofans, metge_ids, pacient_ids, infermer_ids):
    """Genera operacions i assigna infermers."""
    print(f"  [operacio] Generant {QTY_OPERACIONS} operacions...")
    t = time.time()
    operacio_ids = []

    for i in range(QTY_OPERACIONS):
        planta, quirofan = random.choice(quirofans)
        id_metge = random.choice(metge_ids)
        id_pacient = random.choice(pacient_ids)
        entrada_prev = datetime.combine(data_aleatoria(2), temps_aleatori(8, 16))
        durada = timedelta(hours=random.randint(1, 5))
        sortida_prev = entrada_prev + durada

        # 70% ja realitzades
        if random.random() < 0.7:
            entrada = entrada_prev + timedelta(minutes=random.randint(-15, 15))
            sortida = sortida_prev + timedelta(minutes=random.randint(-30, 30))
        else:
            entrada = None
            sortida = None

        cursor.execute(
            """INSERT INTO operacio (descripcio, entrada, sortida, entrada_prevista,
               sortida_prevista, id_metge, id_pacient, num_planta, num_quirofan)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_operacio""",
            (
                fake_es.sentence(nb_words=6),
                entrada, sortida, entrada_prev, sortida_prev,
                id_metge, id_pacient, planta, quirofan,
            )
        )
        op_id = cursor.fetchone()[0]
        operacio_ids.append(op_id)

        # Assignar 2-4 infermers per operació
        num_inf = random.randint(2, 4)
        infs = random.sample(infermer_ids, min(num_inf, len(infermer_ids)))
        for id_inf in infs:
            cursor.execute(
                "INSERT INTO operacio_infermer (id_inf, id_operacio) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (id_inf, op_id)
            )

        if (i + 1) % 1000 == 0:
            cursor.connection.commit()
            print_progress(i + 1, QTY_OPERACIONS, "operacio", t)

    cursor.connection.commit()
    print(f"\n  [operacio] {QTY_OPERACIONS} operacions + assistències OK")


# ============================================================
# FUNCIÓ PRINCIPAL
# ============================================================

def generar_dummy_data():
    """Executa la generació completa de dummy data."""
    print("=" * 56)
    print("  HOSPITAL DE BLANES - Generació de Dummy Data")
    print("=" * 56)
    t_total = time.time()

    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
    cursor = conn.cursor()

    try:
        # 1. Estructura de l'hospital
        print("\n[FASE 1] Estructura de l'hospital")
        generar_plantes(cursor)
        habitacions = generar_habitacions(cursor)
        quirofans = generar_quirofans(cursor)
        model_ids = generar_models_aparell(cursor)
        generar_aparells(cursor, quirofans, model_ids)
        conn.commit()

        # 2. Catàlegs
        print("\n[FASE 2] Catàlegs (diagnòstics i medicaments)")
        diagnostic_ids = generar_diagnostics(cursor)
        medicament_ids = generar_medicaments(cursor)
        conn.commit()

        # 3. Personal
        print("\n[FASE 3] Personal de l'hospital")
        metge_ids, nifs_usats = generar_empleats_i_metges(cursor)
        conn.commit()
        infermer_ids = generar_empleats_i_infermers(cursor, metge_ids, nifs_usats)
        conn.commit()
        generar_empleats_varis(cursor, nifs_usats, "neteja", QTY_NETEJA)
        conn.commit()
        generar_empleats_varis(cursor, nifs_usats, "administratiu", QTY_ADMIN)
        conn.commit()

        # 4. Pacients
        print("\n[FASE 4] Pacients")
        pacient_ids = generar_pacients(cursor)
        conn.commit()

        # 5. Visites i receptes
        print("\n[FASE 5] Visites, receptes i línies de recepta")
        visita_ids, recepta_ids = generar_receptes_i_visites(
            cursor, metge_ids, pacient_ids, diagnostic_ids
        )
        conn.commit()
        generar_linies_recepta(cursor, recepta_ids, medicament_ids)
        conn.commit()

        # 6. Ingressos i operacions
        print("\n[FASE 6] Ingressos i operacions")
        generar_ingressos(cursor, habitacions, pacient_ids)
        conn.commit()
        generar_operacions(cursor, quirofans, metge_ids, pacient_ids, infermer_ids)
        conn.commit()

        elapsed = time.time() - t_total
        print("\n" + "=" * 56)
        print(f"  COMPLETAT en {elapsed:.1f} segons!")
        print("=" * 56)
        print(f"  Empleats:   {QTY_METGES + QTY_INFERMERS + QTY_NETEJA + QTY_ADMIN}")
        print(f"    Metges:      {QTY_METGES}")
        print(f"    Infermers:   {QTY_INFERMERS}")
        print(f"    Neteja:      {QTY_NETEJA}")
        print(f"    Admin:       {QTY_ADMIN}")
        print(f"  Pacients:   {QTY_PACIENTS}")
        print(f"  Visites:    {QTY_VISITES}")
        print(f"  Receptes:   {len(recepta_ids)}")
        print(f"  Ingressos:  {QTY_INGRESSOS}")
        print(f"  Operacions: {QTY_OPERACIONS}")
        print("=" * 56)

    except Exception as e:
        conn.rollback()
        print(f"\n\nERROR: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


# ============================================================
# EXECUCIÓ DIRECTA
# ============================================================

if __name__ == "__main__":
    generar_dummy_data()

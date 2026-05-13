"""
HOSPITAL DE BLANES - Eliminació de Dummy Data
Elimina totes les dades de les taules respectant l'ordre de FK.
"""

import psycopg2

DB_CONFIG = {
    "host": "192.168.56.110",
    "port": 5432,
    "dbname": "hospitalapolo",
    "user": "posgres",
    "password": "Passw0rd",
}

# Ordre invers de dependències (primer les que tenen FK)
TAULES_EN_ORDRE = [
    "operacio_infermer",
    "operacio",
    "ingres",
    "linia_recepta",
    "visita",
    "recepta",
    "pacient",
    "aparell",
    "infermer",
    "metge",
    "empleat",
    "medicament",
    "diagnostic",
    "model_aparell",
    "quirofan",
    "habitacio",
    # NO eliminem planta (4 registres fixes)
]


def eliminar_dummy_data():
    """Elimina totes les dades dummy de la BD."""
    print("=" * 56)
    print("  HOSPITAL DE BLANES - Eliminació de Dummy Data")
    print("=" * 56)

    confirmacio = input("\n  Segur que vols eliminar TOTES les dades? (escriu SI): ")
    if confirmacio != "SI":
        print("  Operació cancel·lada.")
        return

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        for taula in TAULES_EN_ORDRE:
            cursor.execute(f"TRUNCATE TABLE {taula} CASCADE;")
            cursor.execute(f"SELECT COUNT(*) FROM {taula};")
            count = cursor.fetchone()[0]
            print(f"  [TRUNCATE] {taula:25s} -> {count} registres")

        # Reiniciar seqüències
        cursor.execute("""
            DO $$
            DECLARE
                seq RECORD;
            BEGIN
                FOR seq IN
                    SELECT c.relname AS seq_name
                    FROM pg_class c
                    WHERE c.relkind = 'S'
                LOOP
                    EXECUTE 'ALTER SEQUENCE ' || seq.seq_name || ' RESTART WITH 1';
                END LOOP;
            END $$;
        """)

        conn.commit()
        print("\n  Totes les dades eliminades i seqüències reiniciades.")
        print("=" * 56)

    except Exception as e:
        conn.rollback()
        print(f"\n  ERROR: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    eliminar_dummy_data()

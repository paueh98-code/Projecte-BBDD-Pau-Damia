"""
HOSPITAL DE APOL·LO - Eliminació de Dummy Data
Elimina totes les dades de les taules respectant l'ordre de FK.
"""
import tkinter as tk
import psycopg2

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


def eliminar_dummy_data(connexion, root):
    """Elimina totes les dades dummy de la BD."""
    eliminarDummyData_PopUp = tk.Toplevel(root)
    eliminarDummyData_PopUp.title("Eliminar Dades")
    eliminarDummyData_PopUp.geometry("450x200")

    tk.Label(eliminarDummyData_PopUp, text="Segur que vols eliminar TOTES les dades?").grid(row=1, column=1, columnspan=3)
    
    tk.Button(eliminarDummyData_PopUp, text="Purgar totes les dades", command=lambda: granPurga(connexion)).grid(row=2, column=1)
    tk.Button(eliminarDummyData_PopUp, text="Cancel·lar", command=lambda: eliminarDummyData_PopUp.destroy()).grid(row=2, column=3)

def granPurga(connexion):
    cursor = connexion.cursor()
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

        connexion.commit()

    except Exception as e:
        connexion.rollback()
        print(f"\n  ERROR: {e}")
        raise
    finally:
        cursor.close()

if __name__ == "__main__":
    eliminar_dummy_data()

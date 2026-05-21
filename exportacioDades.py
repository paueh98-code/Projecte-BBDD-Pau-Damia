import psycopg2 as psy
import psycopg2.extras as psye
import tkinter as tk
import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError

def dadesAExportar(connexion, root):
    exportacioPopup = tk.Toplevel(root)
    exportacioPopup.title("Exportació de dades a JSON")
    exportacioPopup.geometry("500x250")

    tk.Label(exportacioPopup, text="Inici del rang de dies:").grid(row=1, column=1)
    diaIniciEntry = tk.Entry(exportacioPopup, width=20)
    diaIniciEntry.grid(row=1, column=2)

    tk.Label(exportacioPopup, text="Final del rang de dies:").grid(row=1, column=3)
    diaFinalEntry = tk.Entry(exportacioPopup, width=20)
    diaFinalEntry.grid(row=1, column=4)

    tk.Button(exportacioPopup, text="Exportar", command=lambda: exportacioDades(connexion, diaIniciEntry, diaFinalEntry)).grid(row=2, column=1)
    tk.Button(exportacioPopup, text="Cancel·lar", command=lambda: exportacioPopup.destroy()).grid(row=2, column=4)

def exportacioDades(connexion, diaIniciEntry, diaFinalEntry):
    cursor = connexion.cursor(cursor_factory = psye.RealDictCursor)
    try:
        cursor.execute('''
            SELECT * 
            FROM visita
            WHERE data BETWEEN %s and %s''', (diaIniciEntry.get(), diaFinalEntry.get()))
        with open("Dades_Exportades.json", "w+") as fitxer:
            fitxer.write("[\n")

            primeraFila = True

            while True:
                files = cursor.fetchmany(5000)

                if not files:
                    break

                for fila in files:
                    if not primeraFila:
                        fitxer.write(",\n")
                    
                    json.dump(
                        fila,
                        fitxer,
                        ensure_ascii=False,
                        default=str
                    )

                    primeraFila = False
            fitxer.write("\n]")
        print("Exportació exitosa")

        cursor.close()

        with open("Schema_Exportacio.schema.json", "r") as schema:
            jsonSchema = json.load(schema)
        
        with open("Dades_Exportades.json", "r") as fitxer:
            dades = json.load(fitxer)
        
    except Exception as e:
        print("ERROR", e)
        connexion.rollback()
    try:
        validate(instance=dades, schema=jsonSchema)
        print("Validació exitosa")

    except ValidationError as e:
        print("Error de validació:", e.message)
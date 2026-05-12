import tkinter as tk
import psycopg2 as psy

#Funció 10: Crea la finestra per a inserir pacients a la base de dades
def registrarPacients(root, connexion):
    global tarSanEntry
    global pNameEntry
    global pSurname1Entry
    global pSurname2Entry
    global pAdrecaEntry
    global pEmailEntry
    global pTelEntry
    global pNifEntry
    global sexeEntry

    registrarPacients_popup = tk.Toplevel(root)
    registrarPacients_popup.title("Registrar a un pacient")
    registrarPacients_popup.geometry("900x400")

    tk.Label(registrarPacients_popup, text="Nom:").grid(row=1, column=1)
    pNameEntry = tk.Entry(registrarPacients_popup, width=30)
    pNameEntry.grid(row=1, column=2, pady= 10, padx= 20)
    
    tk.Label(registrarPacients_popup, text="Primer Cognom:").grid(row=1, column=3)
    pSurname1Entry = tk.Entry(registrarPacients_popup, width=30)
    pSurname1Entry.grid(row=1, column=4, pady= 10, padx= 20)

    tk.Label(registrarPacients_popup, text="Segon Cognom:").grid(row=1, column=5)
    pSurname2Entry = tk.Entry(registrarPacients_popup, width=30)
    pSurname2Entry.grid(row=1, column=6, pady= 10, padx= 20)
    
    tk.Label(registrarPacients_popup, text="Targeta Sanitaria:").grid(row=2, column=1)
    tarSanEntry = tk.Entry(registrarPacients_popup, width=30)
    tarSanEntry.grid(row=2, column=2, pady= 10, padx= 20)

    tk.Label(registrarPacients_popup, text="Adreça:").grid(row=2, column=3)
    pAdrecaEntry = tk.Entry(registrarPacients_popup, width=30)
    pAdrecaEntry.grid(row=2, column=4, pady= 10, padx= 20)

    tk.Label(registrarPacients_popup, text="Email:").grid(row=2, column=5)
    pEmailEntry = tk.Entry(registrarPacients_popup, width=30)
    pEmailEntry.grid(row=2, column=6, pady= 10, padx= 20)

    tk.Label(registrarPacients_popup, text="Telèfon:").grid(row=3, column=1)
    pTelEntry = tk.Entry(registrarPacients_popup, width=30)
    pTelEntry.grid(row=3, column=2, pady= 10, padx= 20)

    tk.Label(registrarPacients_popup, text="NIF:").grid(row=3, column=3)
    pNifEntry = tk.Entry(registrarPacients_popup, width=30)
    pNifEntry.grid(row=3, column=4, pady= 10, padx= 20)

    tk.Label(registrarPacients_popup, text="Sexe:").grid(row=3, column=5)
    sexeEntry = tk.Entry(registrarPacients_popup, width=30)
    sexeEntry.grid(row=3, column=6, pady= 10, padx= 20)

    tk.Button(registrarPacients_popup, text="Enviar", command=lambda: enviarPacient(tarSanEntry, pNameEntry, pSurname1Entry, pSurname2Entry, pAdrecaEntry, pEmailEntry, pTelEntry, pNifEntry, sexeEntry, connexion)).grid(row=4, column=1, pady=10, padx=20)
    
    tk.Button(registrarPacients_popup, text="Sortir", command=registrarPacients_popup.destroy).grid(row=4, column=6, pady=10, padx=20)


#Funció 11: Fa el Insert utilitzant les dades del formulari de la funció 6
def enviarPacient(tarSanEntry, pNameEntry, pSurname1Entry, pSurname2Entry, pAdrecaEntry, pEmailEntry, pTelEntry, pNifEntry, sexeEntry, connexion): 
    try:
        cursor = connexion.cursor()
        cursor.execute('''
            INSERT INTO pacient(targeta_sanitaria, nom, cognom1, cognom2, adreca, email, telefon, nif, sexe)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''', (tarSanEntry.get() ,pNameEntry.get(), pSurname1Entry.get(), pSurname2Entry.get(), pAdrecaEntry.get(), pEmailEntry.get(), pTelEntry.get(), pNifEntry.get(), sexeEntry.get()))
        connexion.commit()
        cursor.close()
    except Exception as e:
        connexion.rollback()
        print("ERROR", e)
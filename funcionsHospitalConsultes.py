import tkinter as tk
import psycopg2 as psy
from tkinter import ttk
import datetime as dt

#Funció 12: Demana les dades per a verificar la relació del infermer/era
def relacioInf(connexion, root):
    relacioInf_popUp = tk.Toplevel(root)
    relacioInf_popUp.title("Relacio del Infermer")
    relacioInf_popUp.geometry("600x300")

    tk.Label(relacioInf_popUp, text="Id Infermer").grid(row=1, column=1)
    idInfermerEntry = tk.Entry(relacioInf_popUp, width=30)
    idInfermerEntry.grid(row=1, column=3)

    text = tk.Text(relacioInf_popUp, height=2, width=70)
    text.grid(row=2, column=1, columnspan=3)

    tk.Button(relacioInf_popUp, text="Comprovar", command=lambda: comprovarRelacio(connexion, text, idInfermerEntry)).grid(row=3, column=2)

#Funció 13: Crida el procediment per veure la relació
def comprovarRelacio(connexion, text, idInfermerEntry):
    try:
        cursor = connexion.cursor()
        
        #Netejar les notices anteriors
        connexion.notices.clear()

        #Call a la procedure
        cursor.execute('''
            CALL fn_relacio_inf(%s)''', (idInfermerEntry.get(),))

        #Netejar el text de la variable "text"
        text.delete("1.0", "end")

        #Anotar les noticies que va rebent
        for notice in connexion.notices:
            text.insert("end", notice)

        connexion.commit()
        cursor.close()
    except Exception as e:
        print("ERROR", e)
        connexion.rollback()

#Funció 14: Demana les dades per al informe de tot del que es disposa en una planta
def resumPlanta(root, connexion):
    resumPlanta_popUp = tk.Toplevel(root)
    resumPlanta_popUp.title("Caracteristiques de la planta")
    resumPlanta_popUp.geometry("900x450")

    tk.Label(resumPlanta_popUp, text="Planta a analitzar:").grid(row=1, column=1)
    plantaEntry = tk.Entry(resumPlanta_popUp, width=30)
    plantaEntry.grid(row=1, column=3)

    tree = ttk.Treeview(resumPlanta_popUp, columns=("Habitacions", "Quirofans", "Personal"), show="headings")
    tree.heading("Habitacions", text="Habitacions")
    tree.heading("Quirofans", text="Quirofans")
    tree.heading("Personal", text="Personal")
    tree.grid(row=2, column=1, columnspan=3)

    tk.Button(resumPlanta_popUp, text="Revisar", command=lambda: revisarPlanta(connexion, tree, plantaEntry)).grid(row=3, column=2)

#Funció 15: Aqui utilitza les dades de la funció 14 per a fer un informe de la planta especificada
def revisarPlanta(connexion, tree, plantaEntry):
    try:
        for item in tree.get_children():
            tree.delete(item)
        
        cursor = connexion.cursor()
        cursor.execute('''
            SELECT (SELECT COUNT(num_habitacio)
		    FROM habitacio
	    	WHERE num_planta = %s) AS "Habitació", (SELECT COUNT(num_quirofan)
			                                        FROM quirofan
											        WHERE num_planta = %s) AS "Quirofan", (SELECT COUNT(id_inf)
												   						                   FROM infermer
																				           WHERE num_planta = %s) AS "Personal"''', (plantaEntry.get(), plantaEntry.get(), plantaEntry.get()))
        dades = cursor.fetchall()
        cursor.close()

        for fila in dades:
            tree.insert("", "end", values=fila)
    except Exception as e:
        print("ERROR", e)
        connexion.rollback()

#Funció 16: Dona un pop up que conte una taula amb tota la informació d'empleats 
def informePersonal(root, connexion):
    informePersonal_popUp = tk.Toplevel(root)
    informePersonal_popUp.title("Informe sobre el personal actual")
    informePersonal_popUp.geometry("1280x720")

    tree = ttk.Treeview(informePersonal_popUp, columns=("id_emp", "nom", "cognom1", "cognom2", "nif", "email", "telefon", "salari", "data_contractacio", "adreca", "tipus_feina"), show="headings")
    tree.heading("id_emp", text="Id Empleat")
    tree.column("id_emp", width=20)
    tree.heading("nom", text="Nom")
    tree.column("nom", width=40)
    tree.heading("cognom1", text="Cognom 1")
    tree.column("cognom1", width=40)
    tree.heading("cognom2", text="Cognom 2")
    tree.column("cognom2", width=40)
    tree.heading("nif", text="NIF")
    tree.column("nif", width=40)
    tree.heading("email", text="Email")
    tree.column("email", width=150)
    tree.heading("telefon", text="Telefon")
    tree.column("telefon", width=30)
    tree.heading("salari", text="Salari")
    tree.column("salari", width=15)
    tree.heading("data_contractacio", text="Data de contractació")
    tree.column("data_contractacio", width=25)
    tree.heading("adreca", text="Adreça")
    tree.column("adreca", width=70)
    tree.heading("tipus_feina", text="Tipus de feina")
    tree.column("tipus_feina", width=50)
    
    scroll_y = ttk.Scrollbar(informePersonal_popUp, orient="vertical", command=tree.yview)
    scroll_x = ttk.Scrollbar(informePersonal_popUp, orient="horizontal", command=tree.xview)

    tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

    tree.grid(row=1, column=1, columnspan=5, sticky="nsew")
    scroll_y.grid(row=1, column=6, sticky="ns")
    scroll_x.grid(row=2, column=1, columnspan=5, sticky="ew")

    informePersonal_popUp.grid_rowconfigure(1, weight=1)
    informePersonal_popUp.grid_columnconfigure(1, weight=1)

    try:
        for item in tree.get_children():
            tree.delete(item)

        cursor = connexion.cursor()
        cursor.execute('''
            SELECT *
            FROM empleat''')
        dades = cursor.fetchall()
        cursor.close()

        for fila in dades:
            tree.insert("", "end", values=fila)
    except Exception as e:
        print("ERROR", e)
        connexion.rollback()

#Funció 17: Aqui preguntem el dia del que es volen revisar les visites 
def visitesDia(root, connexion):
    visitesDia_popUp = tk.Toplevel(root)
    visitesDia_popUp.title("Revisar visites segons el dia")
    visitesDia_popUp.geometry("450x225")

    tk.Label(visitesDia_popUp, text="Dia de les visites:").grid(row=1, column=1)
    diaVisitaEntry = tk.Entry(visitesDia_popUp, width=10)
    diaVisitaEntry.grid(row=1, column=2)

    tk.Button(visitesDia_popUp, text="Comprovar", command=lambda: comptarVisites(connexion, tree, diaVisitaEntry)).grid(row=1, column=3)

    tree = ttk.Treeview(visitesDia_popUp, columns=("Visites"), show="headings")
    tree.heading("Visites", text="Visites")
    tree.grid(row=2, column=1, columnspan=3)
    
#Funció 18: Aqui utilitzem el dia de la funció 17 per a donar el total de visites d'aquell dia
def comptarVisites(connexion, tree, diaVisitaEntry):    
    try:
        for item in tree.get_children():
            tree.delete(item)

        cursor = connexion.cursor()
        cursor.execute('''
            SELECT COUNT(id_visita) AS "Visites"
            FROM visita
            WHERE data = %s''', (diaVisitaEntry.get(),))
        dades = cursor.fetchall()
        cursor.close()

        for fila in dades:
            tree.insert("", "end", values=fila)
    except Exception as e:
        print("ERROR", e)
        connexion.rollback()

#Funció 19: Amb aquesta funció donarem un dia a la funció 20 
def visitesPlanificadesDia(root, connexion):
    visitesPlanificadesDia_popUp = tk.Toplevel(root)
    visitesPlanificadesDia_popUp.title("Visites planificades per cert dia")

    tk.Label(visitesPlanificadesDia_popUp, text="Dia de les visites:").grid(row=1, column=1)
    dataVisitaEntry = tk.Entry(visitesPlanificadesDia_popUp, width=30)
    dataVisitaEntry.grid(row=1, column=2)

    tk.Button(visitesPlanificadesDia_popUp, text="Veure visites", command=lambda: revisarVisites(tree, dataVisitaEntry, connexion)).grid(row=1, column=3)

    treeFrame = tk.Frame(visitesPlanificadesDia_popUp)
    treeFrame.grid(row=2, column=1, columnspan=5, pady=10)

    scrollbar = tk.Scrollbar(treeFrame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    tree = ttk.Treeview(treeFrame, columns=("id_visita", "descripcio", "hora", "Nom Metge", "Nom Pacient"), show="headings", yscrollcommand=scrollbar.set)
    tree.heading("id_visita", text="Id")
    tree.heading("descripcio", text="Descripció")
    tree.heading("hora", text="Hora")
    tree.heading("Nom Metge", text="Nom Metge")
    tree.heading("Nom Pacient", text="Nom Pacient")
    tree.pack(side=tk.LEFT, fill=tk.BOTH)

    scrollbar.config(command=tree.yview)

#Funció 20: Aquesta funció procesa el dia oferit a la funció 20 i ens dona la informació de les visites d'aquell dia
def revisarVisites(tree, dataVisitaEntry, connexion):
    try:
        for item in tree.get_children():
            tree.delete(item)

        cursor = connexion.cursor()
        cursor.execute('''
            SELECT v.id_visita, v.descripcio, v.hora, e.nom||' '||e.cognom1||' '||e.cognom2 AS "Nom metge", p.nom||' '||p.cognom1||' '||p.cognom2 AS "Nom pacient"
            FROM visita v
            INNER JOIN empleat e ON e.id_emp = v.id_metge
            INNER JOIN pacient p ON p.id_pacient = v.id_pacient
            WHERE v.data = %s
            ORDER BY v.hora DESC''', (dataVisitaEntry.get(),))
        dades = cursor.fetchall()
        cursor.close()

        for fila in dades:
            tree.insert("", "end", values=fila)
    except Exception as e:
        print("ERROR", e)
        connexion.rollback()

#Funció 21: Aqui demanarem el dia per a l'informe de operacions
def diaOperacions(connexion, root):
    diaOperacionsPopUp = tk.Toplevel(root)
    diaOperacionsPopUp.title("Informe d'operacions segons dia")
    diaOperacionsPopUp.geometry("900x450")

    diaOperacionsPopUp.grid_columnconfigure(1, weight=1)
    diaOperacionsPopUp.grid_columnconfigure(2, weight=1)
    diaOperacionsPopUp.grid_columnconfigure(3, weight=0)
    diaOperacionsPopUp.grid_rowconfigure(1, weight=0)
    diaOperacionsPopUp.grid_rowconfigure(2, weight=1)

    tk.Label(diaOperacionsPopUp, text="Dia a revisar: "). grid(row=1, column=1, sticky="w")
    diaOperacionsEntry = tk.Entry(diaOperacionsPopUp, width=30)
    diaOperacionsEntry.grid(row=1, column=2, sticky="ew")

    tk.Button(diaOperacionsPopUp, text="Revisar dia", command=lambda: revisarOperacions(connexion, diaOperacionsEntry, text)).grid(row=1, column=3)

    text = tk.Text(diaOperacionsPopUp, wrap="none")
    text.grid(row=2, column=1, columnspan=3, sticky="nsew")

    scroll_y = ttk.Scrollbar(diaOperacionsPopUp, orient="vertical", command=text.yview)
    scroll_x = ttk.Scrollbar(diaOperacionsPopUp, orient="horizontal", command=text.xview)

    text.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
    scroll_y.grid(row=2, column=3, sticky="ns")
    scroll_x.grid(row=3, column=1, columnspan=2, sticky="ew")

#Funció 22: Aqui ens donara la informació que necesitem de les operacions segons el dia ingresat a la funció 21
def revisarOperacions(connexion, diaOperacionsEntry, text):
    try:
        cursor = connexion.cursor()
        
        #Netejar les notices anteriors
        connexion.notices.clear()

        dia = dt.datetime.strptime(diaOperacionsEntry.get(),"%Y-%m-%d").date()
        #Call a la procedure
        cursor.execute('''
            CALL mostrar_operacions_dia(%s)''', (dia,))

        #Netejar el text de la variable "text"
        text.delete("1.0", "end")

        #Anotar les noticies que va rebent
        for notice in connexion.notices:
            text.insert("end", notice)

        connexion.commit()
        cursor.close()
    except Exception as e:
        print("ERROR", e)
        connexion.rollback()
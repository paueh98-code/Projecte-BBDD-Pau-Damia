import tkinter as tk
import psycopg2 as psy

#Funció 3: Gestiona el tancament de la aplicació. Un cop s'utilitza aquesta funció la base de dades es desconectada de la maquina y la aplicació és tancada.
def tancar(connexion, root):
    if connexion:
        connexion.close()
    root.quit()

#Funció 4: Permet al usuari tancar sessió per a iniciar una nova sessio amb unes altres credencials. També tanca la connexió actual amb la base de dades.
def logout(connexion, mainPage_frame, login_frame):
    if connexion:
        connexion.close()

    mainPage_frame.pack_forget()
    login_frame.pack()

    return None

#Funció 5: Crea la finestra per a inserir empleats a la base de dades (donar d'alta)
def altaEmpleats(root, connexion):
    altaEmpleats_popup = tk.Toplevel(root)
    altaEmpleats_popup.title("Donar d'alta un empleat")
    altaEmpleats_popup.geometry("900x400")

    altaEmpleats_popup.columnconfigure(0, weight=1)
    altaEmpleats_popup.rowconfigure(0, weight=1)

    frame = tk.Frame(altaEmpleats_popup)
    frame.grid(row=0, column=0, sticky="nsew")

    for i in range(1, 7):
        frame.columnconfigure(i, weight=1)

    tk.Label(frame, text="Nom:").grid(row=1, column=1)
    eNameEntry = tk.Entry(frame, width=30)
    eNameEntry.grid(row=1, column=2, sticky="ew", pady= 10, padx= 20)

    tk.Label(frame, text="Primer Cognom:").grid(row=1, column=3)
    eSurname1Entry = tk.Entry(frame, width=30)
    eSurname1Entry.grid(row=1, column=4, sticky="ew", pady= 10, padx= 20)

    tk.Label(frame, text="Segon Cognom:").grid(row=1, column=5)
    eSurname2Entry = tk.Entry(frame, width=30)
    eSurname2Entry.grid(row=1, column=6, sticky="ew", pady= 10, padx= 20)

    tk.Label(frame, text="NIF:").grid(row=2, column=1)
    eNifEntry = tk.Entry(frame, width=30)
    eNifEntry.grid(row=2, column=2, sticky="ew", pady= 10, padx= 20)

    tk.Label(frame, text="Email:").grid(row=2, column=3)
    eEmailEntry = tk.Entry(frame, width=30)
    eEmailEntry.grid(row=2, column=4, sticky="ew", pady= 10, padx= 20)

    tk.Label(frame, text="Telèfon:").grid(row=2, column=5)
    eTelEntry = tk.Entry(frame, width=30)
    eTelEntry.grid(row=2, column=6, sticky="ew", pady= 10, padx= 20)

    tk.Label(frame, text="Salari:").grid(row=3, column=1)
    salEntry = tk.Entry(frame, width=30)
    salEntry.grid(row=3, column=2, sticky="ew", pady= 10, padx= 20)

    tk.Label(frame, text="Adreça:").grid(row=3, column=3)
    eAdrecaEntry = tk.Entry(frame, width=30)
    eAdrecaEntry.grid(row=3, column=4, sticky="ew", pady= 10, padx= 20)

    tk.Label(frame, text="Feina:").grid(row=3, column=5)
    feinaEntry = tk.Entry(frame, width=30)
    feinaEntry.grid(row=3, column=6, sticky="ew", pady= 10, padx= 20)

    tk.Button(frame, text="Enviar", command=lambda: enviarAlta(eNameEntry, eSurname1Entry, eSurname2Entry, eNifEntry, eEmailEntry, eTelEntry, salEntry, eAdrecaEntry, feinaEntry, connexion, root)).grid(row=4, column=1, pady=10, padx=20)
    
    tk.Button(frame, text="Sortir", command=altaEmpleats_popup.destroy).grid(row=4, column=6, pady=10, padx=20)

#Funció 6: Fa el Insert utilitzant les dades del formulari de la funció 4
def enviarAlta(eNameEntry, eSurname1Entry, eSurname2Entry, eNifEntry, eEmailEntry, eTelEntry, salEntry, eAdrecaEntry, feinaEntry, connexion, root): 
    
    try:
        cursor = connexion.cursor()
        cursor.execute('''
            INSERT INTO empleat(nom, cognom1, cognom2, nif, email, telefon, salari, data_contractacio, adreca, tipus_feina)
            VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_DATE, %s, %s)''', (eNameEntry.get(), eSurname1Entry.get(), eSurname2Entry.get(), eNifEntry.get(), eEmailEntry.get(), eTelEntry.get(), int(salEntry.get()), eAdrecaEntry.get(), feinaEntry.get()))
        connexion.commit()
        cursor.close()
    except Exception as e:
        connexion.rollback()
        print("ERROR", e)

#Especificacions dels metges per a la taula metges    
    if feinaEntry.get() == "metge":
        metge_popUp = tk.Toplevel(root)
        metge_popUp.title("Especificacions del metge")
        metge_popUp.geometry("450x200")

        metge_popUp.columnconfigure(0, weight=1)
        metge_popUp.rowconfigure(0, weight=1)

        frame = tk.Frame(metge_popUp)
        frame.grid(row=0, column=0, sticky="nsew")

        for i in range(1, 7):
            frame.columnconfigure(i, weight=1)

        tk.Label(metge_popUp, text="CV:").grid(row=1, column=1)
        mCvEntry = tk.Entry(metge_popUp, width=30)
        mCvEntry.grid(row=1, column=2, sticky="ew")

        tk.Label(metge_popUp, text="Especialitat:").grid(row=2, column=1)
        mEspecialitatEntry = tk.Entry(metge_popUp, width=30)
        mEspecialitatEntry.grid(row=2, column=2, sticky="ew")
        tk.Label(metge_popUp, text="Numero Colegiat:").grid(row=3, column=1)
        numColegiatEntry = tk.Entry(metge_popUp, width=30)
        numColegiatEntry.grid(row=3, column=2, sticky="ew")

        tk.Button(metge_popUp, text="Enviar", command=lambda: enviarMetge(connexion, eNifEntry, mCvEntry, mEspecialitatEntry, numColegiatEntry, metge_popUp)).grid(row=4, column=1)

#Especificacions del infermers/eras per a la taula infermer
    elif feinaEntry.get() == "infermer":
        infermer_popUp = tk.Toplevel(root)
        infermer_popUp.title("Especificacions d'infermer/a")
        infermer_popUp.geometry("450x200")
        
        infermer_popUp.columnconfigure(0, weight=1)
        infermer_popUp.rowconfigure(0, weight=1)

        frame = tk.Frame(infermer_popUp)
        frame.grid(row=0, column=0, sticky="nsew")

        for i in range(1, 7):
            frame.columnconfigure(i, weight=1)

        tk.Label(frame, text="CV:").grid(row=1, column=1)
        iCvEntry = tk.Entry(frame, width=30)
        iCvEntry.grid(row=1, column=2)

        tk.Label(frame, text="Especialitat:").grid(row=1, column=3)
        iEspecialitatEntry = tk.Entry(frame, width=30)
        iEspecialitatEntry.grid(row=1, column=4)

        tk.Label(frame, text="Id metge:").grid(row=2, column=1)
        idMetgeEntry = tk.Entry(frame, width=30)
        idMetgeEntry.grid(row=2, column=2)

        tk.Label(frame, text="Num. Planta:").grid(row=2, column=3)
        numPlantaEntry = tk.Entry(frame, width=30)
        numPlantaEntry.grid(row=2, column=4)

        tk.Button(frame, text="Enviar", command=lambda: enviarDadesInfermer(connexion, eNifEntry, iCvEntry, iEspecialitatEntry, idMetgeEntry, numPlantaEntry, infermer_popUp)).grid(row=3, column=1)


#Funció 7: Envia les dades necesaries per verificar que s'han inserit les dades correctament
def enviarDadesInfermer(connexion, eNifEntry, iCvEntry, iEspecialitatEntry, idMetgeEntry, numPlantaEntry, infermer_popUp):
    idMetgeText = idMetgeEntry.get().strip()
    plantaText = numPlantaEntry.get().strip()

    if bool(idMetgeText) == bool(plantaText):
        print("Nomes pot pertanyer a un metge o a una planta")
        return
    
    if idMetgeText:
        try:
            idMetge = int(idMetgeText)
        except ValueError:
            print("El ID te que ser un numero vàlid")
        planta = None
    else:
        try:
            planta = int(plantaText)
            if planta <= 0:
                print("La planta te que ser major que 0")
                return
        except ValueError:
            print("La planta te que ser un numero vàlid")
            return
        idMetge = None

    enviarInfermer(connexion, eNifEntry, iCvEntry, iEspecialitatEntry, idMetge, planta, infermer_popUp)

#Funció 8: Envia les dades addicionals a la taula metge
def enviarMetge(connexion, eNifEntry, mCvEntry, mEspecialitatEntry, numColegiatEntry, metge_popUp):
    try:
        cursor = connexion.cursor()
        cursor.execute('''
            INSERT INTO metge(id_metge, cv, especialitat, num_colegiat)
            VALUES (fn_get_id_emp(%s), %s, %s, %s)''', (eNifEntry.get(), mCvEntry.get(), mEspecialitatEntry.get(), numColegiatEntry.get()))
        connexion.commit()
        cursor.close()
        metge_popUp.destroy()
    except Exception as e:
        connexion.rollback()
        print("ERROR", e)

#Funció 9: Envia les dades addicionals a la taula infermer    
def enviarInfermer(connexion, eNifEntry, iCvEntry, iEspecialitatEntry, idMetge, planta, infermer_popUp):
    try:
        cursor = connexion.cursor()
        cursor.execute('''
            INSERT INTO infermer(id_inf, cv, especialitat, id_metge, num_planta)
            VALUES (fn_get_id_emp(%s), %s, %s, %s, %s)''', (eNifEntry.get(), iCvEntry.get(), iEspecialitatEntry.get(), idMetge, planta))
        connexion.commit()
        cursor.close()
        infermer_popUp.destroy()
    except Exception as e:
        connexion.rollback()
        print("ERROR", e)
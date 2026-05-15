import os
import psycopg2 as psy
import tkinter as tk
import funcionsHospitalEmpleats as fhe
import funcionsHospitalPacients as fhp
import funcionsHospitalConsultes as fhc
from  DummyData.eliminar_dades import eliminar_dummy_data as ed
from  DummyData.generar_dades import menuDummyData as gdd

#Variable per asegurar una connexio permanent durant tot el ús de la aplicació
connexion = None

#Funció 1:
def submit(usernameEntry, passwordEntry, login_frame, mainPage_frame, errors):
    global connexion
    
    username = usernameEntry.get()
    password = passwordEntry.get()

    try:
        connexion = psy.connect(
        host="192.168.56.107",
        dbname="Hospital Apolo",
        user=username,
        password=password
        )

        login_frame.pack_forget()
        mainPage_frame.pack()

        return connexion
    
    except:
        errors.set("Invalid username or password, try again.")
        return None

#Funció 2:
def logout_wrapper():
    global connexion
    connexion = fhe.logout(connexion, mainPage_frame, login_frame)
    connexion = submit(usernameEntry, passwordEntry, login_frame, mainPage_frame, errors)

#La finestra que utilitzo s'anomena 'root'.
root = tk.Tk()
root.title("Hospital Apol·lo")
root.geometry("1280x720")

#LOGIN FRAME/PAGE: Primera pagina que veura l'usuari. Aqui es un farà login
login_frame = tk.Frame(root)
login_frame.pack()

#Insertar logo...


#Entry on l'usuari escriura el nom del seu usuari de la base de dades.
tk.Label(login_frame, text="Username:").grid(row=1, column=1)
usernameEntry = tk.Entry(login_frame, width=40)
usernameEntry.grid(row=1, column= 2, pady=30)

#Entry on l'usuari escriura la contrasenya del seu usuari.
tk.Label(login_frame, text="Password:").grid(row=2, column=1)
passwordEntry = tk.Entry(login_frame, width=40, show="*")
passwordEntry.grid(row=2, column=2, pady=30)

#Botó que activa la funció 1.
submitButton = tk.Button(login_frame, text="Submit", command=lambda: submit(usernameEntry, passwordEntry, login_frame, mainPage_frame, errors))
submitButton.grid(row=3, column=2, pady=30)

#Aquest label nomes s'utilitza per informar en cas d'error en el process de login al usuari. El missatge surt a l'excepció de la funció 1.
errors= tk.StringVar(root)
tk.Label(login_frame, textvariable=errors).grid(row=4, column=2)

#MAIN FRAME: Un cop registrat l'usuari tindra una serie d'accions i depenent dels seus permisos alguns donaran un missatge d'error si no haurien de poder fer aquella acció.
mainPage_frame = tk.Frame(root)

#El titol de la pàgina principal (Encara esta WIP)
tk.Label(mainPage_frame, text="Pàgina principal Hospital Apol·lo").grid(row=1, column=2, columnspan=2)

#Donar d'alta empleats
tk.Button(mainPage_frame, text="Donar d'alta a empleats", command=lambda: fhe.altaEmpleats(root, connexion)).grid(row=2,column=2)

#Donar d'alta empleats
tk.Button(mainPage_frame, text="Ingresar pacients", command=lambda: fhp.registrarPacients(root, connexion)).grid(row=2,column=3)

#Veure si un infermer te relacio amb una planta o un metge
tk.Button(mainPage_frame, text="Visualitzar relació d'un infermer", command=lambda: fhc.relacioInf(connexion, root)).grid(row=3,column=2)

#Veure dades d'una planta
tk.Button(mainPage_frame, text="Veure dades sobre una planta", command=lambda: fhc.resumPlanta(root, connexion)).grid(row=3, column=3)

#Informe sobre el personal actual del hospital
tk.Button(mainPage_frame, text="Informe de personal", command=lambda: fhc.informePersonal(root, connexion)).grid(row=4, column=2)

#Veure el total de visites que hi han assignades a un dia en especific
tk.Button(mainPage_frame, text="Revisar visites segons dia", command=lambda: fhc.visitesDia(root, connexion)).grid(row=4, column=3)

#Veure dades sobre les visites de un dia en especific
tk.Button(mainPage_frame, text="Planificació de visites actuals", command=lambda: fhc.visitesPlanificadesDia(root, connexion)).grid(row=5, column=2)

#


#Generar dades de probes
tk.Button(mainPage_frame, text="Generar Dummy Data", command=lambda: gdd(root, connexion)).grid(row=6, column=2)

#Eliminar dades
tk.Button(mainPage_frame, text="Eliminar Dades", command=lambda: ed(connexion, root)).grid(row=6, column=3)

#Boto que activa la funció 3
tk.Button(mainPage_frame, text="Logout", command=lambda: logout_wrapper()).grid(row=9, column=2)

#Botó que activa la funció 2
tk.Button(mainPage_frame, text="Close", command=lambda: fhe.tancar(connexion, root)).grid(row=9,column=3)

#Aixo permet que la pàgina es mantingui oberta durant tot el proces
root.mainloop()
#!/usr/bin/env python3

# HOSPITAL APOL·LO - Restauració de backups amb PITR
# Script simple per restaurar l'últim backup físic de PostgreSQL
# Permet recuperar fins a una data/hora o fins a un restore point
# Configurat segons el sistema anterior de backups i alta disponibilitat

import shutil
import subprocess
from datetime import datetime
from pathlib import Path

# Directoris utilitzats en el projecte
DIRECTORI_COPIES = Path("/var/backups/postgresql")
DIRECTORI_DADES = Path("/var/lib/postgresql/18/main")
DIRECTORI_WAL = Path("/var/lib/postgresql/18/wal_archive")
SERVEI_POSTGRES = "postgresql"

print("=" * 60)
print("  HOSPITAL APOL·LO - Restauració PITR")
print("=" * 60)

# Comprovar que existeix el directori de backups
if not DIRECTORI_COPIES.exists():
    print(f"[ERROR] No existeix el directori de backups: {DIRECTORI_COPIES}")
    raise SystemExit(1)

# Comprovar que existeix el directori dels WAL arxivats
if not DIRECTORI_WAL.exists():
    print(f"[ERROR] No existeix el directori WAL: {DIRECTORI_WAL}")
    raise SystemExit(1)

# Buscar l'últim backup local creat pel script de còpies
backups = sorted(
    [copia for copia in DIRECTORI_COPIES.glob("backup_*") if copia.is_dir()],
    key=lambda copia: copia.stat().st_mtime,
    reverse=True,
)

if not backups:
    print(f"[ERROR] No s'ha trobat cap backup local a {DIRECTORI_COPIES}")
    raise SystemExit(1)

backup_seleccionat = backups[0]
linies_pitr = []

print(f"\n[INFO] Backup seleccionat: {backup_seleccionat}")
print(f"[INFO] Directori de dades: {DIRECTORI_DADES}")
print(f"[INFO] Directori WAL: {DIRECTORI_WAL}")

# Menú simple de restauració
print("\nTipus de restauració:")
print("1. Restaurar fins a l'últim WAL disponible")
print("2. Restaurar fins a una data i hora concreta")
print("3. Restaurar fins a un restore point")

opcio = input("Opció [1/2/3]: ").strip()

# Opció 1: no s'afegeix cap recovery_target
if opcio == "1":
    print("[INFO] Es restaurarà fins a l'últim WAL disponible.")

# Opció 2: restauració per hora
elif opcio == "2":
    data_hora = input("Introdueix la data i hora [YYYY-MM-DD HH:MM:SS]: ").strip()

    try:
        datetime.strptime(data_hora, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print("[ERROR] El format de data no és correcte.")
        raise SystemExit(1)

    linies_pitr.append(f"recovery_target_time = '{data_hora}'")
    linies_pitr.append("recovery_target_action = 'pause'")

# Opció 3: restauració per restore point
elif opcio == "3":
    restore_point = input("Introdueix el nom del restore point: ").strip()

    if restore_point == "":
        print("[ERROR] El nom del restore point no pot estar buit.")
        raise SystemExit(1)

    linies_pitr.append(f"recovery_target_name = '{restore_point}'")
    linies_pitr.append("recovery_target_action = 'pause'")

# Control d'opció incorrecta
else:
    print("[ERROR] Opció no vàlida.")
    raise SystemExit(1)

# Confirmació abans de substituir el directori de dades
print("\n[AVÍS] Aquesta operació substituirà el directori actual de dades de PostgreSQL.")
confirmacio = input("Escriu RESTAURAR per continuar: ").strip()

if confirmacio != "RESTAURAR":
    print("[INFO] Restauració cancel·lada.")
    raise SystemExit(0)

try:
    # Aturar PostgreSQL abans de modificar el directori de dades
    print("\n[INFO] Aturant PostgreSQL...")
    subprocess.run(["systemctl", "stop", SERVEI_POSTGRES], check=True)

    # Guardar el directori actual per seguretat
    if DIRECTORI_DADES.exists():
        data_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
        directori_anterior = DIRECTORI_DADES.parent / f"main_abans_restore_{data_actual}"
        print(f"[INFO] Guardant el directori actual a: {directori_anterior}")
        shutil.move(str(DIRECTORI_DADES), str(directori_anterior))

    # Copiar el backup seleccionat com a nou directori de dades
    print("[INFO] Copiant el backup al directori de dades...")
    shutil.copytree(backup_seleccionat, DIRECTORI_DADES)

    # Eliminar fitxers temporals o de mode standby que no s'han de reutilitzar
    fitxers_a_eliminar = ["postmaster.pid", "postmaster.opts", "standby.signal"]

    for nom_fitxer in fitxers_a_eliminar:
        ruta_fitxer = DIRECTORI_DADES / nom_fitxer
        if ruta_fitxer.exists():
            ruta_fitxer.unlink()

    # Crear recovery.signal perquè PostgreSQL faci la recuperació PITR
    print("[INFO] Creant recovery.signal...")
    (DIRECTORI_DADES / "recovery.signal").touch()

    # Afegir la configuració de recuperació a postgresql.auto.conf
    print("[INFO] Configurant restore_command i objectiu de recuperació...")

    with open(DIRECTORI_DADES / "postgresql.auto.conf", "a", encoding="utf-8") as fitxer:
        fitxer.write("\n# Configuració afegida pel script de restauració PITR\n")
        fitxer.write(f"restore_command = 'cp {DIRECTORI_WAL}/%f %p'\n")
        fitxer.write("recovery_target_timeline = 'latest'\n")

        for linia in linies_pitr:
            fitxer.write(linia + "\n")

    # Corregir propietari i permisos del directori restaurat
    print("[INFO] Ajustant permisos...")
    subprocess.run(["chown", "-R", "postgres:postgres", str(DIRECTORI_DADES)], check=True)
    subprocess.run(["chmod", "700", str(DIRECTORI_DADES)], check=True)

    # Iniciar PostgreSQL perquè comenci la recuperació
    print("[INFO] Iniciant PostgreSQL...")
    subprocess.run(["systemctl", "start", SERVEI_POSTGRES], check=True)

except subprocess.CalledProcessError:
    print("[ERROR] Ha fallat una comanda del sistema.")
    raise SystemExit(1)

except Exception as error:
    print(f"[ERROR] Restauració interrompuda: {error}")
    raise SystemExit(1)

print("\n[OK] Restauració iniciada correctament.")
print("\nComprovacions recomanades:")
print("sudo systemctl status postgresql")
print("sudo -u postgres psql -c \"SELECT pg_is_in_recovery();\"")

# Si s'ha restaurat per hora o restore point, PostgreSQL quedarà pausat
if linies_pitr:
    print("\nQuan comprovis que les dades són correctes, reprèn la recuperació amb:")
    print("sudo -u postgres psql -c \"SELECT pg_wal_replay_resume();\"")

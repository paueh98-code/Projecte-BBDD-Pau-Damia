#!/usr/bin/env python3

import shutil
import subprocess
from datetime import datetime
from pathlib import Path


# Configuració del projecte Hospital Apol·lo
DIRECTORI_COPIES = Path("/var/backups/postgresql")
DIRECTORI_DADES = Path("/var/lib/postgresql/18/main")
DIRECTORI_WAL = Path("/var/lib/postgresql/18/wal_archive")
SERVEI_POSTGRESQL = "postgresql"

# Buscar l'últim backup físic creat amb pg_basebackup
copies = sorted(
    [copia for copia in DIRECTORI_COPIES.glob("backup_*") if copia.is_dir()],
    key=lambda copia: copia.stat().st_mtime,
    reverse=True
)

print("=" * 55)
print("  HOSPITAL APOL·LO - Restauració PITR")
print("=" * 55)

if not copies:
    print("[ERROR] No s'ha trobat cap backup a /var/backups/postgresql")
    raise SystemExit(1)

backup_seleccionat = copies[0]

print(f"\n[INFO] Backup seleccionat: {backup_seleccionat}")
print(f"[INFO] Directori de dades: {DIRECTORI_DADES}")
print(f"[INFO] Directori WAL: {DIRECTORI_WAL}")

if not DIRECTORI_WAL.exists():
    print(f"[ERROR] No existeix el directori WAL: {DIRECTORI_WAL}")
    raise SystemExit(1)

# Menú de restauració PITR
print("\nTipus de restauració:")
print("1. Restaurar fins a una data i hora concreta")
print("2. Restaurar fins a un restore point")

opcio = input("Opció [1/2]: ").strip()
linies_pitr = []

# Recuperació fins a una data i hora concreta
if opcio == "1":
    data_objectiu = input("Data i hora objectiu [YYYY-MM-DD HH:MM:SS]: ").strip()

    try:
        datetime.strptime(data_objectiu, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print("[ERROR] Format de data incorrecte")
        raise SystemExit(1)

    linies_pitr.append(f"recovery_target_time = '{data_objectiu}'")

# Recuperació fins a un restore point
elif opcio == "2":
    nom_restore_point = input("Nom del restore point: ").strip()

    if not nom_restore_point:
        print("[ERROR] El nom del restore point no pot estar buit")
        raise SystemExit(1)

    linies_pitr.append(f"recovery_target_name = '{nom_restore_point}'")

else:
    print("[ERROR] Opció no vàlida")
    raise SystemExit(1)

# Amb promote PostgreSQL acaba la recuperació automàticament
linies_pitr.append("recovery_target_action = 'promote'")

# Confirmació abans de substituir el directori de dades
print("\n[ATENCIÓ] Aquesta operació substituirà el directori de dades actual de PostgreSQL.")
confirmacio = input("Escriu RESTAURAR per continuar: ").strip()

if confirmacio != "RESTAURAR":
    print("[INFO] Restauració cancel·lada")
    raise SystemExit(0)

# Aturar PostgreSQL abans de tocar el directori de dades
print("\n[INFO] Aturant PostgreSQL...")
subprocess.run(["systemctl", "stop", SERVEI_POSTGRESQL], check=True)

# Guardar el directori de dades actual abans de reemplaçar-lo
if DIRECTORI_DADES.exists():
    marca_temps = datetime.now().strftime("%Y%m%d_%H%M%S")
    directori_anterior = DIRECTORI_COPIES / f"dades_abans_restauracio_{marca_temps}"
    print(f"[INFO] Movent dades actuals a: {directori_anterior}")
    shutil.move(str(DIRECTORI_DADES), str(directori_anterior))

# Restaurar el backup físic al directori de dades de PostgreSQL
print("[INFO] Copiant el backup al directori de dades...")
shutil.copytree(backup_seleccionat, DIRECTORI_DADES)

# Eliminar standby.signal si existís per evitar que arrenqui com a standby
fitxer_standby = DIRECTORI_DADES / "standby.signal"
if fitxer_standby.exists():
    fitxer_standby.unlink()

# Crear recovery.signal perquè PostgreSQL entri en mode recuperació
print("[INFO] Creant recovery.signal...")
(DIRECTORI_DADES / "recovery.signal").touch()

# Afegir la configuració PITR a postgresql.auto.conf
print("[INFO] Configurant restore_command i objectiu de recuperació...")
fitxer_auto_conf = DIRECTORI_DADES / "postgresql.auto.conf"

with fitxer_auto_conf.open("a", encoding="utf-8") as fitxer:
    fitxer.write("\n# Configuració afegida pel script de restauració PITR\n")
    fitxer.write(f"restore_command = 'cp {DIRECTORI_WAL}/%f %p'\n")

    for linia in linies_pitr:
        fitxer.write(linia + "\n")

# Ajustar propietari i permisos del directori restaurat
print("[INFO] Ajustant permisos...")
subprocess.run(["chown", "-R", "postgres:postgres", str(DIRECTORI_DADES)], check=True)
subprocess.run(["chmod", "700", str(DIRECTORI_DADES)], check=True)

# Arrencar PostgreSQL per iniciar i finalitzar la recuperació PITR
print("[INFO] Arrencant PostgreSQL...")
subprocess.run(["systemctl", "start", SERVEI_POSTGRESQL], check=True)

print("\n[OK] Restauració PITR executada")
print("[INFO] PostgreSQL finalitzarà la recuperació automàticament amb recovery_target_action = 'promote'")

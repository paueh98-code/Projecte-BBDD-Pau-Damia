import subprocess
from datetime import datetime
from pathlib import Path
import shutil
import tarfile


# Configuració
DIRECTORI_COPIES = Path("/var/backups/postgresql")
MAX_COPIES = 5

HOST_POSTGRES = "192.168.56.110"
PORT_POSTGRES = "5432"
USUARI_REPLICACIO = "replicator"

DESTI_NUVOL = "onedrive_apolo:backups_postgresql"

DIRECTORI_COPIES.mkdir(parents=True, exist_ok=True)

data_actual = datetime.now().strftime("%Y%m%d_%H%M")
desti_copia = DIRECTORI_COPIES / f"backup_{data_actual}"
fitxer_comprimit = DIRECTORI_COPIES / f"{desti_copia.name}.tar.gz"

# Crear còpia base de PostgreSQL
ordre_copia = [
    "pg_basebackup",
    "-D", str(desti_copia),
    "-Fp",
    "-X", "fetch",
    "-P",
    "-U", USUARI_REPLICACIO,
    "-h", HOST_POSTGRES,
    "-p", PORT_POSTGRES
]

print("[INFO] Iniciant pg_basebackup...")

try:
    subprocess.run(ordre_copia, check=True)
    print(f"[OK] Còpia creada a: {desti_copia}")
except subprocess.CalledProcessError:
    print("[ERROR] Error durant la còpia de seguretat")
    raise SystemExit(1)

# Comprimir la còpia abans de pujar-la al núvol
print(f"[INFO] Comprimint la còpia: {fitxer_comprimit}")

try:
    with tarfile.open(fitxer_comprimit, "w:gz") as tar:
        tar.add(desti_copia, arcname=desti_copia.name)
    print("[OK] Còpia comprimida correctament")
except Exception as error:
    print(f"[ERROR] No s'ha pogut comprimir la còpia: {error}")
    raise SystemExit(1)

# Pujar el fitxer comprimit al núvol amb rclone
print("[INFO] Pujant la còpia comprimida al núvol...")

try:
    subprocess.run(
        ["rclone", "copy", str(fitxer_comprimit), DESTI_NUVOL, "-P"],
        check=True
    )
    print("[OK] Còpia pujada correctament al núvol")
except FileNotFoundError:
    print("[ERROR] No s'ha trobat la comanda rclone")
except subprocess.CalledProcessError:
    print("[ERROR] No s'ha pogut pujar la còpia al núvol")

# Eliminar el fitxer comprimit local per no ocupar espai doble
try:
    if fitxer_comprimit.exists():
        fitxer_comprimit.unlink()
        print("[INFO] Fitxer comprimit local eliminat")
except Exception as error:
    print(f"[ERROR] No s'ha pogut eliminar el fitxer comprimit local: {error}")

# Retenció local: mantenir només les 5 còpies més recents
print("[INFO] Aplicant política de retenció local...")

copies = sorted(
    [copia for copia in DIRECTORI_COPIES.glob("backup_*") if copia.is_dir()],
    key=lambda copia: copia.stat().st_mtime,
    reverse=True
)

for copia_antiga in copies[MAX_COPIES:]:
    try:
        print(f"[INFO] Eliminant còpia antiga: {copia_antiga.name}")
        shutil.rmtree(copia_antiga)
    except Exception as error:
        print(f"[ERROR] No s'ha pogut eliminar {copia_antiga.name}: {error}")

print("[OK] Backup finalitzat")

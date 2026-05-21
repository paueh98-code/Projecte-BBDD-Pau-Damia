

# Hospital Apol·lo - Esquema d'Alta Disponibilitat

Projecte d'alta disponibilitat per al sistema de gestió de l'Hospital Apol·lo, basat en PostgreSQL amb replicació actiu-passiu, còpies de seguretat automatitzades i recuperació Point-In-Time Recovery (PITR).

> **Nota de seguretat:** en aquest README les contrasenyes s'han substituït per `<PASSWORD>` per evitar publicar credencials al repositori. En un entorn real, no utilitzeu autenticació `trust`; feu servir `scram-sha-256`, certificats o un altre mecanisme segur.

## Índex

- [1. Infraestructura de hardware](#1-infraestructura-de-hardware)
  - [1.1 Objectiu](#11-objectiu)
  - [1.2 Dimensions del sistema](#12-dimensions-del-sistema)
  - [1.3 Estructura proposada](#13-estructura-proposada)
- [2. Estructura de replicació](#2-estructura-de-replicació)
  - [2.1 Objectiu](#21-objectiu)
  - [2.2 Configuració del node primari](#22-configuració-del-node-primari)
  - [2.3 Configuració del node secundari](#23-configuració-del-node-secundari-standby)
  - [2.4 Verificació](#24-verificació)
  - [2.5 Sistema de failover](#25-sistema-de-failover)
- [3. Configuració de còpies de seguretat](#3-configuració-de-còpies-de-seguretat)
  - [3.1 Objectiu](#31-objectiu)
  - [3.2 Configuració prèvia](#32-configuració-prèvia)
  - [3.3 Configuració del crontab](#33-configuració-del-crontab)
- [4. Recuperació de còpies de seguretat](#4-recuperació-de-còpies-de-seguretat)
  - [4.1 Objectiu](#41-objectiu)
  - [4.2 Passos](#42-passos)

## Dades de l'entorn

| Element | Valor |
|---|---|
| Sistema operatiu | Ubuntu Server 24.04 LTS |
| SGBD | PostgreSQL 18 |
| Node primari | `192.168.56.110` |
| Node standby | `192.168.56.111` |
| Usuari de replicació | `replicator` |
| Mode de replicació | Actiu-passiu amb Streaming Replication |
| Sistema de recuperació | PITR amb arxivat WAL |

---

# 1. Infraestructura de hardware

## 1.1 Objectiu

Garantir la disponibilitat 24x7 del sistema de gestió de l'Hospital de Blanes, amb tolerància a fallades, capacitat d'escalabilitat i rendiment òptim.

Per això es proposa una infraestructura basada en dos nodes de base de dades replicats en mode actiu-passiu.

## 1.2 Dimensions del sistema

La infraestructura s'ha dissenyat per suportar la càrrega prevista de l'hospital:

- 50.000 pacients registrats.
- 100.000 visites mèdiques.
- 100 metges.
- 200 infermers.
- 100 persones de neteja.
- 50 administratius.
- Total aproximat: 450 empleats.
- Operacions quirúrgiques, ingressos, receptes i diagnòstics associats.
- Múltiples usuaris concurrents: personal mèdic, administratiu i directiu.

Amb aquest volum de dades, s'estima una base de dades d'uns **2-4 GB en disc**, amb pics de **20-30 connexions simultànies**.

El hardware proposat cobreix aquesta necessitat i deixa marge per al creixement futur de l'hospital.

## 1.3 Estructura proposada

La solució consta de dos nodes PostgreSQL en configuració actiu-passiu amb **Streaming Replication**.

## 1.3.1 Servidor principal

| Component | Detalls tècnics | Preu aprox. |
|---|---|---:|
| CPU | 4 cores / 8 threads, Intel Xeon E-2314 o similar | 180 € |
| Memòria RAM | 32 GB DDR4 ECC 3200 MHz | 120 € |
| Disc sistema | 1 x 500 GB SSD SATA, SO + PostgreSQL | 50 € |
| Disc dades | 2 x 1 TB NVMe SSD, RAID 1 per dades BD | 180 € |
| Disc backups | 1 x 2 TB HDD SATA, còpies locals | 60 € |
| Sistema operatiu | Ubuntu Server 24.04 LTS | 0 € |
| SGBD | PostgreSQL 18 | 0 € |
| **Total** |  | **~590 €** |

### Justificació

El node primari gestiona totes les operacions de lectura i escriptura de la base de dades. Amb 50.000 pacients i 100.000 visites, cal garantir un rendiment òptim en I/O.

Els 32 GB de RAM permeten que PostgreSQL mantingui un `shared_buffers` gran, amb 8 GB recomanats, i que pugui cachejar les consultes més freqüents.

Els dos discos NVMe en RAID 1 asseguren velocitat i redundància per a les dades. El disc HDD addicional serveix per guardar les 5 còpies de seguretat locals. La memòria ECC ajuda a prevenir errors de bit que podrien corrompre dades clíniques sensibles.

## 1.3.2 Servidor standby

| Component | Detalls tècnics | Preu aprox. |
|---|---|---:|
| CPU | 4 cores / 8 threads, Intel Xeon E-2314 o similar | 180 € |
| Memòria RAM | 32 GB DDR4 ECC 3200 MHz | 120 € |
| Disc sistema | 1 x 500 GB SSD SATA, SO + PostgreSQL | 50 € |
| Disc dades | 2 x 1 TB NVMe SSD, RAID 1 per dades BD | 180 € |
| Sistema operatiu | Ubuntu Server 24.04 LTS | 0 € |
| SGBD | PostgreSQL 18 amb `hot_standby` activat | 0 € |
| **Total** |  | **~560 €** |

### Justificació

El node secundari funciona com a **hot standby**: manté una còpia actualitzada del node principal mitjançant Streaming Replication i està preparat per entrar en funcionament immediat si el primari falla.

Tot i que no rep escriptures en temps normal, permet consultes de només lectura, útils per a informes i dashboards com Power BI. Això garanteix la continuïtat del servei en cas de desastre.

---

# 2. Estructura de replicació

## 2.1 Objectiu

Mitjançant un sistema de rèplica actiu-passiu, el node primari transmet els canvis en temps real a un node standby. D'aquesta manera es garanteix una recuperació ràpida davant caigudes de servei i es facilita el manteniment dels servidors sense aturades.

## 2.2 Configuració del node primari

Editem l'arxiu `postgresql.conf`:

```bash
sudo nano /etc/postgresql/18/main/postgresql.conf
```

Afegim o modifiquem els valors següents:

```conf
# Write-Ahead Log
wal_level = replica

# Replication
max_wal_senders = 10
max_replication_slots = 10
wal_keep_size = 512MB
max_slot_wal_keep_size = -1
idle_replication_slot_timeout = 0

# Hot standby
hot_standby = on

# Archiving
archive_mode = on
archive_library = ''
archive_command = 'cp %p /var/lib/postgresql/18/wal_archive/%f'
```

Explicació dels paràmetres principals:

- `wal_level = replica`: permet generar WALs aptes per a rèplica.
- `max_wal_senders`: determina quants standbys es poden connectar.
- `wal_keep_size`: manté fitxers WAL durant prou temps per evitar errors de recuperació.
- `archive_mode` i `archive_command`: permeten fer backups consistents i mantenir l'arxivat continu.

Creem el directori d'arxivat WAL:

```bash
sudo mkdir -p /var/lib/postgresql/18/wal_archive
sudo chown postgres:postgres /var/lib/postgresql/18/wal_archive
```

Editem `pg_hba.conf` i afegim la connexió de replicació:

```bash
sudo nano /etc/postgresql/18/main/pg_hba.conf
```

```conf
host    replication    replicator    192.168.56.111/32    trust
```

Creem l'usuari de replicació:

```bash
sudo -u postgres psql
```

```sql
CREATE USER replicator WITH REPLICATION LOGIN ENCRYPTED PASSWORD '<PASSWORD>';
\q
```

Reiniciem PostgreSQL:

```bash
sudo systemctl restart postgresql
```

## 2.3 Configuració del node secundari standby

Primer aturem PostgreSQL i eliminem les dades actuals del node standby:

```bash
sudo systemctl stop postgresql
sudo find /var/lib/postgresql/18/main -mindepth 1 -delete
```

Fem la còpia de les dades del node primari amb `pg_basebackup`:

```bash
sudo -iu postgres
pg_basebackup -h 192.168.56.110 -D /var/lib/postgresql/18/main -U replicator -Fp -Xs -P -R
```

Creem el fitxer `.pgpass` per evitar haver d'introduir la contrasenya manualment:

```bash
echo "192.168.56.110:5432:*:replicator:<PASSWORD>" > ~/.pgpass
chmod 600 ~/.pgpass
```

Al node secundari, revisem o afegim la configuració següent:

```bash
sudo nano /etc/postgresql/18/main/postgresql.conf
```

```conf
primary_conninfo = 'host=192.168.56.110 port=5432 user=replicator password=<PASSWORD>'
primary_slot_name = ''
hot_standby = on
```

Finalment, establim permisos i iniciem PostgreSQL:

```bash
sudo chown -R postgres:postgres /var/lib/postgresql/18/main
sudo chmod 700 /var/lib/postgresql/18/main
sudo systemctl start postgresql
```

## 2.4 Verificació

Al node secundari:

```bash
sudo -u postgres psql -c "SELECT pg_is_in_recovery();"
```

El resultat esperat és:

```text
 pg_is_in_recovery
-------------------
 t
```

Al node primari:

```bash
sudo -u postgres psql -c "SELECT client_addr, state, sync_state FROM pg_stat_replication;"
```

Resultat esperat:

```text
 client_addr    |   state   | sync_state
----------------+-----------+------------
 192.168.56.111 | streaming | async
```

## 2.5 Sistema de failover

S'ha implementat un sistema de failover automàtic mitjançant un script Bash executat periòdicament amb cron.

Al node standby, creem l'script:

```bash
sudo nano /usr/local/bin/failover_check.sh
```

```bash
#!/bin/bash

PRIMARY_IP="192.168.56.110"

if ! pg_isready -h "$PRIMARY_IP" -p 5432 -q; then
    echo "[FAILOVER] $(date): Master off. Standby promocionat." >> /var/log/failover.log
    sudo -u postgres pg_ctlcluster 18 main promote
else
    echo "[OK] $(date): Master on." >> /var/log/failover.log
fi
```

Donem permisos d'execució:

```bash
sudo chmod +x /usr/local/bin/failover_check.sh
```

Configurem el cron:

```bash
sudo crontab -e
```

```cron
* * * * * /usr/local/bin/failover_check.sh
```

Així es comprova cada minut si el servidor primari està funcionant. Si no ho està, el servidor standby es promociona a primari.

---

# 3. Configuració de còpies de seguretat

## 3.1 Objectiu

Configurar un sistema de còpies de seguretat físiques amb `pg_basebackup`, seguint l'enfocament d'arxivat continu i restauració Point-In-Time Recovery, utilitzant un script automatitzat en Python.

## 3.2 Configuració prèvia

S'utilitza la mateixa configuració d'arxivat continu aplicada a la replicació, però s'afegeix al fitxer `pg_hba.conf`:

```conf
host    replication    replicator    192.168.56.110/32    trust
```

Creem el directori de backups:

```bash
sudo mkdir -p /var/backups/postgresql
sudo chown -R postgres:postgres /var/backups/postgresql
sudo chmod 700 /var/backups/postgresql
```

Afegim l'script de creació de backups:

[backup_postgres_rclone_comprimido.py](https://github.com/paueh98-code/Projecte-BBDD-Pau-Damia/blob/main/Alta_Disponibilitat/backup_postgres_rclone_comprimido.py)

Aquest script crea una còpia a:

```text
/var/backups/postgresql
```

Es mantenen com a màxim cinc còpies locals i també es puja una còpia comprimida a OneDrive utilitzant `rclone`.

Igual que al standby, al node principal creem un fitxer `.pgpass` perquè no demani la contrasenya:

```bash
sudo -u postgres -H nano /var/lib/postgresql/.pgpass
```

Contingut del fitxer:

```text
192.168.56.110:5432:*:replicator:<PASSWORD>
```

Assignem propietari i permisos:

```bash
sudo chown postgres:postgres /var/lib/postgresql/.pgpass
sudo chmod 600 /var/lib/postgresql/.pgpass
```

## 3.3 Configuració del crontab

Editem el crontab de l'usuari `postgres`:

```bash
sudo crontab -u postgres -e
```

Afegim `HOME` i `PATH` per assegurar que trobi els fitxers de configuració de `rclone` i utilitzi com a carpeta principal la de `postgres`:

```cron
HOME=/var/lib/postgresql
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

0 2 * * * /usr/bin/python3 /usr/local/sbin/backup_postgres_rclone.py >> /var/log/backup_postgres.log 2>&1
```

La còpia de seguretat s'executarà cada dia a les 02:00.

Creem el fitxer de logs i assignem permisos:

```bash
sudo touch /var/log/backup_postgres.log
sudo chown postgres:postgres /var/log/backup_postgres.log
sudo chmod 640 /var/log/backup_postgres.log
```

---

# 4. Recuperació de còpies de seguretat

## 4.1 Objectiu

Restaurar PostgreSQL des d'un backup físic fet amb `pg_basebackup`, amb suport per a recuperació **Point-In-Time Recovery** tant per hora concreta com per `restore point`.

## 4.2 Passos

Creem una taula per fer la prova de restauració:

```bash
sudo -u postgres psql -d hospitalapolo -c "CREATE TABLE prova(id INT PRIMARY KEY, text_prova TEXT);"
sudo -u postgres psql -d hospitalapolo -c "INSERT INTO prova VALUES (1, 'Aixo es una prova');"
sudo -u postgres psql -d hospitalapolo -c "SELECT * FROM prova;"
```

Resultat esperat:

```text
 id |    text_prova
----+------------------
  1 | Aixo es una prova
```

Creem la còpia de seguretat amb l'script de backups:

```bash
sudo -u postgres -H python3 /usr/local/sbin/backup_postgres_rclone.py
```

Creem un punt de recuperació:

```bash
sudo -u postgres psql -d hospitalapolo -c "SELECT pg_create_restore_point('punt_prova');"
```

Eliminem la taula:

```bash
sudo -u postgres psql -d hospitalapolo -c "DROP TABLE prova CASCADE;"
sudo -u postgres psql -d hospitalapolo -c "SELECT * FROM prova;"
```

El resultat esperat és un error indicant que la relació `prova` no existeix:

```text
ERROR: relation "prova" does not exist
```

Com que és una prova, forcem l'arxivat del WAL per evitar problemes en la recuperació al `recovery_point`:

```bash
sudo -u postgres psql -c "SELECT pg_switch_wal();"
```

Executem l'script de restauració:

```bash
sudo -u postgres -H python3 /usr/local/sbin/restaurar_backup_pitr_directo.py
```

L'script permet restaurar de dues maneres:

1. Restaurar fins a una data i hora concreta.
2. Restaurar fins a un `restore point`, per exemple `punt_prova`.

Després de la restauració, comprovem que la taula s'ha recuperat correctament:

```bash
sudo -u postgres psql -d hospitalapolo -c "SELECT * FROM prova;"
```

Resultat esperat:

```text
 id |    text_prova
----+------------------
  1 | Aixo es una prova
```

L'script de restauració s'encarrega d'aturar i arrencar PostgreSQL automàticament:

```python
# Aturar PostgreSQL abans de modificar el directori de dades
print("\n[INFO] Aturant PostgreSQL...")
subprocess.run(["systemctl", "stop", SERVEI_POSTGRESQL], check=True)

# Arrencar PostgreSQL per iniciar la recuperació PITR
print("[INFO] Arrencant PostgreSQL...")
subprocess.run(["systemctl", "start", SERVEI_POSTGRESQL], check=True)
```

---

## Resum final

Aquest esquema permet:

- Alta disponibilitat amb dos nodes PostgreSQL.
- Replicació actiu-passiu amb Streaming Replication.
- Consultes de només lectura al node standby.
- Failover automàtic mitjançant Bash i cron.
- Còpies físiques amb `pg_basebackup`.
- Retenció local de fins a cinc còpies.
- Pujada de backups comprimits a OneDrive amb `rclone`.
- Recuperació PITR per data/hora o per `restore point`.


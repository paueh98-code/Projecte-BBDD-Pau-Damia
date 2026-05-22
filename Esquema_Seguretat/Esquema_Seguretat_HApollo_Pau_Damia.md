# Esquema de seguretat

**Autors:** Pau Encinas, Damià Méndez  
**Projecte:** Hospital Apol·lo  
**Cicle:** ASIX 1

---

## Índex

1. [Matriu de seguretat](#1-matriu-de-seguretat)
2. [Data masking](#2-data-masking)
3. [Protecció de dades](#3-protecció-de-dades)
4. [Configuració SSL](#4-configuració-ssl)
   - [4.1 Creació de certificats i configuració PostgreSQL](#41-creació-de-certificats-i-configuració-postgresql)
   - [4.2 Configuració Standby](#42-configuració-standby)
   - [4.3 Renovació automàtica](#43-renovació-automàtica)
   - [4.4 Configuració client](#44-configuració-client)

---

## 1. Matriu de seguretat

Hem creat 5 rols per als usuaris de la base de dades:

- **Sysadmin:** l'administrador de la base de dades amb tots els permisos.
- **Directius:** per al personal de direcció. Poden consultar les taules per fer estadístiques i afegir nous empleats i material nou, com aparells i medicaments.
- **Metges:** consulten i gestionen totes les taules relacionades amb l'atenció als pacients.
- **Infermers:** poden consultar les taules per fer tractaments a l'hospital però no poden fer modificacions.
- **Administratius:** tasques de gestió com altes i baixes de pacients i empleats, i programació de visites, ingressos i operacions.

Script de creació de rols:

[hospital_apolo_rols.sql](https://github.com/paueh98-code/Projecte-BBDD-Pau-Damia/blob/main/Esquema_Seguretat/hospital_apolo_rols.sql)

---

## 2. Data masking

Per fer el **data masking** hem creat una vista amb l'emmascarament de les dades i l'hem aplicat als usuaris.

Script per a la creació de la vista amb data masking:

[data_masking_apolo.sql](https://github.com/paueh98-code/Projecte-BBDD-Pau-Damia/blob/main/Esquema_Seguretat/data_masking_apolo.sql)

---

## 3. Protecció de dades

La següent taula identifica totes les dades personals tractades pel sistema, el seu nivell de protecció i la mesura aplicada:

| Camp / Dada | Descripció | Nivell | Categoria | Mesura aplicada |
|---|---|---|---|---|
| `pacient.nif` | NIF/DNI del pacient | Alt | Identificatiu | Data masking (esquema `mask`) |
| `pacient.targeta_sanitaria` | Codi CIP / targeta sanitària | Alt | Sanitari | Data masking (esquema `mask`) |
| `pacient.adreca` | Adreça postal | Mig | Identificatiu | Data masking (esquema `mask`) |
| `pacient.telefon` | Telèfon de contacte | Mig | Identificatiu | Data masking (esquema `mask`) |
| `pacient.email` | Correu electrònic | Mig | Identificatiu | Data masking (esquema `mask`) |
| `empleat.nif` | NIF/DNI de l'empleat | Alt | Identificatiu | Data masking (esquema `mask`) |
| `empleat.adreca / telefon / email` | Dades de contacte de l'empleat | Mig | Identificatiu | Data masking (esquema `mask`) |
| `visita.descripcio` | Descripció clínica de la visita | Alt | Salut | Truncada per rols no clínics |
| `diagnostic.descripcio` | Diagnòstic mèdic | Alt | Salut | Accés restringit a metges |
| `linia_recepta` (`pauta`, `dosi`) | Prescripció farmacològica | Alt | Salut | Emmascarada per directius i administratius |
| `operacio.descripcio` | Descripció de l'operació | Alt | Salut | Truncada per directius i administratius |

---

## 4. Configuració SSL

### 4.1 Creació de certificats i configuració PostgreSQL

Primer entrem al directori principal de configuració de PostgreSQL:

```bash
cd /etc/postgresql/18/main
```

Generem la clau privada de la CA:

```bash
sudo openssl genrsa -out ca.key 4096
```

Creem el certificat de la CA:

```bash
sudo openssl req -x509 -new -nodes \
  -key ca.key \
  -sha256 \
  -days 3650 \
  -out ca.crt \
  -subj "/CN=HospitalApoloCA"
```

Generem la clau privada del servidor primari:

```bash
sudo openssl genrsa -out server.key 2048
```

Creem la petició de certificat del servidor:

```bash
sudo openssl req -new \
  -key server.key \
  -out server.csr \
  -subj "/CN=pg-primary"
```

Signem el certificat del servidor amb la CA:

```bash
sudo openssl x509 -req \
  -in server.csr \
  -CA ca.crt \
  -CAkey ca.key \
  -CAcreateserial \
  -out server.crt \
  -days 365 \
  -sha256
```

Copiem la CA com a certificat arrel:

```bash
sudo cp ca.crt root.crt
```

Assignem propietari i permisos als certificats:

```bash
sudo chown postgres:postgres server.key server.crt root.crt
sudo chmod 400 server.key
sudo chmod 644 server.crt root.crt
```

Editem el fitxer de configuració de PostgreSQL:

```bash
sudo nano /etc/postgresql/18/main/postgresql.conf
```

Afegim o modifiquem els següents valors:

```conf
# SSL
ssl = on
ssl_ca_file = '/etc/postgresql/18/main/root.crt'
ssl_cert_file = '/etc/postgresql/18/main/server.crt'
#ssl_crl_file = ''
#ssl_crl_dir = ''
ssl_key_file = '/etc/postgresql/18/main/server.key'
```

Després editem el fitxer `pg_hba.conf`:

```bash
sudo nano /etc/postgresql/18/main/pg_hba.conf
```

Afegim les connexions SSL:

```conf
hostssl all         all        192.168.56.0/24     scram-sha-256
hostssl replication replicator 192.168.56.111/32   scram-sha-256
hostssl replication replicator 192.168.56.110/32   scram-sha-256
```

Reiniciem PostgreSQL perquè apliqui els canvis:

```bash
sudo systemctl restart postgresql
```

---

### 4.2 Configuració Standby

Generem els certificats per al servidor **standby**, els passem al servidor standby i apliquem la mateixa configuració.

Generem la clau privada del standby:

```bash
sudo openssl genrsa -out standby.key 2048
```

Creem la petició de certificat:

```bash
sudo openssl req -new \
  -key standby.key \
  -out standby.csr \
  -subj "/CN=pg-standby"
```

Signem el certificat del standby amb la CA:

```bash
sudo openssl x509 -req \
  -in standby.csr \
  -CA ca.crt \
  -CAkey ca.key \
  -CAcreateserial \
  -out standby.crt \
  -days 365 \
  -sha256
```

Al servidor standby, establim els permisos:

```bash
sudo chmod 400 /etc/postgresql/18/main/standby.key
sudo chmod 644 /etc/postgresql/18/main/standby.crt
sudo chmod 644 /etc/postgresql/18/main/root.crt
```

Configurem SSL al `postgresql.conf` del servidor standby:

```conf
# SSL
ssl = on
ssl_ca_file = '/etc/postgresql/18/main/root.crt'
ssl_cert_file = '/etc/postgresql/18/main/standby.crt'
#ssl_crl_file = ''
#ssl_crl_dir = ''
ssl_key_file = '/etc/postgresql/18/main/standby.key'
```

Al `pg_hba.conf` del servidor standby afegim:

```conf
hostssl all all 192.168.56.0/24 scram-sha-256
```

---

### 4.3 Renovació automàtica

Utilitzarem el següent script per renovar els certificats automàticament:

```bash
sudo nano /usr/local/sbin/renovar_ssl_postgres.sh
```

Contingut del script:

```bash
#!/bin/bash

# Seleccionem el directori on tenim els certificats
cd /etc/postgresql/18/main

# Generem nova clau privada del servidor
openssl genrsa -out server.key 2048

# Creem nova petició de certificat
openssl req -new \
  -key server.key \
  -out server.csr \
  -subj "/CN=pg-primary"

# Signem el certificat amb la CA
openssl x509 -req \
  -in server.csr \
  -CA ca.crt \
  -CAkey ca.key \
  -CAcreateserial \
  -out server.crt \
  -days 365 \
  -sha256

# Copiar la CA com a root
cp ca.crt root.crt

# Permisos
chown postgres:postgres server.key server.crt root.crt
chmod 400 server.key
chmod 644 server.crt root.crt

# Reiniciar PostgreSQL
sudo systemctl restart postgresql
```

Donem permisos d'execució al script:

```bash
sudo chmod +x /usr/local/sbin/renovar_ssl_postgres.sh
```

Configurem el cron perquè s'executi cada 8 mesos a les 4:00:

```bash
sudo crontab -e
```

Afegim la següent línia:

```cron
0 4 1 */8 * /usr/local/sbin/renovar_ssl_postgres.sh
```

---

### 4.4 Configuració client

Al nostre client de Windows modifiquem el fitxer:

```text
C:\Windows\System32\drivers\etc\hosts
```

Afegim els servidors:

```text
192.168.56.110 pg-primary
192.168.56.111 pg-standby
```

Creem un arxiu `.env`:

```env
DB_SSLMODE=verify-full
DB_SSLROOTCERT=certs/root.crt
```

A l'aplicació carreguem les variables d'entorn del fitxer `.env`:

```python
from dotenv import load_dotenv
import os

# Carregar les variables d'entorn del fitxer .env
load_dotenv()
```

I afegim la configuració SSL a la connexió:

```python
sslmode=os.getenv("DB_SSLMODE"),
sslrootcert=os.getenv("DB_SSLROOTCERT")
```

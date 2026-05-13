# Generació de dades fictícies - Dummy Data

**Projecte:** Hospital Apol·lo  
**Autors:** Pau Encinas i Damià Méndez  
**Curs:** ASIX 1  

---

## Eina utilitzada

S'ha utilitzat la llibreria **Faker** de Python amb dos *locales*:

- `faker` amb locale `es_ES` (castellà): per al 95% dels registres. Genera noms, cognoms, adreces, emails i telèfons amb format espanyol.
- `faker` amb locale `ru_RU` (rus): per al 5% dels registres. Genera dades en alfabet ciríl·lic, tal com demana l'enunciat per donar suport a la població de l'est d'Europa.

Per a les insercions massives s'ha utilitzat **psycopg2** amb la funció `execute_values`, que permet inserir milers de registres en una sola crida SQL, millorant significativament el rendiment.

---

## Dades generades

La taula següent mostra l'ordre d'inserció, respectant les claus foranes, les quantitats i les dependències de cada taula:

| Ordre | Taula | Quantitat | Depèn de | Observació |
|---:|---|---:|---|---|
| 1 | `planta` | 4 | — | Fixes, de l'1 al 4 |
| 2 | `habitacio` | 40 | `planta` | 10 per planta |
| 3 | `quirofan` | 8 | `planta` | 2 per planta |
| 4 | `model_aparell` | 15 | — | Llista predefinida |
| 5 | `aparell` | 80 | `quirofan`, `model_aparell` | Aleatori |
| 6 | `diagnostic` | 50 | — | Llista predefinida |
| 7 | `medicament` | 100 | — | Llista predefinida |
| 8 | `empleat` - metge | 100 | — | Faker `es_ES` / `ru_RU` |
| 9 | `metge` | 100 | `empleat` | 1 especialitat cadascun |
| 10 | `empleat` - infermer | 200 | — | Faker `es_ES` / `ru_RU` |
| 11 | `infermer` | 200 | `empleat`, `metge`, `planta` | 70% metge / 30% planta |
| 12 | `empleat` - neteja | 100 | — | Faker `es_ES` / `ru_RU` |
| 13 | `empleat` - admin | 50 | — | Faker `es_ES` / `ru_RU` |
| 14 | `pacient` | 50.000 | — | Lots de 5.000 |
| 15 | `recepta` | ~70.000 | — | 70% de les visites |
| 16 | `visita` | 100.000 | `metge`, `pacient`, `recepta`, `diagnostic` | Lots de 5.000 |
| 17 | `linia_recepta` | ~150.000 | `recepta`, `medicament` | 1-3 per recepta |
| 18 | `ingres` | 10.000 | `habitacio`, `pacient` | 80% finalitzats |
| 19 | `operacio` | 5.000 | `quirofan`, `metge`, `pacient` | 70% realitzades |
| 20 | `operacio_infermer` | ~15.000 | `operacio`, `infermer` | 2-4 per operació |

---

## Consistència de les dades

S'han aplicat diverses mesures per garantir que les dades generades siguin coherents i respectin les restriccions de la base de dades.

### Ordre d'inserció

Les taules es generen en ordre de dependències de claus foranes:

1. Primer es generen les taules independents, com `planta`, `diagnostic` i `medicament`.
2. Després es generen les taules que en depenen, com `empleat`, `metge` i `infermer`.
3. Finalment es generen les relacions principals, com `visita`, `operacio` i `ingres`.

Això evita errors de tipus `FK violation`.

### Formats correctes

S'han tingut en compte els formats següents:

- **NIF:** 8 dígits + lletra calculada amb mòdul 23, seguint el format espanyol.
- **Targeta sanitària (CIP):** prefix de comunitat, com `CATS`, `ANDA` o `VALE`, seguit de 10 dígits.
- **Número de col·legiat:** format `CC/NNNNN`, amb codi de província i 5 dígits.
- **Hores de visita:** entre les 08:00 i les 20:00, en intervals de 15 minuts.
- **Dates:** distribuïdes en els últims 2 anys.
- **Sexe:** valors vàlids segons el `CHECK`: `home`, `dona` o `altre`.

### Regles de les taules

També s'han respectat les regles pròpies de cada taula:

- Els infermers es distribueixen així:
  - 70% assignats a un metge: `id_metge NOT NULL` i `num_planta NULL`.
  - 30% assignats a planta: `id_metge NULL` i `num_planta NOT NULL`.

- Les visites segueixen aquestes proporcions:
  - 80% tenen diagnòstic.
  - 70% tenen recepta.
  - No totes les visites generen recepta ni diagnòstic.

- Les receptes tenen entre 1 i 3 línies de recepta amb medicaments diferents.

- Les operacions es reparteixen així:
  - 70% ja realitzades, amb entrada i sortida amb valor.
  - 30% programades, amb entrada i sortida `NULL`.

- Els ingressos es reparteixen així:
  - 80% finalitzats.
  - 20% encara actius, amb sortida `NULL`.

- Cada operació és assistida per entre 2 i 4 infermers escollits aleatòriament.

### Dades ciríl·liques

Un 5% dels registres de pacients i empleats es generen amb el locale `ru_RU` de Faker.

Això produeix noms i adreces en alfabet ciríl·lic, per exemple:

```text
Иванов Сергей
ул. Ленина, 42, г. Москва
```

Aquesta prova valida que la base de dades amb codificació **UTF-8** suporta correctament caràcters ciríl·lics.

### Unicitat

El script manté un conjunt (`set`) de NIFs generats per evitar duplicats, ja que el NIF és `UNIQUE` tant a la taula `pacient` com a la taula `empleat`.

Si el NIF generat ja existeix al conjunt, se'n genera un de nou.

---

## Índexs creats

S'han creat diferents índexs per optimitzar les consultes més freqüents que podria necessitar l'aplicació.

El fitxer SQL amb la creació dels índexs es pot consultar aquí:

[creacio_indexos.sql](https://github.com/paueh98-code/Projecte-BBDD-Pau-Damia/blob/main/DummyData/creacio_indexos.sql)

---

## Execució

Primer s'executa l'script de generació de dades:

```bash
python generar_dades.py
```

Aquest script mostra una barra de progrés per cada taula i un resum final amb totes les quantitats generades.

Després s'executa l'script de generació d'índexs:

```bash
psql -d nom_base_dades -f creacio_indexos.sql
```

Finalment, també hi ha l'opció d'eliminar les dades executant l'script corresponent:

```bash
python eliminar_dades.py
```

Aquest script demana confirmació escrivint:

```text
SI
```

Si es confirma, fa un `TRUNCATE CASCADE` de totes les taules en ordre invers de dependències i reinicia les seqüències a 1.

---

## Fitxers utilitzats

| Fitxer | Descripció |
|---|---|
| [`generar_dades.py`](https://github.com/paueh98-code/Projecte-BBDD-Pau-Damia/blob/main/DummyData/generar_dades.py) | Script principal de generació. Insereix totes les dades en 6 fases ordenades per claus foranes. |
| [`eliminar_dades.py`](https://github.com/paueh98-code/Projecte-BBDD-Pau-Damia/blob/main/DummyData/eliminar_dades.py) | Elimina totes les dades amb `TRUNCATE CASCADE` en ordre invers i reinicia les seqüències. |
| [`creacio_indexos.sql`](https://github.com/paueh98-code/Projecte-BBDD-Pau-Damia/blob/main/DummyData/creacio_indexos.sql) | Conté 17 índexs sobre 8 taules per optimitzar consultes freqüents. |

# Diagrama ER - Model Relacional

**Autors:** Pau Encinas i Damià Méndez  
**Cicle:** ASIX 1

Aquest document recull el **diagrama entitat-relació (ER)** i el seu pas a **model relacional** per a la base de dades del sistema de gestió hospitalària.

## Índex

1. [Diagrama ER](#diagrama-er)
2. [Decisions de disseny](#decisions-de-disseny)
3. [Model relacional](#model-relacional)

---

## Diagrama ER

![Diagrama ER](assets/diagrama_er.png)

---

## Decisions de disseny

Per gestionar la disponibilitat de les habitacions per als ingressos i dels quiròfans per a les operacions, s'ha decidit guardar a les taules `INGRES` i `OPERACIO` les dates programades i les dates efectives:

- `entrada_prevista`
- `sortida_prevista`
- `entrada`
- `sortida`

També s'ha separat el concepte de **model d'aparell** i **aparell físic**:

- `MODEL_APARELL`: representa el tipus o model de màquina.
- `APARELL`: representa la màquina individual assignada a un quiròfan.

Pel que fa a les receptes, per poder guardar diferents medicaments dins d'una mateixa recepta s'ha utilitzat l'entitat feble `LINIA_RECEPTA`.

---

## Model relacional

### EMPLEAT

```text
EMPLEAT(id_emp, nom, cognom1, cognom2, nif, email, telèfon, salari, data_contractació, adreça, tipus_feina)
```

---

### INFERMER

```text
INFERMER(id_inf, cv, especialitat, id_metge, núm_planta)
```

**Claus foranes:**

- `id_inf` referencia `EMPLEAT(id_emp)`
- `id_metge` referencia `METGE(id_metge)`
- `núm_planta` referencia `PLANTA(núm_planta)`

---

### METGE

```text
METGE(id_metge, cv, especialitat, núm_colegiat)
```

**Claus foranes:**

- `id_metge` referencia `EMPLEAT(id_emp)`

---

### PLANTA

```text
PLANTA(núm_planta)
```

---

### QUIROFAN

```text
QUIROFAN(núm_planta, núm_quirofan)
```

**Claus foranes:**

- `núm_planta` referencia `PLANTA(núm_planta)`

---

### HABITACIÓ

```text
HABITACIÓ(núm_planta, núm_habitació, núm_llits)
```

**Claus foranes:**

- `núm_planta` referencia `PLANTA(núm_planta)`

---

### APARELL

```text
APARELL(id_aparell, núm_planta, núm_quirofan, id_model, data_revisió)
```

**Claus foranes:**

- `(núm_planta, núm_quirofan)` referencia `QUIROFAN(núm_planta, núm_quirofan)`
- `id_model` referencia `MODEL_APARELL(id_model)`

---

### MODEL_APARELL

```text
MODEL_APARELL(id_model, descripció, nom)
```

---

### OPERACIO

```text
OPERACIO(id_operacio, descripció, entrada, sortida, entrada_prevista, sortida_prevista, id_metge, id_pacient, núm_planta, núm_quirofan)
```

**Claus foranes:**

- `(núm_planta, núm_quirofan)` referencia `QUIROFAN(núm_planta, núm_quirofan)`
- `id_metge` referencia `METGE(id_metge)`
- `id_pacient` referencia `PACIENT(id_pacient)`

---

### OPERACIO_INFERMER

```text
OPERACIO_INFERMER(id_inf, id_operacio)
```

**Claus foranes:**

- `id_inf` referencia `INFERMER(id_inf)`
- `id_operacio` referencia `OPERACIO(id_operacio)`

---

### INGRES

```text
INGRES(id_ingres, núm_planta, núm_habitació, id_pacient, entrada, sortida, entrada_prevista, sortida_prevista)
```

**Claus foranes:**

- `(núm_planta, núm_habitació)` referencia `HABITACIÓ(núm_planta, núm_habitació)`
- `id_pacient` referencia `PACIENT(id_pacient)`

---

### PACIENT

```text
PACIENT(id_pacient, targeta_sanitaria, nom, cognom1, cognom2, adreça, email, telèfon, nif, sexe)
```

---

### VISITA

```text
VISITA(id_visita, hora, data, descripció, id_metge, id_pacient, id_recepta, id_diagnostic)
```

**Claus foranes:**

- `id_metge` referencia `METGE(id_metge)`
- `id_pacient` referencia `PACIENT(id_pacient)`
- `id_recepta` referencia `RECEPTA(id_recepta)`
- `id_diagnostic` referencia `DIAGNOSTIC(id_diagnostic)`

---

### DIAGNOSTIC

```text
DIAGNOSTIC(id_diagnostic, descripció)
```

---

### RECEPTA

```text
RECEPTA(id_recepta, data_inici, data_finalització)
```

---

### LINIA_RECEPTA

```text
LINIA_RECEPTA(id_recepta, núm_linia, pauta, dosi, id_medicament)
```

**Claus foranes:**

- `id_recepta` referencia `RECEPTA(id_recepta)`
- `id_medicament` referencia `MEDICAMENT(id_medicament)`

---

### MEDICAMENT

```text
MEDICAMENT(id_medicament, nom, descripció)
```

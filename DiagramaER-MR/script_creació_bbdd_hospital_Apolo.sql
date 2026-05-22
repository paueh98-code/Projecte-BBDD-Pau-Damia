
-- HOSPITAL DE BLANES APOL ·LO - Script de creació de la Base de Dades
-- Autors: Pau Encinas, Damià Méndez

-- Crear la base de dades amb codificació UTF-8
CREATE DATABASE hospital_blanes
    WITH ENCODING = 'UTF8'
    LC_COLLATE = 'ca_ES.UTF-8'
    LC_CTYPE = 'ca_ES.UTF-8';

-- Connectar a la base de dades
\c hospital_blanes;

-- EMPLEAT: Supertipus de tot el personal de l'hospital
CREATE TABLE IF NOT EXISTS empleat (
    id_emp          SERIAL      PRIMARY KEY,
    nom             VARCHAR(100) NOT NULL,
    cognom1         VARCHAR(100) NOT NULL,
    cognom2         VARCHAR(100),
    nif             VARCHAR(20)  NOT NULL UNIQUE,
    email           VARCHAR(150),
    telefon         VARCHAR(20),
    salari          NUMERIC(10,2),
    data_contractacio DATE,
    adreca          VARCHAR(250),
    tipus_feina     VARCHAR(100) NOT NULL
        CHECK (tipus_feina IN ('metge', 'infermer', 'administratiu', 'conductor ambulancia', 'neteja', 'directiu', 'informatic', 'manteniment'))
);

-- PLANTA: Les 4 plantes de l'hospital
CREATE TABLE IF NOT EXISTS planta (
    num_planta      INT         PRIMARY KEY
        CHECK (num_planta BETWEEN 1 AND 4)
);

-- PACIENT
CREATE TABLE IF NOT EXISTS pacient (
    id_pacient          SERIAL      PRIMARY KEY,
    targeta_sanitaria   VARCHAR(30) NOT NULL UNIQUE,
    nom                 VARCHAR(100) NOT NULL,
    cognom1             VARCHAR(100) NOT NULL,
    cognom2             VARCHAR(100),
    adreca              VARCHAR(250),
    email               VARCHAR(150),
    telefon             VARCHAR(20),
    nif                 VARCHAR(20)  NOT NULL UNIQUE,
    sexe                VARCHAR(10)
        CHECK (sexe IN ('home', 'dona', 'altre'))
);

-- MEDICAMENT
CREATE TABLE IF NOT EXISTS medicament (
    id_medicament   SERIAL      PRIMARY KEY,
    nom             VARCHAR(200) NOT NULL,
    descripcio      TEXT
);

-- MODEL_APARELL: Tipus d'aparell mèdic (respirador, màquina d'oxigen, etc.)
CREATE TABLE IF NOT EXISTS model_aparell (
    id_model        SERIAL      PRIMARY KEY,
    nom             VARCHAR(150) NOT NULL,
    descripcio      TEXT
);

-- DIAGNOSTIC
CREATE TABLE IF NOT EXISTS diagnostic (
    id_diagnostic   SERIAL      PRIMARY KEY,
    descripcio      TEXT        NOT NULL
);

-- RECEPTA
CREATE TABLE IF NOT EXISTS recepta (
    id_recepta          SERIAL  PRIMARY KEY,
    data_inici          DATE    NOT NULL,
    data_finalitzacio   DATE
);

-- METGE: Subtipus d'EMPLEAT
CREATE TABLE IF NOT EXISTS metge (
    id_metge        INT         PRIMARY KEY REFERENCES empleat(id_emp)
                                ON UPDATE CASCADE ON DELETE RESTRICT,
    cv              TEXT,
    especialitat    VARCHAR(150) NOT NULL,
    num_colegiat    VARCHAR(30)  NOT NULL UNIQUE
);

-- INFERMER: Subtipus d'EMPLEAT, pot dependre d'un metge o ser de planta
CREATE TABLE IF NOT EXISTS infermer (
    id_inf          INT         PRIMARY KEY REFERENCES empleat(id_emp)
                                ON UPDATE CASCADE ON DELETE RESTRICT,
    cv              TEXT,
    especialitat    VARCHAR(150),
    id_metge        INT         REFERENCES metge(id_metge)
                                ON UPDATE CASCADE ON DELETE SET NULL,
    num_planta      INT         REFERENCES planta(num_planta)
                                ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT chk_infermer_assignacio CHECK (
        (id_metge IS NOT NULL AND num_planta IS NULL)
        OR
        (id_metge IS NULL AND num_planta IS NOT NULL)
    )
);


-- QUIROFAN: Entitat feble dependent de PLANTA 
CREATE TABLE IF NOT EXISTS quirofan (
    num_planta      INT         NOT NULL REFERENCES planta(num_planta)
                                ON UPDATE CASCADE ON DELETE RESTRICT,
    num_quirofan    VARCHAR(10) NOT NULL,
    PRIMARY KEY (num_planta, num_quirofan)
);

-- HABITACIO: Entitat feble dependent de PLANTA
CREATE TABLE IF NOT EXISTS habitacio (
    num_planta      INT         NOT NULL REFERENCES planta(num_planta)
                                ON UPDATE CASCADE ON DELETE RESTRICT,
    num_habitacio   VARCHAR(10) NOT NULL,
    num_llits       INT         NOT NULL DEFAULT 1
                                CHECK (num_llits > 0),
    PRIMARY KEY (num_planta, num_habitacio)
);


-- VISITA
CREATE TABLE IF NOT EXISTS visita (
    id_visita       SERIAL      PRIMARY KEY,
    hora            TIME        NOT NULL,
    data            DATE        NOT NULL,
    descripcio      TEXT,
    id_metge        INT         NOT NULL REFERENCES metge(id_metge)
                                ON UPDATE CASCADE ON DELETE RESTRICT,
    id_pacient      INT         NOT NULL REFERENCES pacient(id_pacient)
                                ON UPDATE CASCADE ON DELETE RESTRICT,
    id_recepta      INT         REFERENCES recepta(id_recepta)
                                ON UPDATE CASCADE ON DELETE SET NULL,
    id_diagnostic   INT         REFERENCES diagnostic(id_diagnostic)
                                ON UPDATE CASCADE ON DELETE SET NULL
);



-- LINIA_RECEPTA: Entitat feble de RECEPTA
CREATE TABLE IF NOT EXISTS linia_recepta (
    id_recepta      INT         NOT NULL REFERENCES recepta(id_recepta)
                                ON UPDATE CASCADE ON DELETE CASCADE,
    num_linia       INT         NOT NULL,
    pauta           VARCHAR(250),
    dosi            VARCHAR(100),
    id_medicament   INT         NOT NULL REFERENCES medicament(id_medicament)
                                ON UPDATE CASCADE ON DELETE RESTRICT,
    PRIMARY KEY (id_recepta, num_linia)
);


-- OPERACIO
CREATE TABLE IF NOT EXISTS operacio (
    id_operacio         SERIAL  PRIMARY KEY,
    descripcio          TEXT,
    entrada             TIMESTAMP,
    sortida             TIMESTAMP,
    entrada_prevista    TIMESTAMP NOT NULL,
    sortida_prevista    TIMESTAMP,
    id_metge            INT     NOT NULL REFERENCES metge(id_metge)
                                ON UPDATE CASCADE ON DELETE RESTRICT,
    id_pacient          INT     NOT NULL REFERENCES pacient(id_pacient)
                                ON UPDATE CASCADE ON DELETE RESTRICT,
    num_planta          INT     NOT NULL,
    num_quirofan        VARCHAR(10) NOT NULL,
    CONSTRAINT fk_operacio_quirofan
        FOREIGN KEY (num_planta, num_quirofan)
        REFERENCES quirofan(num_planta, num_quirofan)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_operacio_dates CHECK (
        sortida_prevista IS NULL OR entrada_prevista <= sortida_prevista
    )
);

-- OPERACIO_INFERMER: Relació N:M entre operacions i infermers
CREATE TABLE IF NOT EXISTS operacio_infermer (
    id_inf          INT         NOT NULL REFERENCES infermer(id_inf)
                                ON UPDATE CASCADE ON DELETE RESTRICT,
    id_operacio     INT         NOT NULL REFERENCES operacio(id_operacio)
                                ON UPDATE CASCADE ON DELETE CASCADE,
    PRIMARY KEY (id_inf, id_operacio)
);

-- INGRES: Ingressos de pacients a habitacions i programacions
CREATE TABLE IF NOT EXISTS ingres (
    id_ingres           SERIAL  PRIMARY KEY,
    num_planta          INT     NOT NULL,
    num_habitacio       VARCHAR(10) NOT NULL,
    id_pacient          INT     NOT NULL REFERENCES pacient(id_pacient)
                                ON UPDATE CASCADE ON DELETE RESTRICT,
    entrada             TIMESTAMP,
    sortida             TIMESTAMP,
    entrada_prevista    TIMESTAMP NOT NULL,
    sortida_prevista    TIMESTAMP,
    CONSTRAINT fk_ingres_habitacio
        FOREIGN KEY (num_planta, num_habitacio)
        REFERENCES habitacio(num_planta, num_habitacio)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_ingres_dates CHECK (
        sortida_prevista IS NULL OR entrada_prevista <= sortida_prevista
    )
);

-- APARELL: Màquina individual assignada a un quiròfan
CREATE TABLE IF NOT EXISTS aparell (
    id_aparell      SERIAL      PRIMARY KEY,
    num_planta      INT         NOT NULL,
    num_quirofan    VARCHAR(10) NOT NULL,
    id_model        INT         NOT NULL REFERENCES model_aparell(id_model)
                                ON UPDATE CASCADE ON DELETE RESTRICT,
    data_revisio    DATE,
    CONSTRAINT fk_aparell_quirofan
        FOREIGN KEY (num_planta, num_quirofan)
        REFERENCES quirofan(num_planta, num_quirofan)
        ON UPDATE CASCADE ON DELETE RESTRICT
);



-- Crear les 4 plantes
INSERT INTO planta (num_planta) VALUES (1), (2), (3), (4);
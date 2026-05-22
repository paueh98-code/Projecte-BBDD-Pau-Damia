--Creació de l'essquema de masking
CREATE SCHEMA IF NOT EXISTS mask;
--Masking de pacients
CREATE OR REPLACE VIEW mask.pacient AS
SELECT
    id_pacient,
    -- Targeta sanitària: primers 4 + asteriscs + últims 4
    CONCAT(
        SUBSTRING(targeta_sanitaria, 1, 4),
        REPEAT('*', GREATEST(LENGTH(targeta_sanitaria) - 8, 0)),
        SUBSTRING(targeta_sanitaria, LENGTH(targeta_sanitaria) - 3, 4)
    ) AS targeta_sanitaria,
    nom,
    cognom1,
    cognom2,
    -- Adreça: primers 8 caràcters + ***
    CASE
        WHEN adreca IS NULL THEN NULL
        WHEN LENGTH(adreca) < 5 THEN '***'
        ELSE SUBSTRING(adreca, 1, 8) || '***'
    END AS adreca,
    -- Email: primers 2 caràcters + asteriscs + @domini
    CASE
        WHEN email IS NULL THEN NULL
        WHEN POSITION('@' IN email) <= 2 THEN '*' || SUBSTRING(email FROM POSITION('@' IN email))
        ELSE SUBSTRING(email, 1, 2)
             || REPEAT('*', POSITION('@' IN email) - 3)
             || SUBSTRING(email FROM POSITION('@' IN email))
    END AS email,
    -- Telèfon: primers 3 + asteriscs + últims 3
    CASE
        WHEN telefon IS NULL THEN NULL
        WHEN LENGTH(telefon) < 6 THEN '***'
        ELSE SUBSTRING(telefon, 1, 3)
             || REPEAT('*', GREATEST(LENGTH(telefon) - 6, 0))
             || SUBSTRING(telefon, LENGTH(telefon) - 2, 3)
    END AS telefon,
    -- NIF: primer caràcter + asteriscs + últim caràcter
    CASE
        WHEN nif IS NULL THEN NULL
        WHEN LENGTH(nif) < 3 THEN '***'
        ELSE SUBSTRING(nif, 1, 1)
             || REPEAT('*', LENGTH(nif) - 2)
             || SUBSTRING(nif, LENGTH(nif), 1)
    END AS nif,
    sexe
FROM public.pacient;
--Masking de empleat
CREATE OR REPLACE VIEW mask.empleat AS
SELECT
    id_emp,
    nom,
    cognom1,
    cognom2,
    -- NIF emmascardat
    CASE
        WHEN nif IS NULL THEN NULL
        WHEN LENGTH(nif) < 3 THEN '***'
        ELSE SUBSTRING(nif, 1, 1)
             || REPEAT('*', LENGTH(nif) - 2)
             || SUBSTRING(nif, LENGTH(nif), 1)
    END AS nif,
    -- Email emmascardat
    CASE
        WHEN email IS NULL THEN NULL
        WHEN POSITION('@' IN email) <= 2 THEN '*' || SUBSTRING(email FROM POSITION('@' IN email))
        ELSE SUBSTRING(email, 1, 2)
             || REPEAT('*', POSITION('@' IN email) - 3)
             || SUBSTRING(email FROM POSITION('@' IN email))
    END AS email,
    -- Telèfon emmascardat
    CASE
        WHEN telefon IS NULL THEN NULL
        WHEN LENGTH(telefon) < 6 THEN '***'
        ELSE SUBSTRING(telefon, 1, 3)
             || REPEAT('*', GREATEST(LENGTH(telefon) - 6, 0))
             || SUBSTRING(telefon, LENGTH(telefon) - 2, 3)
    END AS telefon,
    salari,
    data_contractacio,
    -- Adreça emmascarada
    CASE
        WHEN adreca IS NULL THEN NULL
        WHEN LENGTH(adreca) < 5 THEN '***'
        ELSE SUBSTRING(adreca, 1, 8) || '***'
    END AS adreca,
    tipus_feina
FROM public.empleat;
--Masking de visita
CREATE OR REPLACE VIEW mask.visita AS
SELECT
    id_visita,
    hora,
    data,
    CASE
        WHEN descripcio IS NOT NULL THEN LEFT(descripcio, 30) || '...'
        ELSE NULL
    END AS descripcio,
    id_metge,
    id_pacient,
    id_recepta,
    id_diagnostic
FROM public.visita;
--Masking de linia recepta
CREATE OR REPLACE VIEW mask.linia_recepta AS
SELECT
    id_recepta,
    num_linia,
    '***' AS pauta,
    '***' AS dosi,
    id_medicament
FROM public.linia_recepta;
--Masking de operació
CREATE OR REPLACE VIEW mask.operacio AS
SELECT
    id_operacio,
    CASE
        WHEN descripcio IS NOT NULL THEN LEFT(descripcio, 20) || '...'
        ELSE NULL
    END AS descripcio,
    entrada,
    sortida,
    entrada_prevista,
    sortida_prevista,
    id_metge,
    id_pacient,
    num_planta,
    num_quirofan
FROM public.operacio;
--Permisos per usar l'esquema mask
GRANT USAGE ON SCHEMA mask TO rol_metge, rol_infermer, rol_directiu, rol_administratiu;
GRANT SELECT ON ALL TABLES IN SCHEMA mask TO rol_metge, rol_infermer, rol_directiu, rol_administratiu;

ALTER DEFAULT PRIVILEGES IN SCHEMA mask
    GRANT SELECT ON TABLES TO rol_metge, rol_infermer, rol_directiu, rol_administratiu;
--Configuració del SEARCH_PATH per buscar primer a mask abans de a public
ALTER ROLE rol_metge      SET search_path = mask, public;
ALTER ROLE rol_infermer   SET search_path = mask, public;
ALTER ROLE rol_directiu   SET search_path = mask, public;
ALTER ROLE rol_administratiu   SET search_path = mask, public;
-- Revocar acces a taules sensibles
-- Pacient i empleat: revocar a metge, infermer, directiu i administratiu
REVOKE SELECT ON public.pacient FROM rol_metge, rol_infermer, rol_directiu, rol_administratiu;
REVOKE SELECT ON public.empleat FROM rol_metge, rol_infermer, rol_directiu, rol_administratiu;

-- Visita: revocar a infermer, administratiu i directiu (el metge la necessita completa)
REVOKE SELECT ON public.visita FROM rol_infermer, rol_directiu, rol_administratiu;

-- Linia_recepta: revocar a directiu i administratiu
REVOKE SELECT ON public.linia_recepta FROM rol_directiu, rol_administratiu;

-- Operacio: revocar a directiu i administratiu
REVOKE SELECT ON public.operacio FROM rol_directiu, rol_administratiu;

-- El metge accedeix a public.visita (completa) directament
GRANT SELECT ON public.visita TO rol_metge;
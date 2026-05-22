
-- Creació dels rols
-- Administrador del sistema: accés total
CREATE ROLE sysadmin NOLOGIN;
GRANT ALL PRIVILEGES
ON DATABASE hospitalapolo
TO sysadmin;
-- Directius: poden afegir empleats i recursos com aparells i medicaments. Poden veure les altres taules per fer estadistiques.
CREATE ROLE rol_directiu NOLOGIN;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO rol_directiu;
GRANT INSERT, UPDATE, DELETE ON
    aparell, model_aparell, empleat, metge, infermer, medicament
TO rol_directiu;
-- Metges: Consulta: pacient, metge, infermer, planta,
--              quirofan, habitacio, aparell, model_aparell,ingres.
--		Gestió completa: visita, recepta, linia_recepta,
--                     diagnostic, medicament, operacio,
--                     operacio_infermer.
CREATE ROLE rol_metge NOLOGIN;
GRANT SELECT ON
    pacient, metge, infermer, planta, quirofan, habitacio, aparell, model_aparell, ingres
TO rol_metge;
GRANT SELECT, INSERT, UPDATE, DELETE ON
    visita, recepta, linia_recepta, diagnostic, medicament, operacio, operacio_infermer
TO rol_metge;
-- Infermer: pot consultar les mateixes taules que el metge pero no les pot modificar.
CREATE ROLE rol_infermer NOLOGIN;
GRANT SELECT ON
    pacient, metge, infermer, planta, quirofan, habitacio, aparell, model_aparell, visita, recepta, linia_recepta, diagnostic, medicament, operacio, ingres, operacio_infermer
TO rol_infermer;
--Administratius: gestionen tot el que es altes i baixes de personal, gestions de pacients i programacions d'ingresos, operacions i visites.
CREATE ROLE rol_administratiu NOLOGIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON
    empleat, metge, infermer, pacient, visita, quirofan, habitacio, ingres, aparell, medicament, operacio
TO rol_administratiu;
GRANT SELECT ON
    recepta, linia_recepta, diagnostic, model_aparell, operacio_infermer
TO rol_administratiu;
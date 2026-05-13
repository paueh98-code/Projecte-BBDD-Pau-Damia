-- ============================================================
-- HOSPITAL APOL·LO - Creació d'Índexs
-- Optimització de rendiment per a consultes freqüents
-- Autors: Pau Encinas, Damià Méndez
-- ============================================================

-- PACIENT: cerques per nom complet (informes, manteniment)
CREATE INDEX IF NOT EXISTS idx_pacient_nom
    ON pacient (cognom1, cognom2, nom);

-- EMPLEAT: cerques per tipus de feina (informes de personal)
CREATE INDEX IF NOT EXISTS idx_empleat_tipus
    ON empleat (tipus_feina);

-- EMPLEAT: cerques per nom
CREATE INDEX IF NOT EXISTS idx_empleat_nom
    ON empleat (cognom1, cognom2, nom);

-- VISITA: cerques per data (informe visites per dia, exportació entre dates)
CREATE INDEX IF NOT EXISTS idx_visita_data
    ON visita (data);

-- VISITA: cerques per metge (visites d'un metge, ranking)
CREATE INDEX IF NOT EXISTS idx_visita_metge
    ON visita (id_metge);

-- VISITA: cerques per pacient (historial del pacient)
CREATE INDEX IF NOT EXISTS idx_visita_pacient
    ON visita (id_pacient);

-- VISITA: cerques per diagnòstic (malalties més comunes)
CREATE INDEX IF NOT EXISTS idx_visita_diagnostic
    ON visita (id_diagnostic);

-- OPERACIO: cerques per data prevista (planificació quiròfans)
CREATE INDEX IF NOT EXISTS idx_operacio_data
    ON operacio (entrada_prevista);

-- OPERACIO: cerques per metge
CREATE INDEX IF NOT EXISTS idx_operacio_metge
    ON operacio (id_metge);

-- OPERACIO: cerques per pacient
CREATE INDEX IF NOT EXISTS idx_operacio_pacient
    ON operacio (id_pacient);

-- INGRES: cerques per pacient (historial ingressos)
CREATE INDEX IF NOT EXISTS idx_ingres_pacient
    ON ingres (id_pacient);

-- INGRES: cerques per data (ocupació habitacions)
CREATE INDEX IF NOT EXISTS idx_ingres_dates
    ON ingres (entrada_prevista);

-- INFERMER: cerques per metge assignat
CREATE INDEX IF NOT EXISTS idx_infermer_metge
    ON infermer (id_metge);

-- INFERMER: cerques per planta
CREATE INDEX IF NOT EXISTS idx_infermer_planta
    ON infermer (num_planta);

-- LINIA_RECEPTA: cerques per medicament (estadístiques)
CREATE INDEX IF NOT EXISTS idx_linia_recepta_med
    ON linia_recepta (id_medicament);

-- APARELL: cerques per model (inventari per tipus)
CREATE INDEX IF NOT EXISTS idx_aparell_model
    ON aparell (id_model);

-- ============================================================
-- TOTAL: 17 índexs sobre 8 taules
-- ============================================================

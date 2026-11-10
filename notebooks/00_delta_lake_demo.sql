-- Démonstration Delta Lake : UPDATE, Time Travel, RESTORE, MERGE

-- Simulation d'une erreur
UPDATE workspace.default.ventes_par_jour SET chiffre_affaires = 0 WHERE jour = '2024-05-17';

-- Lecture de la version précédente (Time Travel)
SELECT * FROM workspace.default.ventes_par_jour VERSION AS OF 0 WHERE jour = '2024-05-17';

-- Restauration
RESTORE TABLE workspace.default.ventes_par_jour TO VERSION AS OF 0;

-- Chargement incrémental (upsert)
CREATE OR REPLACE TEMP VIEW nouvelles_ventes AS
SELECT * FROM VALUES
  (DATE'2024-05-17', CAST(2500 AS BIGINT), CAST(130 AS BIGINT)),
  (DATE'2024-05-18', CAST(3900 AS BIGINT), CAST(195 AS BIGINT))
AS t(jour, chiffre_affaires, nb_transactions);

MERGE INTO workspace.default.ventes_par_jour AS cible
USING nouvelles_ventes AS source
ON cible.jour = source.jour
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;

-- Historique des versions
DESCRIBE HISTORY workspace.default.ventes_par_jour;

-- 🥇 GOLD : CA quotidien par pays
CREATE OR REPLACE TABLE workspace.gold.ca_pays_jour
COMMENT 'CA quotidien par pays - source silver.ventes' AS
SELECT country AS pays, date_vente,
       SUM(montant) AS chiffre_affaires,
       COUNT(*) AS nb_transactions,
       ROUND(SUM(montant) / COUNT(*), 2) AS panier_moyen
FROM workspace.silver.ventes
GROUP BY country, date_vente;



-- 🥇 GOLD : classement des franchises
CREATE OR REPLACE TABLE workspace.gold.classement_franchises
COMMENT 'Performance par franchise - source silver.ventes' AS
SELECT franchise, city AS ville, country AS pays, size AS taille,
       SUM(montant) AS chiffre_affaires,
       COUNT(*) AS nb_transactions,
       RANK() OVER (ORDER BY SUM(montant) DESC) AS rang
FROM workspace.silver.ventes
GROUP BY franchise, city, country, size;

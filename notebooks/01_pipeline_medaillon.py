# Databricks notebook source
# MAGIC %md
# MAGIC # Pipeline médaillon Bakehouse : Bronze → Silver → Gold

# COMMAND ----------
# MAGIC %sql
# MAGIC CREATE SCHEMA IF NOT EXISTS workspace.bronze COMMENT 'Données brutes';
# MAGIC CREATE SCHEMA IF NOT EXISTS workspace.silver COMMENT 'Données nettoyées';
# MAGIC CREATE SCHEMA IF NOT EXISTS workspace.gold   COMMENT 'Données métier agrégées';

# COMMAND ----------
# 🥉 BRONZE : copie brute des sources
spark.table("samples.bakehouse.sales_transactions") \
     .write.mode("overwrite").saveAsTable("workspace.bronze.transactions")
spark.table("samples.bakehouse.sales_franchises") \
     .write.mode("overwrite").saveAsTable("workspace.bronze.franchises")

# COMMAND ----------
# 🥈 SILVER : nettoyage, enrichissement, RGPD
from pyspark.sql import functions as F

tx = spark.table("workspace.bronze.transactions")
fr = spark.table("workspace.bronze.franchises")

silver = (
    tx
    .dropDuplicates(["transactionID"])                                # doublons
    .filter(F.col("quantity") > 0)                                    # lignes incohérentes
    .withColumn("date_vente", F.to_date("dateTime"))
    .withColumn("montant", F.col("quantity") * F.col("unitPrice"))
    .join(fr.select("franchiseID", F.col("name").alias("franchise"),
                    "city", "country", "size"),
          on="franchiseID", how="left")                               # enrichissement
    .drop("cardNumber")                                               # donnée sensible (RGPD)
)
silver.write.mode("overwrite").saveAsTable("workspace.silver.ventes")

# COMMAND ----------
# MAGIC %sql
# MAGIC -- Contrôle qualité Silver
# MAGIC SELECT COUNT(*) AS nb_lignes,
# MAGIC        COUNT(DISTINCT transactionID) AS nb_transactions_uniques,
# MAGIC        SUM(CASE WHEN franchise IS NULL THEN 1 ELSE 0 END) AS ventes_sans_franchise,
# MAGIC        MIN(date_vente) AS premiere_vente, MAX(date_vente) AS derniere_vente
# MAGIC FROM workspace.silver.ventes;

# COMMAND ----------
# MAGIC %sql
# MAGIC -- 🥇 GOLD : CA quotidien par pays
# MAGIC CREATE OR REPLACE TABLE workspace.gold.ca_pays_jour
# MAGIC COMMENT 'CA quotidien par pays - source silver.ventes' AS
# MAGIC SELECT country AS pays, date_vente,
# MAGIC        SUM(montant) AS chiffre_affaires,
# MAGIC        COUNT(*) AS nb_transactions,
# MAGIC        ROUND(SUM(montant) / COUNT(*), 2) AS panier_moyen
# MAGIC FROM workspace.silver.ventes
# MAGIC GROUP BY country, date_vente;

# COMMAND ----------
# MAGIC %sql
# MAGIC -- 🥇 GOLD : classement des franchises
# MAGIC CREATE OR REPLACE TABLE workspace.gold.classement_franchises
# MAGIC COMMENT 'Performance par franchise - source silver.ventes' AS
# MAGIC SELECT franchise, city AS ville, country AS pays, size AS taille,
# MAGIC        SUM(montant) AS chiffre_affaires,
# MAGIC        COUNT(*) AS nb_transactions,
# MAGIC        RANK() OVER (ORDER BY SUM(montant) DESC) AS rang
# MAGIC FROM workspace.silver.ventes
# MAGIC GROUP BY franchise, city, country, size;

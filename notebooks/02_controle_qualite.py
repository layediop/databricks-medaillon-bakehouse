# Databricks notebook source
# Tâche "controle_qualite" du Job : échoue (et déclenche une alerte email) si les données sont incorrectes
doublons = spark.sql("""
    SELECT COUNT(*) - COUNT(DISTINCT transactionID) AS nb
    FROM workspace.silver.ventes
""").first()["nb"]

lignes_gold = spark.table("workspace.gold.ca_pays_jour").count()

assert doublons == 0, f"ÉCHEC : {doublons} doublons dans silver.ventes"
assert lignes_gold > 0, "ÉCHEC : la table gold.ca_pays_jour est vide"

print(f"Contrôle qualité OK : 0 doublon, {lignes_gold} lignes en Gold")

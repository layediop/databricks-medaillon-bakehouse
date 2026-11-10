# Mesures DAX

Connexion : Power BI Desktop → connecteur Databricks → SQL Warehouse (DirectQuery), token à scope `sql`.

```DAX
Panier moyen =
DIVIDE(
    SUM(ca_pays_jour[chiffre_affaires]),
    SUM(ca_pays_jour[nb_transactions])
)
```

> La colonne `panier_moyen` de la table Gold est masquée dans le rapport : additionner des ratios donnerait un résultat faux. La mesure recalcule le ratio selon le contexte de filtre (pays, date…).

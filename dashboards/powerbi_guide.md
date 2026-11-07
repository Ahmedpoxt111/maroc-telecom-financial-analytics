# Construire le dashboard Power BI
Fichier PBIX non fourni : ces instructions décrivent sa construction; les CSV sont déjà prêts.
1. Power BI Desktop > Obtenir des données > Texte/CSV : importer powerbi_financials.csv (UTF-8, séparateur virgule). Fixer year en entier, value en nombre décimal avec paramètres régionaux Anglais (États-Unis), car décimale point. Les autres colonnes sont texte.
2. Importer data/processed/ratios.csv, forecasts.csv, dcf.csv, sensitivity.csv et data/raw/sources.csv. Ne pas relier entre eux deux faits sur year seul : cela créerait une relation plusieurs-à-plusieurs. Créer une dimension Année (2023-2030), relations un-à-plusieurs vers les faits; garder DCF et sensibilité séparés pour leurs propres visuels.
3. Page Historique : filtre status=reported et scenario=historique. Courbes revenue_kpi, ebitda_adjusted et ebita_adjusted; cartes liquidité générale et marge ajustée depuis ratios. Ne jamais sommer des métriques différentes.
4. Page Prévisions : filtre status=forecast; segment scenario en sélection unique; courbe revenue et colonnes fcff par year. Présenter « Hypothèses auteur » dans le titre.
5. Page Valorisation : tableau dcf (scenario, enterprise_value, terminal_share); matrice sensitivity avec wacc en lignes, terminal_growth en colonnes et enterprise_value en valeurs. Mise en forme conditionnelle. Afficher « VE pédagogique au 31/12/2025, millions MAD ».
6. Page Sources : URL et localisateurs; afficher les écarts de publication du dictionnaire. Actualiser après chaque exécution Python. Pas de rafraîchissement automatique des sources web.

Mesures DAX dans la table renommée Financials (adapter ; ou , selon la locale) :
```dax
CA historique = CALCULATE(SUM(Financials[value]), Financials[metric] = "revenue_kpi", Financials[status] = "reported")
EBITDA ajusté = CALCULATE(SUM(Financials[value]), Financials[metric] = "ebitda_adjusted", Financials[status] = "reported")
Marge EBITDA = DIVIDE([EBITDA ajusté], [CA historique])
CA prévision = CALCULATE(SUM(Financials[value]), Financials[metric] = "revenue", Financials[status] = "forecast")
```
Contrôles : CA 2025=36 681; EBITDA 2025=18 493; trois scénarios de cinq années. Les totaux multi-années des ratios et de la VE doivent être désactivés. Les DAX sont des instructions à vérifier dans Desktop; seul le pipeline CSV/SQL est exécuté ici.

# Dictionnaire, bases et écarts

**Complément :** les bilans sociaux, CPC, ESG, CAF et tableau de financement IAM SA sont désormais transcrits du DEU 2025 dans `social_statements.csv` et `financing.csv`. Leurs tableaux lisibles et les 19 ratios sociaux se trouvent dans `data/tables/` et `LIRE_LES_TABLEAUX.html`. Les définitions ci-dessous concernent principalement l’ancien jeu consolidé; ne pas fusionner les périmètres. L’ESG et la CAF sociaux sont des chiffres publiés, pas une reconstitution d’IFRS.
Tous les montants des données brutes sont en millions MAD, valeurs positives; acquisitions cash stockées comme sorties positives. Chaque cellule comporte source_id, locator (page imprimée), basis et status. La transcription est manuelle à partir des tableaux officiels consultés le 07/11/2026. Aucun remplissage des données absentes par zéro.

- S1 : série des KPI ajustés actuellement affichée pour 2023-2025; indicateurs alternatifs, pas états IFRS complets.
- S2 : états consolidés présentés dans le rapport financier 2025, p.4 et 23-25. Le rapport précise qu'il ne remplace pas la version officielle intégrée au DEU. Ne pas appeler ce fichier le DEU.
- S3 : dette nette KPI en comparatif FY2025; ne pas la substituer mécaniquement à dette LT+CT-trésorerie.

## Écarts conservés, jamais corrigés silencieusement
CA 2024 : 36 704 (KPI) contre 36 699 (états IFRS S2). Résultat groupe 2025 : 6 969 dans le communiqué FY2025 contre 6 968 dans S2. Le pipeline utilise S2 pour les ratios IFRS et S1 pour les marges ajustées.
Le communiqué FY2024 initial présentait EBITDA ajusté 19 197 et EBITA ajusté 12 182; la série KPI reprise en 2025 affiche 19 188 et 12 092. Résultat net ajusté 2023 : 6 195 dans le communiqué initial, 6 108 sur S1. Ces séries sont des versions de publication différentes; aucune explication de retraitement n'est inventée ici. Voir la source initiale : https://www.iam.ma/documents/66341/0/Maroc_Telecom_CP-Resultats_FY2024.pdf/86aa304c-1c81-6d17-dea2-107e36f62422?t=1741084834525
Comparatif initial 2023 : https://live.euronext.com/fr/products/equities/company-news/2024-02-16-maroc-telecom-resultats-consolides-2023

## Colonnes brutes
revenue_ifrs, operating_profit_ifrs, net_income_total, net_income_group : CA, résultat opérationnel, résultat net total et part groupe des états consolidés.
assets, current_assets : total actif et actif courant. equity_total, equity_group, nci_book : capitaux propres consolidés, part groupe et intérêts minoritaires comptables.
noncurrent_liabilities, current_liabilities : passifs par échéance. debt_lt, debt_st : emprunts et autres passifs financiers. cash : trésorerie et équivalents.
stocks, receivables_other, operating_payables : stocks, créances d'exploitation et autres, dettes d'exploitation.
operating_cashflow : flux d'exploitation après impôts. cash_capex_outflow : acquisitions d'immobilisations en cash. cash_disposals : cessions cash.
revenue_kpi, ebitda_adjusted, ebita_adjusted, net_income_adjusted_group, capex_kpi : indicateurs du tableau S1. capex_kpi comprend fréquences et licences, sans être assimilable au cash capex.
net_debt_kpi : dette nette communiquée S3, seulement 2024-2025; pas de 2023 estimé.

## Calculs
Croissance IFRS=CA/CA précédent-1; 2023 vide faute de 2022. Marges ajustées=KPI ajusté/CA KPI. Marge nette=RN total/CA IFRS. Liquidité générale=actif courant/passif courant. Autonomie=CP totaux/actif. ROE part groupe=RN groupe/CP groupe de clôture (pas moyenne).
Dette nette simple=dette LT+CT-cash, distincte de la définition S3. BFR proxy=stocks+créances et autres-dettes exploitation; aucune assimilation au BFR normalisé du DCF. FCF cash proxy=CFO-acquisitions cash+cessions cash, différent du FCFF avant financement.
Les écarts de 1 MDH dans certaines égalités peuvent résulter des arrondis : contrôle bilan à tolérance de 1 MDH.
CAF et SIG PCG marocain ne sont pas reconstitués à partir d'IFRS; pas de faux tableau complet. Aucun audit légal effectué.

## Sorties
ratios.csv : status=calculated; ratios en décimal, montants en MDH. forecasts.csv : status=forecast; montants issus d'hypothèses. dcf.csv et sensitivity.csv : status=calculated_from_assumptions; VE en MDH, taux décimaux. sources.csv contient les URL et dates de consultation. powerbi_financials.csv : format long, statut obligatoire pour séparer historique et projection.

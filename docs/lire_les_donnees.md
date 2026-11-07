# Organisation des données — version 2

Les tableaux du bilan actif, bilan passif, CPC, ESG et CAF concernent **IAM SA seule**, référentiel marocain CGNC. L'historique consolidé et le DCF concernent le **Groupe**, IFRS et KPI ajustés explicitement séparés. Aucune somme ni ratio n'assemble ces deux périmètres.

## Fichiers à utiliser
- `data/raw/social_statements.csv` : transcription des états sociaux du DEU 2025, années 2023, 2024, 2025, en milliers MAD. Valeurs nettes pour l'actif; sélection des postes et sous-postes, sans colonnes brut/amortissements. Les postes explicitement nuls utiles sont conservés; les lignes de répétition identiques et certains sous-postes nuls sont omis.
- `data/tables/` : tableaux français en colonnes 2023-2025, en **millions MAD**, conversion exacte par division par 1 000. Une colonne source/page et les variations 2025/2024 accompagnent les chiffres.
- `data/processed/social_analysis.csv` : FR fonctionnel, besoin de financement global, trésorerie nette et ratios calculés à partir du bilan social net.
- `dashboards/finance_sociale.csv` : table annuelle plate avec indicateurs nommés, une ligne par année, uniquement IAM SA. Destinée à Power BI sans ambiguïté d'agrégation.
- `data/raw/reported_financials.csv` : historique consolidé conservé, avec `basis` explicite. Ne pas importer ce fichier dans le modèle IAM SA en le joignant par année.

## Contrôles et écarts
Les valeurs publiées des sous-totaux sont conservées même si la somme des nombres arrondis diffère légèrement. Les contrôles calculent les écarts, avec une tolérance de 0,005 MDH (5 milliers MAD) pour les états sociaux. Le contrôle total actif=total passif est exact pour chaque année.
La marge brute 2023 publiée est -12 632 milliers MAD, contre -12 631 calculés à partir des ventes et achats arrondis; cet écart de 1 millier est exposé, pas remplacé. La CAF utilise uniquement les dotations/reprises éligibles de l'ESG, pas les dotations totales du CPC.

## Formules sociales
FR fonctionnel=financement permanent-actif immobilisé net.
BFG=actif circulant hors trésorerie-passif circulant hors trésorerie.
Trésorerie nette=trésorerie actif-trésorerie passif; doit correspondre à FR-BFG sous réserve des arrondis.
Marge EBE=EBE/CA social; marge nette=RN social/CA social; autonomie=CP sociaux/total actif social.
Les ratios de structure sont calculés sur bilan net de clôture; ce n'est pas un bilan fonctionnel retraité en valeurs brutes. Les dividendes reçus des filiales sont inclus dans le résultat financier social, pas dans l'EBE.

ESG signifie ici **État des soldes de gestion**, pas critères environnementaux, sociaux et de gouvernance.

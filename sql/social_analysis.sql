-- IAM SA, CGNC, milliers MAD en entrée; millions MAD en sortie.
-- Les sous-totaux ne sont jamais additionnés avec leurs détails.
SELECT year,
MAX(CASE WHEN statement='Bilan actif' AND code='TOTAL' THEN value END)/1000 AS total_actif_mdh,
MAX(CASE WHEN statement='Bilan passif' AND code='TOTAL' THEN value END)/1000 AS total_passif_mdh
FROM social_reported GROUP BY year;

-- FR fonctionnel sur bilan net de clôture et BFG hors trésorerie.
SELECT year,
(MAX(CASE WHEN statement='Bilan passif' AND code='I' THEN value END)
-MAX(CASE WHEN statement='Bilan actif' AND code='I' THEN value END))/1000 AS fr_mdh,
(MAX(CASE WHEN statement='Bilan actif' AND code='II' THEN value END)
-MAX(CASE WHEN statement='Bilan passif' AND code='II' THEN value END))/1000 AS bfg_mdh
FROM social_reported GROUP BY year;

SELECT a.year,a.value/b.value AS marge_ebe
FROM social_reported a JOIN social_reported b ON a.year=b.year
WHERE a.statement='ESG TFR' AND a.code='V' AND b.statement='CPC' AND b.code='CA';

-- Aucun doublon attendu.
SELECT statement,code,year,COUNT(*) FROM social_reported
GROUP BY statement,code,year HAVING COUNT(*)>1;

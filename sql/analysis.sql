-- SQLite 3; exécuter après chargement par python -m src.pipeline.
-- Contrôle de doublons : aucun résultat attendu.
SELECT year,metric,COUNT(*) n FROM reported GROUP BY year,metric HAVING COUNT(*)>1;
-- Marge ajustée : même base KPI pour le numérateur et le dénominateur.
SELECT a.year,a.value/b.value AS ebitda_margin_adjusted
FROM reported a JOIN reported b ON a.year=b.year
WHERE a.metric='ebitda_adjusted' AND b.metric='revenue_kpi';
-- Croissance IFRS : n'utilise pas le CA KPI 2024.
WITH ca AS (SELECT year,value,LAG(value) OVER(ORDER BY year) previous
FROM reported WHERE metric='revenue_ifrs')
SELECT year,value/previous-1 AS growth FROM ca;

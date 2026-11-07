# Hypothèses et méthode DCF
Toutes les lignes de config/scenarios.csv sont des hypothèses de l'auteur, pas des objectifs de Maroc Telecom.
Valorisation rétrospective au 31/12/2025; flux annuels de fin d'année 2026-2030, MAD nominaux.

|Paramètre|Prudent|Central|Favorable|
|---|---:|---:|---:|
|Croissance annuelle CA|0%|2,5%|4,5%|
|Marge EBITDA|48%|51%|53%|
|D&A / CA|19%|19%|19%|
|CAPEX total / CA|28%|26%|24%|
|BFR normalisé / CA|2%|2%|2%|
|Impôt normatif|35%|35%|35%|
|WACC|11,5%|10%|9%|
|Croissance perpétuelle|1%|2%|2,5%|

Justification : encadrer une stagnation ou une reprise du CA et une pression ou récupération de marge. D&A est une approximation indépendante, pas EBITDA moins EBITA observé. Le CAPEX inclut une enveloppe normalisée de licences; il n'est pas égal au seul ratio hors licences communiqué par la direction. Impôt normatif simplifié, pas un taux fiscal légal affirmé. WACC choisi pour tester le risque, sans prétendre à une calibration CAPM. Les valeurs constantes simplifient le projet et doivent être challengées.

CA(t)=CA(t-1)*(1+croissance). EBITDA=CA*marge. D&A=CA*ratio. EBIT=EBITDA-D&A.
NOPAT=EBIT*(1-impôt). BFR=CA*ratio. BFR 2025 initial=CA2025*ratio 2026 (hypothèse, pas BFR publié).
FCFF=NOPAT+D&A-CAPEX-variation BFR.
VE=somme FCFF(t)/(1+WACC)^t + [FCFF2030*(1+g)/(WACC-g)]/(1+WACC)^5.
WACC doit dépasser g. La sensibilité croise cinq WACC et quatre g sur les flux centraux inchangés.

Les flux consolidés comprennent les filiales non intégralement détenues. Le modèle s'arrête à la VE : aucune soustraction arbitraire des minoritaires comptables. Les effets IFRS16 restent une limite : une valorisation professionnelle nécessite une convention explicite sur les loyers, leurs investissements et la dette de location. Pas de prix cible, de recommandation d'achat ou de promesse de rendement.

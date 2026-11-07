"""Construit le notebook Jupyter lisible. Nécessite requirements-notebook.txt."""
from pathlib import Path
import textwrap
import nbformat as nbf
ROOT=Path(__file__).resolve().parents[1]
def main():
    cells=[]
    def md(s):cells.append(nbf.v4.new_markdown_cell(textwrap.dedent(s).strip()))
    def code(s):cells.append(nbf.v4.new_code_cell(textwrap.dedent(s).strip()))
    md('''
    # Maroc Telecom — analyse financière 2023–2025
    États sociaux IAM SA, ratios, comptes du Groupe et scénarios 2026–2030.

    **Lecture immédiate :** les résultats, tableaux et graphiques sont déjà enregistrés dans ce notebook.
    La version `financial_analysis.html`, placée à côté, s’ouvre dans un navigateur sans Jupyter.

    **Pour recalculer :** décompresser le ZIP complet, ouvrir ce notebook dans Jupyter, choisir le noyau
    Python de l’environnement du projet, puis **Kernel → Restart Kernel and Run All Cells**.
    Installer au préalable `requirements-notebook.txt`. Le lancement Windows est expliqué dans `COMMENT_OUVRIR_LES_FICHIERS.md`.

    Les chiffres publiés, les calculs et les hypothèses sont distingués. Les comptes sociaux IAM SA (CGNC)
    ne sont jamais additionnés aux comptes consolidés du Groupe (IFRS/KPI).
    ''')
    code('''
    from pathlib import Path
    import sys, os, csv, html
    from IPython.display import display, HTML, SVG, Markdown

    # Laisser None si Jupyter est lancé dans le dossier du projet ou dans notebooks/.
    PROJECT_DIR = None
    search = [Path(PROJECT_DIR).expanduser()] if PROJECT_DIR else [Path.cwd(), *Path.cwd().parents]
    ROOT = next((p.resolve() for p in search if (p / "src/model.py").is_file()
                 and (p / "data/raw/social_statements.csv").is_file()), None)
    if ROOT is None:
        raise RuntimeError("Dossier du projet introuvable. Décompressez le ZIP complet, lancez Jupyter "
                           "depuis ce dossier, ou renseignez PROJECT_DIR dans cette cellule.")
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from src.pipeline import main
    from src.model import read, history, forecasts, dcf
    main()
    print("Projet trouvé. Les sorties ont été recalculées avec succès.")
    ''')
    code('''
    # Affichage de tableaux en français : aucune bibliothèque de calcul externe nécessaire.
    def nombre(v, percent=False):
        if v is None or v == "":
            return "n.d."
        value = float(v) * (100 if percent else 1)
        return f"{value:,.2f}".replace(",", " ").replace(".", ",") + (" %" if percent else "")

    def tableau(rows, columns, title=""):
        # columns : (clé, libellé, format), où format vaut texte, nombre, pourcentage ou ratio.
        out = '<div style="font-family:Arial;color:#222;overflow:auto">'
        if title:
            out += '<h3>' + html.escape(title) + '</h3>'
        out += '<table style="border-collapse:collapse;font-size:13px"><thead><tr>'
        out += ''.join('<th style="padding:9px;background:#eee;text-align:left;border-bottom:1px solid #888">'
                       + html.escape(label) + '</th>' for key,label,kind in columns)
        out += '</tr></thead><tbody>'
        for row in rows:
            out += '<tr>'
            for key,label,kind in columns:
                value = row.get(key, '')
                text = str(value) if kind == 'texte' else nombre(value, kind == 'pourcentage')
                if kind == 'ratio' and value != '':
                    text += ' x'
                align = 'left' if kind == 'texte' else 'right'
                out += f'<td style="padding:8px;border-bottom:1px solid #ddd;text-align:{align}">{html.escape(text)}</td>'
            out += '</tr>'
        display(HTML(out + '</tbody></table></div>'))

    colonnes_etats = [('libelle','Poste','texte'),('2023','2023','nombre'),
                     ('2024','2024','nombre'),('2025','2025','nombre'),
                     ('variation_25_24','Variation 2025/2024','nombre')]
    ''')
    md('''
    ## 1. États sociaux publiés — IAM SA seule
    Source : DEU 2025, pages 233–238. Valeurs nettes pour l’actif; montants en millions MAD.
    Les sous-totaux publiés sont conservés. Ils ne doivent pas être additionnés aux lignes de détail.
    ''')
    for file,title in [('bilan_actif','Bilan actif net'),('bilan_passif','Bilan passif'),('cpc','Compte de produits et charges'),('esg','État des soldes de gestion'),('caf','CAF et autofinancement')]:
        code(f'tableau(read("data/tables/{file}.csv"), colonnes_etats, "{title} — MDH")')
    code('''
    tableau(read("data/tables/tableau_financement.csv"),
            [('libelle','Poste','texte')] +
            [(f'{side}_{year}',f'{year} {label}','nombre')
             for year in (2023,2024,2025)
             for side,label in [('emplois','Emplois'),('ressources','Ressources')]],
            "Tableau de financement — MDH")
    ''')
    md('''
    ## 2. Les 19 ratios financiers, avec leur formule
    Ratios calculés sur les comptes sociaux IAM SA. Les taux sont affichés en %, les autres rapports en fois.
    Le ROE et le ROA utilisent les capitaux propres et l’actif de clôture, non leurs moyennes.
    ''')
    code('''
    ratios_sociaux = read("data/tables/ratios_financiers.csv")
    for unite, titre, format_nombre in [("%","Ratios en pourcentage","pourcentage"),
                                        ("fois","Ratios en fois","ratio")]:
        tableau([r for r in ratios_sociaux if r["unite"] == unite],
                [('ratio','Ratio','texte'),('formule','Formule','texte')] +
                [(str(y),str(y),format_nombre) for y in (2023,2024,2025)] +
                [('interpretation','Explication','texte')],titre)
    ''')
    code('''
    tableau(read("data/tables/equilibre_financier.csv"),
            [('indicateur','Indicateur','texte')] + [(str(y),str(y),'nombre') for y in (2023,2024,2025)],
            "Fonds de roulement, besoin de financement global et trésorerie — MDH")
    ''')
    md('''
    **Lecture :** l’EBE social baisse en 2025, tandis que le résultat net augmente avec le redressement
    du résultat non courant. La rentabilité nette ne mesure donc pas uniquement l’activité récurrente.
    La liquidité générale reste inférieure à 1; les échéances et le cycle d’exploitation doivent être examinés.
    Ces observations ne constituent pas un avis d’audit.
    ''')
    md('''
    ## 3. Groupe consolidé — périmètre distinct des comptes sociaux
    Les séries IFRS et KPI ajustés ne sont pas confondues : en 2024, le CA IFRS S2 est de 36 699 MDH,
    contre 36 704 MDH dans la série KPI S1. Le dictionnaire documente les écarts entre publications.
    ''')
    code('''
    groupe = [dict(annee=y, **v) for y,v in history().items()]
    tableau(groupe,[('annee','Année','texte'),('revenue_ifrs','CA IFRS','nombre'),
                   ('revenue_kpi','CA KPI','nombre'),('ebitda_adjusted','EBITDA ajusté','nombre'),
                   ('ebita_adjusted','EBITA ajusté','nombre'),('net_income_group','Résultat net part Groupe IFRS','nombre')],
            "Indicateurs du Groupe — MDH")
    display(SVG(filename=str(ROOT / "charts/historical.svg")))
    ''')
    md('''
    ## 4. Scénarios 2026–2030 et DCF — hypothèses de l’auteur
    Prévisions rétrospectives sur base FY2025. Aucune publication 2026 n’est intégrée.
    Les hypothèses sont dans `config/scenarios.csv`; elles ne sont pas des engagements de Maroc Telecom.
    Les trois scénarios sont calculés séparément, sans mélanger leurs flux.
    ''')
    code('''
    hypotheses = read("config/scenarios.csv")
    tableau([r for r in hypotheses if r['year']=='2026'],
            [('scenario','Scénario','texte'),('revenue_growth','Croissance CA','pourcentage'),
             ('ebitda_margin','Marge EBITDA','pourcentage'),('capex_total_ratio','CAPEX total / CA','pourcentage'),
             ('tax_rate','Impôt normatif','pourcentage'),('wacc','WACC','pourcentage'),
             ('terminal_growth','Croissance perpétuelle','pourcentage')],
            "Hypothèses 2026, constantes jusqu’en 2030 dans le modèle")
    projections = forecasts(history(), hypotheses)
    for scenario in ['prudent','central','favorable']:
        tableau([r for r in projections if r['scenario']==scenario],
                [('year','Année','texte'),('revenue','CA','nombre'),('ebitda','EBITDA','nombre'),
                 ('capex_total','CAPEX total','nombre'),('delta_nwc','Variation BFR','nombre'),('fcff','FCFF','nombre')],
                f"Scénario {scenario} — projections en MDH")
    ''')
    code('''
    valorisations = [dcf([r for r in projections if r['scenario']==s])
                    for s in ['prudent','central','favorable']]
    tableau(valorisations,[('scenario','Scénario','texte'),('enterprise_value','Valeur d’entreprise, MDH','nombre'),
                          ('wacc','WACC','pourcentage'),('terminal_growth','Croissance perpétuelle','pourcentage'),
                          ('terminal_share','Part terminale','pourcentage')],
            "DCF pédagogique au 31/12/2025")
    display(SVG(filename=str(ROOT / "charts/forecast.svg")))
    display(SVG(filename=str(ROOT / "charts/fcff.svg")))
    ''')
    md('''
    FCFF = EBIT × (1 − impôt normatif) + D&A − CAPEX − variation du BFR.
    Le DCF actualise les flux de fin d’année et une valeur terminale de Gordon-Shapiro.
    Il s’arrête à la valeur d’entreprise consolidée : aucun cours cible n’est calculé.
    Les limites sur les minoritaires et IFRS 16 figurent dans `docs/methodology.md`.
    ''')
    md('## 5. Requête SQL sur les états sociaux')
    code('''
    import sqlite3
    with sqlite3.connect(str(ROOT / "data/processed/analysis.sqlite")) as con:
        query = """
        SELECT year AS annee,
          MAX(CASE WHEN statement='CPC' AND code='CA' THEN value END)/1000 AS ca,
          MAX(CASE WHEN statement='ESG TFR' AND code='V' THEN value END)/1000 AS ebe,
          MAX(CASE WHEN statement='CPC' AND code='XIII' THEN value END)/1000 AS resultat_net
        FROM social_reported GROUP BY year ORDER BY year
        """
        cur = con.execute(query)
        sql_rows = [dict(zip([c[0] for c in cur.description], row)) for row in cur.fetchall()]
    tableau(sql_rows,[('annee','Année','texte'),('ca','CA social','nombre'),
                      ('ebe','EBE social','nombre'),('resultat_net','Résultat net social','nombre')],
            "Résultats SQL — MDH")
    ''')
    md('## 6. Contrôles et sources')
    code('''
    checks = read("data/processed/statement_checks.csv")
    assert len(checks) == 45
    assert all(r['resultat'] == 'OK' for r in checks)
    print("45 rapprochements sociaux dans la tolérance de 0,005 MDH.")
    import subprocess
    result = subprocess.run([sys.executable,"-m","unittest","discover","-s","tests","-v"],
                            cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace',
                            env={**os.environ, 'PYTHONIOENCODING':'utf-8'})
    print(result.stdout + result.stderr)
    result.check_returncode()
    ''')
    code('''
    tableau(read("data/raw/sources.csv"),
            [('source_id','Source','texte'),('title','Publication','texte'),
             ('locator','Tableau / pages','texte'),('url','Lien','texte')],
            "Sources vérifiées et localisateurs")
    ''')
    md('''
    ## Fichiers pour une lecture sans logiciel de programmation
    - `LIRE_LES_TABLEAUX.html` : tous les états et ratios, ouverts dans un navigateur.
    - `reports/Rapport_Court_Maroc_Telecom.pdf` : synthèse en cinq pages.
    - `workbook/Maroc_Telecom_Etats_Sociaux.xlsx` : dix onglets, formules et graphiques.
    - `dashboards/dashboard.html` : dashboard interactif local.

    L’ETIC complet reste dans le document officiel. Le projet PBIP est un fichier de développement Power BI;
    son affichage dans Desktop n’a pas été validé et aucun PBIX final n’est revendiqué.
    ''')
    nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3 (ipykernel)','language':'python','name':'python3'},'language_info':{'name':'python'}})
    target=ROOT/'notebooks/financial_analysis.ipynb';nbf.validate(nb);nbf.write(nb,target)
    print(f'Notebook construit : {len(cells)} cellules.')
if __name__=='__main__':main()

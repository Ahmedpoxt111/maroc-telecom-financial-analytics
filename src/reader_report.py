"""États financiers et ratios en français, lisibles sans exécuter de code."""
from src.model import ROOT,read,write
import json,html

def financing():
    source=read('data/raw/financing.csv');rows=[]
    for r in source:
        rows.append({**r,**{k:float(r[k])/1000 if r[k]!='' else '' for k in ('emplois_2023','ressources_2023','emplois_2024','ressources_2024','emplois_2025','ressources_2025')}})
    return rows

def ratio_definitions():
    # Références communes aux calculs Python et aux formules Excel.
    return [
    ('Croissance du chiffre d’affaires','CA / CA de l’année précédente − 1','pct','growth','Évolution annuelle du CA; 2023 indisponible sans 2022.'),
    ('Taux de valeur ajoutée','Valeur ajoutée / chiffre d’affaires','pct',('ESG','IV','CPC','CA'),'Part du CA correspondant à la valeur ajoutée sociale.'),
    ('Marge brute d’exploitation','EBE / chiffre d’affaires','pct',('ESG','V','CPC','CA'),'Performance avant dotations et résultat financier.'),
    ('Marge d’exploitation','Résultat d’exploitation / chiffre d’affaires','pct',('CPC','III','CPC','CA'),'Performance après dotations d’exploitation.'),
    ('Marge nette','Résultat net / chiffre d’affaires','pct',('CPC','XIII','CPC','CA'),'Inclut résultats financier et non courant; pas une marge récurrente.'),
    ('Rentabilité des capitaux propres — ROE','Résultat net / capitaux propres de clôture','pct',('CPC','XIII','Bilan passif','A'),'Rentabilité comptable sur capitaux propres de clôture, non moyens.'),
    ('Rentabilité de l’actif — ROA','Résultat net / actif total de clôture','pct',('CPC','XIII','Bilan actif','TOTAL'),'Rentabilité comptable de l’actif, affectée par les éléments non récurrents.'),
    ('Rotation de l’actif','Chiffre d’affaires / actif total de clôture','times',('CPC','CA','Bilan actif','TOTAL'),'CA produit pour un dirham d’actif de clôture.'),
    ('Autonomie financière','Capitaux propres / actif total','pct',('Bilan passif','A','Bilan actif','TOTAL'),'Part du bilan financée par les capitaux propres.'),
    ('Poids des passifs hors capitaux propres','(Total passif − capitaux propres) / total passif','pct','liabilities','Inclut dettes d’exploitation et provisions; distinct de la seule dette financière.'),
    ('Liquidité générale','(Actif circulant + trésorerie actif) / (passif circulant + trésorerie passif)','times','current','Inférieure à 1 sur les trois années : examiner les échéances; ce seul ratio ne prouve pas une insolvabilité.'),
    ('Liquidité réduite','(Actif circulant − stocks + trésorerie actif) / passifs à court terme','times','quick','Même périmètre que la liquidité générale, hors stocks.'),
    ('Liquidité immédiate','Trésorerie actif / (passif circulant + trésorerie passif)','pct','cash','Trésorerie disponible au bilan rapportée aux passifs à court terme.'),
    ('Couverture des immobilisations','Financement permanent / actif immobilisé net','times',('Bilan passif','I','Bilan actif','I'),'Inférieure à 1 : fonds de roulement fonctionnel négatif sur bilan net.'),
    ('Dette financière brute / capitaux propres','(Dettes de financement + trésorerie passif) / capitaux propres','times','debt_equity','Définition sociale simplifiée; ne pas confondre avec la dette nette du Groupe.'),
    ('Dette financière nette / EBE','(Dettes de financement + trésorerie passif − trésorerie actif) / EBE','times','leverage','Dette nette simplifiée hors placements, divisée par l’EBE social.'),
    ('Couverture des charges d’intérêts','EBE / charges d’intérêts','times',('ESG','V','CPC','CF1'),'Couverture comptable des intérêts par l’EBE, pas un covenant bancaire.'),
    ('CAF / chiffre d’affaires','Capacité d’autofinancement / chiffre d’affaires','pct',('CAF','I','CPC','CA'),'CAF publiée dans l’ESG; distincte du cash-flow d’exploitation IFRS.'),
    ('Taux de distribution sur CAF','Distributions de bénéfices / CAF','pct',('CAF','10','CAF','I'),'Flux de distribution de l’exercice, pas dividende voté au titre du même exercice.'),
    ]

def build(d,annual):
    ds={**d,'ESG':d['ESG TFR']};ratios=[]
    for name,formula,unit,rule,note in ratio_definitions():
        vals={}
        for y in (2023,2024,2025):
            a=lambda c:ds['Bilan actif'][c][y]
            p=lambda c:ds['Bilan passif'][c][y]
            v=None
            if isinstance(rule,tuple):
                tn,n,td,de=rule;den=ds[td][de][y];v=ds[tn][n][y]/den if den else None
            elif rule=='growth':v=ds['CPC']['CA'][y]/ds['CPC']['CA'][y-1]-1 if y>2023 else None
            elif rule=='liabilities':v=(p('TOTAL')-p('A'))/p('TOTAL')
            elif rule=='current':v=(a('II')+a('III'))/(p('II')+p('III'))
            elif rule=='quick':v=(a('II')-a('F')+a('III'))/(p('II')+p('III'))
            elif rule=='cash':v=a('III')/(p('II')+p('III'))
            elif rule=='debt_equity':v=(p('C')+p('III'))/p('A')
            elif rule=='leverage':v=(p('C')+p('III')-a('III'))/ds['ESG']['V'][y]
            vals[str(y)]=v if v is not None else ''
        ratios.append(dict(ratio=name,formule=formula,unite='%' if unit=='pct' else 'fois',**vals,interpretation=note,statut='Calculé sur comptes sociaux IAM SA'))
    write('data/tables/ratios_financiers.csv',ratios)
    fin=financing();write('data/tables/tableau_financement.csv',fin)
    rows=[dict(indicateur=label,**{str(a['annee']):a[key] for a in annual},statut='Calculé sur bilan social net') for label,key in [('Financement permanent','financement_permanent'),('Actif immobilisé net','actif_immobilise'),('Fonds de roulement fonctionnel','fr'),('Actif circulant hors trésorerie','actif_circulant'),('Passif circulant hors trésorerie','passif_circulant'),('Besoin de financement global','bfg'),('Trésorerie nette','tresorerie_nette')]]
    write('data/tables/equilibre_financier.csv',rows)
    return ratios,fin,rows

def report(out,ratios,fin,masses):
    esc=lambda s:html.escape(str(s))
    def num(v,unit=''):
        if v=='':return 'n.d.'
        value=float(v)*(100 if unit=='%' else 1)
        return f'{value:,.2f}'.replace(',',' ').replace('.',',')+(' %' if unit=='%' else ' x' if unit=='fois' else '')
    def tbl(rows,columns,unit=''):
        s='<div class="scroll"><table><thead><tr>'+''.join('<th>'+esc(label)+'</th>' for k,label in columns)+'</tr></thead><tbody>'
        for r in rows:
            s+='<tr class="'+r.get('type_ligne','')+'">'
            for k,label in columns:
                val=r[k];numeric=k in ['2023','2024','2025','variation_25_24'] or k.startswith(('emplois_','ressources_'))
                s+='<td'+(' class="n"' if numeric else '')+'>'+(num(val,r.get('unite',unit)) if numeric else esc(val))+'</td>'
            s+='</tr>'
        return s+'</tbody></table></div>'
    items=[('bilan-actif','1. Bilan actif'),('bilan-passif','2. Bilan passif'),('cpc','3. CPC'),('esg','4. ESG'),('caf','5. CAF et autofinancement'),('financement','6. Tableau de financement'),('ratios','7. Ratios financiers'),('equilibre','8. Équilibre financier'),('graphiques','9. Graphiques'),('annexes','10. Annexes et sources')]
    nav=''.join(f'<a href="#{i}">{label}</a>' for i,label in items)
    body='<header><div>MAROC TELECOM · IAM SA</div><h1>États de synthèse et analyse des ratios</h1><p>2023 · 2024 · 2025 — Comptes sociaux, référentiel marocain CGNC</p></header><main><div class="note"><b>Lecture directe :</b> tous les tableaux sont affichés ci-dessous. Montants en millions de dirhams (MDH). Les données publiées sont distinguées des ratios calculés. Ce dossier concerne IAM SA seule; les comptes du Groupe et les prévisions restent séparés.</div><nav>'+nav+'</nav>'
    for (statement,anchor,title,page) in [('Bilan actif','bilan-actif','1. Bilan actif — valeurs nettes','233'),('Bilan passif','bilan-passif','2. Bilan passif','234'),('CPC','cpc','3. Compte de produits et charges (CPC)','235–236'),('ESG TFR','esg','4. État des soldes de gestion (ESG)','237'),('CAF','caf','5. Capacité d’autofinancement et autofinancement','237')]:
        body+=f'<section id="{anchor}"><h2>{title}</h2><p class="scope">Chiffres publiés · DEU 2025, page {page} · MDH</p>'+tbl(out['tables'][statement],[('libelle','Poste'),('2023','2023'),('2024','2024'),('2025','2025'),('variation_25_24','Variation 2025/2024')])+'</section>'
    body+='<section id="financement"><h2>6. Tableau de financement — emplois et ressources</h2><p class="scope">Chiffres publiés · DEU 2025, page 238 · MDH. Une cellule vide signifie non renseignée dans la colonne source. Les sous-totaux ne s’additionnent pas avec leurs détails.</p>'+tbl(fin,[('libelle','Poste'),('emplois_2023','2023 Emplois'),('ressources_2023','2023 Ressources'),('emplois_2024','2024 Emplois'),('ressources_2024','2024 Ressources'),('emplois_2025','2025 Emplois'),('ressources_2025','2025 Ressources')])+'</section>'
    body+='<section id="ratios"><h2>7. Ratios financiers — noms, formules et résultats</h2><p class="scope">19 ratios calculés exclusivement sur les comptes sociaux IAM SA. « n.d. » : non disponible. Les taux sont exprimés en %, les rapports en fois.</p>'+tbl(ratios,[('ratio','Ratio'),('formule','Formule'),('2023','2023'),('2024','2024'),('2025','2025'),('interpretation','Lecture du ratio')])+'</section>'
    body+='<section id="equilibre"><h2>8. Équilibre financier</h2><p class="scope">Calculé à partir des masses du bilan social net, MDH. Écarts d’arrondis possibles par rapport aux masses publiées page 238.</p>'+tbl(masses,[('indicateur','Indicateur'),('2023','2023'),('2024','2024'),('2025','2025')])+'</section>'
    body+='<section id="graphiques"><h2>9. Graphiques</h2><div class="charts">'
    # Graphiques SVG incorporés : aucun chemin de fichier externe.
    for label,keys in [('Performance sociale',['ca','ebe','caf']),('Trésorerie et équilibre',['fr','bfg','tresorerie_nette'])]:
        labels={'ca':'CA','ebe':'EBE','caf':'CAF','fr':'Fonds de roulement','bfg':'BFG','tresorerie_nette':'Trésorerie nette'}
        allv=[r[k] for r in out['annual'] for k in keys];lo=min(0,min(allv))*1.1;hi=max(0,max(allv))*1.1
        def Y(v):return 265-(v-lo)/(hi-lo)*210
        svg=f'<article><h3>{label} (MDH)</h3><svg viewBox="0 0 660 350" role="img" aria-label="{label}">'
        for j in range(5):
            v=lo+(hi-lo)*j/4;y=Y(v);svg+=f'<line x1="80" y1="{y}" x2="610" y2="{y}" stroke="#DDDDDD"/><text x="70" y="{y+4}" text-anchor="end" font-size="12">{num(v)}</text>'
        for j,y in enumerate([2023,2024,2025]):svg+=f'<text x="{100+j*240}" y="292" text-anchor="middle" font-size="13">{y}</text>'
        for i,k in enumerate(keys):
            color=['#222222','#666666','#999999'][i];pts=' '.join(f'{100+j*240},{Y(r[k])}' for j,r in enumerate(out['annual']))
            svg+=f'<polyline points="{pts}" stroke="{color}" stroke-width="3" fill="none"/><text x="{35+i*205}" y="330" font-size="13" fill="{color}">{labels[k]}</text>'
        body+=svg+'</svg></article>'
    body+='</div></section><section id="annexes"><h2>10. Annexes et sources</h2><p>Source principale : <a href="https://www.ammc.ma/sites/default/files/Maroc_Telecom_Document_enregistrement_universel_2025.pdf">Maroc Telecom — Document d’enregistrement universel 2025</a>, pages 233–238. Données transcrites en milliers MAD puis converties en MDH, sans modification des sous-totaux publiés.</p><p><b>ETIC :</b> l’État des informations complémentaires complet figure dans le document officiel, pages 239–255. Il n’est pas reproduit intégralement dans ce dossier analytique.</p><p><b>Arrondis :</b> marge brute 2023 publiée à −12,632 MDH, contre −12,631 MDH recalculés sur les postes arrondis. Les écarts de rapprochement sont affichés et une tolérance de 0,005 MDH est appliquée; aucun chiffre n’est ajusté artificiellement.</p><p><b>Interprétation :</b> le résultat net 2025 se redresse avec le résultat non courant, tandis que l’EBE baisse. Les ratios de résultat net ne représentent donc pas exclusivement la performance récurrente. Les ratios de liquidité nécessitent une lecture des échéances et du cycle d’exploitation.</p><p>Les comptes consolidés et le DCF 2026–2030 sont disponibles dans le dépôt, dans des tables séparées. La valorisation est pédagogique, fondée sur des hypothèses explicites.</p></section></main>'
    css='body{margin:0;background:#FFFFFF;color:#222222;font:15px/1.6 Arial}header{padding:32px max(24px,calc((100vw - 1400px)/2));background:#FFFFFF;color:#222222;border-bottom:1px solid #BBBBBB}header div{font-size:13px;letter-spacing:2px}h1{margin:8px 0;font-size:32px}header p{margin:0;color:#444444}main{max-width:1400px;margin:auto;padding:24px}nav{display:flex;flex-wrap:wrap;gap:10px;margin:20px 0}a{color:#333333}nav a{padding:9px 15px;background:white;border:1px solid #CCCCCC;border-radius:0;text-decoration:none}section{margin:32px 0;padding:22px;background:white;border:1px solid #CCCCCC;border-radius:0;scroll-margin-top:16px}h2{font-size:23px;margin:0;color:#222222}.scope{font-size:13px;color:#555555}table{border-collapse:collapse;width:100%;font-size:14px}th{text-align:left;background:#EEEEEE;padding:12px;border-bottom:2px solid #AAAAAA}td{padding:9px 12px;border-bottom:1px solid #DDDDDD;min-width:95px;vertical-align:top}.n{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}td:first-child{min-width:260px}tr.subtotal td,tr.total td{font-weight:bold;background:#F7F7F7}tr.grand_total td{font-weight:bold;background:#E6E6E6;border-top:2px solid #222222}.scroll{overflow:auto}.note{padding:18px;background:#F4F4F4;border-left:4px solid #222222}.charts{display:grid;grid-template-columns:1fr 1fr;gap:20px}svg{width:100%;height:auto}#ratios td:first-child{min-width:220px}#ratios td:nth-child(2){min-width:250px}#ratios td:last-child{min-width:270px}@media(max-width:900px){.charts{grid-template-columns:1fr}h1{font-size:25px}main{padding:12px}section{padding:14px}}@media print{nav{display:none}body{background:white}section{break-before:page;border:none;padding:0}.scroll{overflow:visible}table{font-size:9px}td{min-width:0!important;padding:4px}.charts{break-inside:avoid}header{background:white;color:#222222}header p{color:#222222}}'
    return '<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Maroc Telecom — Bilans, CPC, ESG et ratios</title><style>'+css+'</style>'+body+'</html>'

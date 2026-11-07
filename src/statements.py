from src.model import ROOT,read,write,history
import json,html,sqlite3
def social_data():
    rows=read('data/raw/social_statements.csv');d={}
    for r in rows:d.setdefault(r['statement'],{}).setdefault(r['code'],{})[int(r['year'])]=int(r['value'])/1000
    return rows,d
def main():
    rows,d=social_data();checks=[];annual=[];tables={}
    for statement in d:
        first=[r for r in rows if r['statement']==statement and r['year']=='2023'];view=[]
        for r in first:
            values=d[statement][r['code']];prev=values[2024]
            view.append(dict(code=r['code'],libelle=r['label'],**{str(y):values[y] for y in (2023,2024,2025)},variation_25_24=values[2025]-prev,variation_pct_25_24=(values[2025]/prev-1) if prev else '',type_ligne=r['row_type'],source='S4',page=r['page']))
        filename={'Bilan actif':'bilan_actif','Bilan passif':'bilan_passif','CPC':'cpc','ESG TFR':'esg','CAF':'caf'}[statement]
        write('data/tables/'+filename+'.csv',view);tables[statement]=view
    for y in (2023,2024,2025):
        a=lambda c:d['Bilan actif'][c][y]
        p=lambda c:d['Bilan passif'][c][y]
        c=lambda k:d['CPC'][k][y]
        e=lambda k:d['ESG TFR'][k][y]
        f=lambda k:d['CAF'][k][y]
        values=dict(annee=y,ca=c('CA'),ebe=e('V'),valeur_ajoutee=e('IV'),resultat_exploitation=c('III'),resultat_financier=c('VI'),resultat_non_courant=c('X'),resultat_net=c('XIII'),caf=f('I'),autofinancement=f('II'),actif_total=a('TOTAL'),capitaux_propres=p('A'),actif_immobilise=a('I'),actif_circulant=a('II'),passif_circulant=p('II'),financement_permanent=p('I'),tresorerie_actif=a('III'),tresorerie_passif=p('III'))
        values.update(fr=p('I')-a('I'),bfg=a('II')-p('II'),tresorerie_nette=a('III')-p('III'),marge_ebe=e('V')/c('CA'),marge_nette=c('XIII')/c('CA'),autonomie=p('A')/a('TOTAL'))
        annual.append(values)
        tests={
          'Total actif - total passif':a('TOTAL')-p('TOTAL'),
          'Actif immobilisé + circulant + trésorerie - total':a('I')+a('II')+a('III')-a('TOTAL'),
          'Financement permanent + passif circulant + trésorerie - total':p('I')+p('II')+p('III')-p('TOTAL'),
          'Produits exploitation - charges exploitation - résultat':c('I')-c('II')-c('III'),
          'Produits financiers - charges financières - résultat':c('IV')-c('V')-c('VI'),
          'Résultat exploitation + financier - courant':c('III')+c('VI')-c('VII'),
          'Produits non courants - charges non courantes - résultat':c('VIII')-c('IX')-c('X'),
          'Résultat avant impôts - IS - résultat net':c('XI')-c('XII')-c('XIII'),
          'Marge brute calculée - publiée':e('1')-e('2')-e('I'),
          'Valeur ajoutée calculée - publiée':e('I')+e('II')-e('III')-e('IV'),
          'EBE calculé - publié':e('IV')+e('8')-e('9')-e('10')-e('V'),
          'CAF calculée - publiée':f('1')+f('2')+f('3')+f('4')-f('5')-f('6')-f('7')-f('8')+f('9')-f('I'),
          'CAF - distributions - autofinancement':f('I')-f('10')-f('II'),
          'FR - BFG - trésorerie nette':values['fr']-values['bfg']-values['tresorerie_nette'],
          'Résultat net CPC - résultat net ESG':c('XIII')-e('X')}
        for name,diff in tests.items():checks.append(dict(annee=y,controle=name,ecart_mdh=round(diff,6),tolerance_mdh=.005,resultat='OK' if abs(diff)<.00500001 else 'ECART',statut='calculated'))
    write('data/processed/social_analysis.csv',annual);write('dashboards/finance_sociale.csv',annual);write('data/processed/statement_checks.csv',checks)
    db=sqlite3.connect(ROOT/'data/processed/analysis.sqlite')
    db.execute('DROP TABLE IF EXISTS social_reported')
    db.execute('CREATE TABLE social_reported (entity TEXT, basis TEXT, statement TEXT, row_order INTEGER, code TEXT, label TEXT, year INTEGER, value REAL, unit TEXT, row_type TEXT, status TEXT, source_id TEXT, page INTEGER, PRIMARY KEY(statement,code,year))')
    db.executemany('INSERT INTO social_reported VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',[tuple(r.values()) for r in rows])
    db.commit()
    q='\n'.join(l for l in (ROOT/'sql/social_analysis.sql').read_text(encoding='utf-8').splitlines() if not l.lstrip().startswith('--'))
    for sql in q.split(';'):
        if sql.strip():db.execute(sql).fetchall()
    db.close()
    out={'tables':tables,'annual':annual,'checks':checks,'group':history(),'forecasts':read('data/processed/forecasts.csv'),'dcf':read('data/processed/dcf.csv'),'sources':read('data/raw/sources.csv')}
    from src.reader_report import build,report
    ratios,fin,masses=build(d,annual)
    out.update(ratios_fr=ratios,financement=fin,masses=masses)
    (ROOT/'data/processed/dashboard_data.json').write_text(json.dumps(out,ensure_ascii=False),encoding='utf-8')
    template=(ROOT/'dashboards/template.html').read_text(encoding='utf-8')
    dashboard=template.replace('/*DATA*/',json.dumps(out,ensure_ascii=False).replace('</',r'<\/'))
    (ROOT/'dashboards/dashboard.html').write_text(dashboard,encoding='utf-8')
    readable=report(out,ratios,fin,masses)
    (ROOT/'reports/etats_de_synthese_et_ratios.html').write_text(readable,encoding='utf-8')
    # Point d'entrée à la racine du dépôt, sans besoin de choisir un sous-dossier.
    (ROOT/'LIRE_LES_TABLEAUX.html').write_text(readable,encoding='utf-8')
    print(f'États sociaux : {len(rows)} observations, {len(checks)} contrôles, {sum(c["resultat"]!="OK" for c in checks)} écarts hors tolérance.')
if __name__=='__main__':main()

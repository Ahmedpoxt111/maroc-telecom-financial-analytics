from src.model import *
import sqlite3,html
def chart(name,title,years,series):
    colors=['#222222','#666666','#999999']; vmax=max(max(v) for v in series.values())*1.15
    s=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="520" viewBox="0 0 1000 520">','<rect width="1000" height="520" fill="#FFFFFF"/>',f'<text x="60" y="40" font-family="Arial" font-size="23">{html.escape(title)}</text>','<text x="60" y="66" font-family="Arial" font-size="14">Millions MAD | Sources et hypothèses : README</text>']
    for i in range(6):
        y=420-i*60;value=vmax*i/5
        s.extend([f'<path d="M90 {y} H950" stroke="#DDDDDD"/>',f'<text x="8" y="{y+5}" font-family="Arial" font-size="13">{value:,.0f}</text>'])
    for j,year in enumerate(years): s.append(f'<text x="{90+j*860/(len(years)-1)}" y="445" font-family="Arial" font-size="14">{year}</text>')
    for i,(label,values) in enumerate(series.items()):
        pts=' '.join(f'{90+j*860/(len(years)-1)},{420-v/vmax*300}' for j,v in enumerate(values))
        s.extend([f'<polyline points="{pts}" fill="none" stroke="{colors[i]}" stroke-width="3"/>',f'<text x="{60+i*305}" y="490" fill="{colors[i]}" font-family="Arial" font-size="15">{html.escape(label)}</text>'])
    (ROOT/'charts'/name).write_text(''.join(s)+'</svg>',encoding='utf-8')
def main():
    d=history();a=read('config/scenarios.csv');r=ratios(d);f=forecasts(d,a)
    vals=[dcf([x for x in f if x['scenario']==s]) for s in sorted({x['scenario'] for x in f})]
    central=[x for x in f if x['scenario']=='central']
    sensitivity=[dcf(central,w,g) for w in (.08,.09,.10,.11,.12) for g in (0,.01,.02,.03)]
    write('data/processed/ratios.csv',r);write('data/processed/forecasts.csv',f);write('data/processed/dcf.csv',vals);write('data/processed/sensitivity.csv',sensitivity)
    hist=[dict(year=y,**v) for y,v in d.items()];write('data/processed/historical_wide.csv',hist)
    long=[]
    for y,v in d.items():
        for k,value in v.items(): long.append(dict(year=y,scenario='historique',metric=k,value=value,unit='million_MAD',status='reported'))
    for row in f:
        for k in ('revenue','ebitda','fcff','capex_total'):
            long.append(dict(year=row['year'],scenario=row['scenario'],metric=k,value=row[k],unit='million_MAD',status='forecast'))
    write('dashboards/powerbi_financials.csv',long)
    db=sqlite3.connect(':memory:')
    db.executescript((ROOT/'sql/schema.sql').read_text())
    for row in read('data/raw/reported_financials.csv'): db.execute('INSERT INTO reported VALUES (?,?,?,?,?,?,?,?)',tuple(row.values()))
    db.commit()
    query_text='\n'.join(line for line in (ROOT/'sql/analysis.sql').read_text(encoding='utf-8').splitlines() if not line.lstrip().startswith('--'))
    for sql in query_text.split(';'):
        if sql.strip(): db.execute(sql).fetchall()
    backup=sqlite3.connect(ROOT/'data/processed/analysis.sqlite');db.backup(backup);backup.close();db.close()
    (ROOT/'charts').mkdir(exist_ok=True)
    chart('historical.svg','Historique : indicateurs ajustés publiés',list(d),{'CA KPI':[v['revenue_kpi'] for v in d.values()],'EBITDA ajusté':[v['ebitda_adjusted'] for v in d.values()],'EBITA ajusté':[v['ebita_adjusted'] for v in d.values()]})
    chart('forecast.svg','Prévisions de CA : hypothèses de scénarios',list(range(2025,2031)),{s:[d[2025]['revenue_kpi']]+[x['revenue'] for x in f if x['scenario']==s] for s in ('prudent','central','favorable')})
    chart('fcff.svg','FCFF modélisé : hypothèses de scénarios',list(range(2026,2031)),{s:[x['fcff'] for x in f if x['scenario']==s] for s in ('prudent','central','favorable')})
    lines=['# Rapport financier et audit des données','', 'Unité : millions MAD. Modèle pédagogique, valorisation au 31/12/2025.', '', '## Diagnostic historique', '',f"Le CA KPI varie de {(d[2025]['revenue_kpi']/d[2023]['revenue_kpi']-1)*100:.2f}% entre 2023 et 2025. La marge EBITDA ajustée passe de {r[0]['ebitda_margin_adjusted']*100:.2f}% à {r[-1]['ebitda_margin_adjusted']*100:.2f}%. Ce sont des calculs à partir de S1.", '', 'La progression du résultat IFRS 2025 ne représente pas une croissance récurrente : le litige Wana affecte les comparatifs (S2, p.24). La liquidité générale reste inférieure à 1; cela appelle une revue des échéances, sans suffire à diagnostiquer une cessation de paiement.', '', '## Scénarios DCF', '', '|Scénario|VE indicative|Part terminale|','|---|---:|---:|']
    lines += [f"|{v['scenario']}|{v['enterprise_value']:,.1f}|{v['terminal_share']:.1%}|" for v in vals]
    lines += ['', 'La VE couvre les flux consolidés. Aucun cours cible ni valeur des capitaux propres de la société mère : les intérêts minoritaires devraient être valorisés au marché, les participations et les locations réconciliées avant un pont VE-actions. La valeur comptable des minoritaires ne constitue pas cette valorisation.', '', '## Limites et pistes de contrôle', '', 'Trois observations annuelles ne permettent pas de valider statistiquement une prévision. Pas de backtest revendiqué. Prévisions figées sur base FY2025, sans intégrer les publications 2026 disponibles à la date de collecte; ce n’est pas une prévision en temps réel.', '', 'BFR proxy = stocks + créances et autres - dettes exploitation : périmètre large, distinct du BFR opérationnel normalisé utilisé en DCF. ROE calculé sur capitaux propres de clôture. FCF cash proxy = CFO - acquisitions cash + cessions, distinct du FCFF et du CFFO communiqué. Les investissements KPI ne sont pas les décaissements du tableau de flux.', '', 'Contrôles prioritaires : justification des écarts de publication, circularisation dette/banques, maturité des passifs courants, licences et CAPEX, événements non récurrents, recouvrabilité clients. Aucun avis d’audit émis.', '', 'Sources et traçabilité : data/raw/sources.csv et docs/data_dictionary.md.']
    (ROOT/'reports').mkdir(exist_ok=True);(ROOT/'reports/financial_report.md').write_text('\n'.join(lines),encoding='utf-8')
    blocks=[];in_table=False
    for line in lines:
        if line.startswith('|'):
            if '|---' in line:continue
            if not in_table:blocks.append('<table>');in_table=True
            blocks.append('<tr>'+''.join('<td>'+html.escape(c)+'</td>' for c in line.strip('|').split('|'))+'</tr>')
        else:
            if in_table:blocks.append('</table>');in_table=False
            if line.startswith('# '):blocks.append('<h1>'+html.escape(line[2:])+'</h1>')
            elif line.startswith('## '):blocks.append('<h2>'+html.escape(line[3:])+'</h2>')
            elif line:blocks.append('<p>'+html.escape(line)+'</p>')
    if in_table:blocks.append('</table>')
    body=''.join(blocks)
    (ROOT/'reports/financial_report.html').write_text('<!doctype html><html lang="fr"><meta charset="utf-8"><title>Maroc Telecom | Analyse</title><style>body{max-width:1000px;margin:40px auto;font:17px/1.6 Arial;color:#18334c;padding:20px}img{width:100%}h1,h2{color:#222222}td{padding:10px 24px;border-bottom:1px solid #DDDDDD}table{border-collapse:collapse;width:100%}tr:first-child{font-weight:bold;background:#eef4f7}</style>'+body+''.join(f'<img alt="{n}" src="../charts/{n}.svg">' for n in ('historical','forecast','fcff'))+'</html>',encoding='utf-8')
    from src.statements import main as build_statements
    build_statements()
    print('Pipeline OK : CSV, SQLite, graphiques SVG, états sociaux et dashboard générés.')
if __name__=='__main__':main()

import csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(path):
    with (ROOT/path).open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))
def write(path,rows):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8',newline='') as f:
        fields=list(dict.fromkeys(k for row in rows for k in row))
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def history():
    d={y:{} for y in (2023,2024,2025)}
    for r in read('data/raw/reported_financials.csv'): d[int(r['year'])][r['metric']]=float(r['value'])
    return d
def ratios(d):
    out=[]
    for y,v in sorted(d.items()):
        out.append(dict(year=y,status='calculated',revenue_growth_ifrs=v['revenue_ifrs']/d[y-1]['revenue_ifrs']-1 if y-1 in d else '',ebitda_margin_adjusted=v['ebitda_adjusted']/v['revenue_kpi'],ebita_margin_adjusted=v['ebita_adjusted']/v['revenue_kpi'],net_margin_ifrs=v['net_income_total']/v['revenue_ifrs'],current_ratio=v['current_assets']/v['current_liabilities'],equity_ratio=v['equity_total']/v['assets'],roe_group_closing=v['net_income_group']/v['equity_group'],net_debt_simple=v['debt_lt']+v['debt_st']-v['cash'],nwc_proxy=v['stocks']+v['receivables_other']-v['operating_payables'],fcf_cash_proxy=v['operating_cashflow']-v['cash_capex_outflow']+v['cash_disposals']))
    return out
def forecasts(d,assumptions):
    out=[]
    for scenario in sorted({a['scenario'] for a in assumptions}):
        rev=d[2025]['revenue_kpi']; previous_nwc=None
        for a in sorted((a for a in assumptions if a['scenario']==scenario),key=lambda x:int(x['year'])):
            a={k:(v if k in ('scenario','status') else float(v)) for k,v in a.items()}
            if not 0 <= a['tax_rate'] <= 1: raise ValueError('Tax rate')
            if previous_nwc is None: previous_nwc=rev*a['nwc_ratio']
            rev*=1+a['revenue_growth']; ebitda=rev*a['ebitda_margin']; da=rev*a['da_ratio']; ebit=ebitda-da
            nwc=rev*a['nwc_ratio']; delta=nwc-previous_nwc; previous_nwc=nwc
            capex=rev*a['capex_total_ratio']; nopat=ebit*(1-a['tax_rate']); fcff=nopat+da-capex-delta
            out.append(dict(scenario=scenario,year=int(a['year']),status='forecast',revenue=rev,ebitda=ebitda,da=da,ebit=ebit,nopat=nopat,capex_total=capex,nwc=nwc,delta_nwc=delta,fcff=fcff,wacc=a['wacc'],terminal_growth=a['terminal_growth']))
    return out
def dcf(rows,wacc=None,g=None):
    w=rows[0]['wacc'] if wacc is None else wacc
    g=rows[0]['terminal_growth'] if g is None else g
    if not w>g: raise ValueError('WACC doit dépasser g')
    pv=sum(r['fcff']/(1+w)**i for i,r in enumerate(rows,1))
    tv=rows[-1]['fcff']*(1+g)/(w-g); pvt=tv/(1+w)**len(rows)
    return dict(scenario=rows[0]['scenario'],status='calculated_from_assumptions',valuation_date='2025-12-31',wacc=w,terminal_growth=g,pv_explicit=pv,terminal_value=tv,pv_terminal=pvt,enterprise_value=pv+pvt,terminal_share=pvt/(pv+pvt))

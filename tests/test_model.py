import unittest,math,csv,sqlite3
from src.model import *
class ModelTests(unittest.TestCase):
    def test_source_integrity(self):
        rows=read('data/raw/reported_financials.csv');sources={x['source_id'] for x in read('data/raw/sources.csv')}
        self.assertEqual(len(rows),len({(r['year'],r['metric']) for r in rows}))
        self.assertTrue(all(r['source_id'] in sources and r['status']=='reported' for r in rows))
    def test_balance(self):
        for v in history().values(): self.assertLessEqual(abs(v['assets']-v['equity_total']-v['current_liabilities']-v['noncurrent_liabilities']),1)
    def test_reconciliations(self):
        d=history();self.assertEqual(d[2024]['revenue_kpi']-d[2024]['revenue_ifrs'],5)
        self.assertEqual(ratios(d)[-1]['fcf_cash_proxy'],9117)
        self.assertAlmostEqual(ratios(d)[-1]['current_ratio'],15168/39054)
    def test_forecast_and_dcf(self):
        f=forecasts(history(),read('config/scenarios.csv'));self.assertEqual(len(f),15)
        c=[r for r in f if r['scenario']=='central']
        self.assertAlmostEqual(c[0]['revenue'],36681*1.025)
        for r in f:
            self.assertAlmostEqual(r['fcff'],r['nopat']+r['da']-r['capex_total']-r['delta_nwc'])
        self.assertGreater(dcf(c,.09,.02)['enterprise_value'],dcf(c,.11,.02)['enterprise_value'])
        self.assertGreater(dcf(c,.10,.03)['enterprise_value'],dcf(c,.10,.01)['enterprise_value'])
        with self.assertRaises(ValueError):dcf(c,.02,.02)
    def test_constant_cashflow(self):
        # Perpétuité constante : valeur analytique FCFF/WACC.
        c=[dict(scenario='test',fcff=100,wacc=.10,terminal_growth=0) for _ in range(5)]
        self.assertAlmostEqual(dcf(c)['enterprise_value'],1000)
    def test_outputs(self):
        self.assertEqual(len(read('data/processed/sensitivity.csv')),20)
        for row in read('data/processed/forecasts.csv'):
            self.assertTrue(math.isfinite(float(row['fcff'])))
        db=sqlite3.connect(ROOT/'data/processed/analysis.sqlite')
        self.assertEqual(db.execute('select count(*) from reported').fetchone()[0],len(read('data/raw/reported_financials.csv')));db.close()
if __name__=='__main__':unittest.main()

import unittest,json,sqlite3
from src.model import ROOT,read
from src.statements import social_data
class StatementTests(unittest.TestCase):
    def test_scope_units_unique(self):
        rows,d=social_data()
        self.assertEqual(len(rows),492)
        self.assertEqual(len(rows),len({(r['statement'],r['code'],r['year']) for r in rows}))
        self.assertTrue(all(r['entity']=='IAM_SA' and r['unit']=='thousand_MAD' and r['source_id']=='S4' for r in rows))
    def test_published_controls(self):
        rows,d=social_data()
        for y in (2023,2024,2025):
            self.assertEqual(d['Bilan actif']['TOTAL'][y],d['Bilan passif']['TOTAL'][y])
            self.assertEqual(d['CPC']['XIII'][y],d['ESG TFR']['X'][y])
        self.assertAlmostEqual(d['CPC']['CA'][2025],18131.524)
        self.assertAlmostEqual(d['CAF']['I'][2025],10411.273)
        self.assertAlmostEqual(d['Bilan actif']['TOTAL'][2025],40499.963)
    def test_rounding_preserved(self):
        _,d=social_data()
        self.assertAlmostEqual(d['ESG TFR']['1'][2023]-d['ESG TFR']['2'][2023]-d['ESG TFR']['I'][2023],.001)
    def test_all_reconciliations(self):
        c=read('data/processed/statement_checks.csv')
        self.assertEqual(len(c),45)
        self.assertTrue(all(abs(float(r['ecart_mdh']))<=.005 for r in c))
    def test_sql_and_csv_consistent(self):
        con=sqlite3.connect(ROOT/'data/processed/analysis.sqlite')
        self.assertEqual(con.execute('SELECT COUNT(*) FROM social_reported').fetchone()[0],492)
        val=con.execute("SELECT value/1000 FROM social_reported WHERE statement='CPC' AND code='CA' AND year=2025").fetchone()[0]
        csv_val=float(read('data/tables/cpc.csv')[3]['2025'])
        self.assertEqual(val,csv_val);con.close()
    def test_dashboard_and_powerbi_values(self):
        d=json.loads((ROOT/'data/processed/dashboard_data.json').read_text(encoding='utf-8'))
        model=json.loads((ROOT/'dashboards/powerbi/IAM.SemanticModel/model.bim').read_text(encoding='utf-8'))
        self.assertEqual(len(model['model']['tables']),6)
        self.assertAlmostEqual(d['annual'][2]['tresorerie_nette'],-1383.741)
        self.assertIn('18131.524',model['model']['tables'][0]['partitions'][0]['source']['expression'][0])
if __name__=='__main__':unittest.main()

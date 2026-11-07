import unittest,json
from src.model import ROOT,read
from src.reader_report import ratio_definitions,financing
class ReadableReportTests(unittest.TestCase):
    def test_ratio_labels_and_values(self):
        r=read('data/tables/ratios_financiers.csv')
        self.assertEqual(len(r),19)
        by={x['ratio']:x for x in r}
        self.assertEqual(by['Croissance du chiffre d’affaires']['2023'],'')
        self.assertAlmostEqual(float(by['Liquidité générale']['2025']),(8113.503+341.255)/(14509.351+1724.996))
        self.assertAlmostEqual(float(by['Rentabilité des capitaux propres — ROE']['2025']),5805.375/21247.673)
    def test_financing(self):
        f=financing();by={r['libelle']:r for r in f}
        for y in (2023,2024,2025):
            self.assertEqual(by['TOTAL GÉNÉRAL EMPLOIS / RESSOURCES'][f'emplois_{y}'],by['TOTAL GÉNÉRAL EMPLOIS / RESSOURCES'][f'ressources_{y}'])
            # Les totaux publiés sont conservés; contrôler l'équilibre après BFG/trésorerie.
            resources=float(by['TOTAL RESSOURCES STABLES'][f'ressources_{y}'])+float(by['Variation du besoin de financement global'][f'ressources_{y}'])+float(by['Variation de la trésorerie'][f'ressources_{y}'])
            uses=float(by['TOTAL EMPLOIS STABLES'][f'emplois_{y}'])+float(by['Variation du besoin de financement global'][f'emplois_{y}'])+float(by['Variation de la trésorerie'][f'emplois_{y}'])
            self.assertLess(abs(resources-uses),.005)
    def test_report_contains_every_statement(self):
        report=(ROOT/'LIRE_LES_TABLEAUX.html').read_text(encoding='utf-8')
        for name in ['Bilan actif','Bilan passif','Compte de produits et charges','État des soldes de gestion','Capacité d’autofinancement','Tableau de financement','Liquidité générale']:
            self.assertIn(name,report)
        self.assertEqual(report.count('<table>'),8)
        self.assertNotIn('<script',report)
if __name__=='__main__':unittest.main()

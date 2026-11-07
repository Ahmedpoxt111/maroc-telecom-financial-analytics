"""Rapport synthétique en français. Dépendance facultative : requirements-report.txt."""
from pathlib import Path
import sys,csv
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.model import ROOT,read
from src.statements import social_data
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_LEFT,TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from xml.sax.saxutils import escape

OUT=ROOT/'reports/Rapport_Court_Maroc_Telecom.pdf'
font_dir=Path('C:/Windows/Fonts')
if (font_dir/'arial.ttf').exists():
    for name,file in [('Arial','arial.ttf'),('Arial-Bold','arialbd.ttf'),('Arial-Italic','ariali.ttf'),('Arial-BoldItalic','arialbi.ttf')]:pdfmetrics.registerFont(TTFont(name,str(font_dir/file)))
    pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial-Italic',boldItalic='Arial-BoldItalic')
    NORMAL,BOLD='Arial','Arial-Bold'
else:NORMAL,BOLD='Helvetica','Helvetica-Bold'
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='ReportTitle',fontName='Helvetica-Bold',fontSize=19,leading=24,spaceAfter=12,textColor=colors.black))
styles.add(ParagraphStyle(name='SectionTitle',fontName='Helvetica-Bold',fontSize=13,leading=17,spaceBefore=8,spaceAfter=9,textColor=colors.black))
styles.add(ParagraphStyle(name='Copy',fontName='Helvetica',fontSize=10,leading=15,spaceAfter=9,textColor=colors.black))
styles.add(ParagraphStyle(name='Cell',fontName='Helvetica',fontSize=8.4,leading=11,textColor=colors.black))
styles.add(ParagraphStyle(name='SmallCopy',fontName='Helvetica',fontSize=8,leading=11,spaceAfter=8,textColor=colors.HexColor('#444444')))
for style_name in ['ReportTitle','SectionTitle','Copy','Cell','SmallCopy']:
    styles[style_name].fontName=BOLD if styles[style_name].fontName.endswith('Bold') else NORMAL
def safe(text):return str(text).replace('−','-').replace('—','-').replace('–','-')
def p(text,style='Copy'):return Paragraph(safe(text),styles[style])
def fmt(v,rate=False):
    if v=='':return 'n.d.'
    return f'{float(v)*(100 if rate else 1):,.1f}'.replace(',',' ').replace('.',',')+(' %' if rate else '')
def tab(headers,rows,widths,numeric=(1,2,3),total_rows=()):
    data=[[p(escape(str(x)),'Cell') for x in headers]]
    for row in rows:data.append([p(str(x),'Cell') if not isinstance(x,Paragraph) else x for x in row])
    t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
    commands=[('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E7E7E7')),('LINEBELOW',(0,0),(-1,0),.6,colors.black),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,1),(-1,-1),.25,colors.HexColor('#D2D2D2'))]
    for r in total_rows:commands.extend([('BACKGROUND',(0,r+1),(-1,r+1),colors.HexColor('#F0F0F0')),('LINEABOVE',(0,r+1),(-1,r+1),.5,colors.HexColor('#888888'))])
    # Les paragraphes numériques sont alignés à droite via leur propre style.
    for r in range(1,len(data)):
        for c in numeric:
            if c<len(data[r]):
                st=ParagraphStyle(name=f'N{r}_{c}',parent=styles['Cell'],alignment=TA_RIGHT)
                data[r][c]=Paragraph(safe(rows[r-1][c]),st)
    t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle(commands));return t
def source(page):return p('Source : Maroc Telecom, DEU 2025, comptes sociaux IAM SA, p. '+page+'. Montants publiés en milliers MAD, convertis en millions MAD (MDH).','SmallCopy')
def footer(canvas,doc):
    w,h=A4;canvas.setStrokeColor(colors.HexColor('#AAAAAA'));canvas.line(42,39,w-42,39)
    canvas.setFont(NORMAL,8);canvas.setFillColor(colors.HexColor('#555555'))
    canvas.drawString(42,26,'Maroc Telecom - Comptes sociaux IAM SA - 2023-2025')
    canvas.drawRightString(w-42,26,str(doc.page))
def main():
    _,d=social_data();annual=read('data/processed/social_analysis.csv');rr=read('data/tables/ratios_financiers.csv');fin=read('data/tables/tableau_financement.csv')
    def vals(statement,code):return [fmt(d[statement][code][y]) for y in (2023,2024,2025)]
    s=[]
    s += [p('Maroc Telecom<br/>États de synthèse et ratios','ReportTitle'),p('Rapport synthétique - Exercices 2023, 2024 et 2025','SmallCopy'),p('Périmètre : <b>IAM SA seule</b>, référentiel comptable marocain CGNC. Les comptes consolidés du Groupe et les prévisions sont présentés séparément dans le projet. Ce rapport résume les tableaux détaillés disponibles dans le classeur Excel.'),p('1. Bilan résumé','SectionTitle')]
    b=[]
    for label,st,code in [('Immobilisations en non-valeurs','Bilan actif','A'),('Immobilisations incorporelles','Bilan actif','B'),('Immobilisations corporelles','Bilan actif','C'),('Immobilisations financières','Bilan actif','D'),('Actif immobilisé net (avec écarts de conversion)','Bilan actif','I'),('Actif circulant hors trésorerie','Bilan actif','II'),('Trésorerie actif','Bilan actif','III'),('TOTAL ACTIF NET','Bilan actif','TOTAL'),('Capitaux propres','Bilan passif','A'),('Dettes de financement','Bilan passif','C'),('Financement permanent total','Bilan passif','I'),('Passif circulant hors trésorerie','Bilan passif','II'),('Trésorerie passif','Bilan passif','III'),('TOTAL PASSIF','Bilan passif','TOTAL')]:b.append([label,*vals(st,code)])
    s += [tab(['Bilan (MDH)','2023','2024','2025'],b,[295,72,72,72],total_rows=[7,13]),Spacer(1,8),source('233-234'),p('Lecture du bilan','SectionTitle'),p('Le total du bilan atteint <b>40 500,0 MDH</b> en 2025, contre 39 905,2 MDH en 2024. Les capitaux propres passent de 16 699,3 à 21 247,7 MDH; leur part dans le financement du bilan remonte de <b>41,8 % à 52,5 %</b>.'),p('L’actif reste fortement immobilisé. Le financement permanent demeure inférieur à l’actif immobilisé net : le fonds de roulement fonctionnel reste négatif. La baisse de la trésorerie passif améliore toutefois nettement la trésorerie nette en 2025.'),PageBreak()]
    s += [p('2. CPC, soldes de gestion et CAF','ReportTitle'),p('Les données suivantes sont publiées. Les marges et leurs variations, commentées sous le tableau, sont calculées à partir de ces chiffres.','SmallCopy')]
    rows=[]
    for label,st,code in [('Chiffre d’affaires','CPC','CA'),('Produits d’exploitation','CPC','I'),('Charges d’exploitation','CPC','II'),('Résultat d’exploitation','CPC','III'),('Résultat financier','CPC','VI'),('Résultat courant','CPC','VII'),('Résultat non courant','CPC','X'),('Résultat avant impôts','CPC','XI'),('Impôt sur les sociétés','CPC','XII'),('RÉSULTAT NET','CPC','XIII'),('Valeur ajoutée','ESG TFR','IV'),('Excédent brut d’exploitation (EBE)','ESG TFR','V'),('Capacité d’autofinancement (CAF)','CAF','I'),('Distributions de bénéfices','CAF','10'),('AUTOFINANCEMENT','CAF','II')]:rows.append([label,*vals(st,code)])
    s += [tab(['CPC et ESG (MDH)','2023','2024','2025'],rows,[295,72,72,72],total_rows=[9,14]),Spacer(1,8),source('235-237'),p('Explication des résultats','SectionTitle'),p('En 2025, le chiffre d’affaires social recule de <b>1,4 %</b>. L’EBE diminue de 2,6 % et sa marge passe de 55,0 % à <b>54,4 %</b>. La marge d’exploitation baisse de 39,5 % à 36,1 % : le résultat opérationnel se dégrade malgré la reprise du bénéfice net.'),p('Le résultat net augmente à <b>5 805,4 MDH</b>, après 1 592,7 MDH en 2024. Le résultat non courant passe de -6 415,5 à +1 712,7 MDH, dans un contexte marqué par le litige Wana et sa résolution partielle. Le redressement du bénéfice ne traduit donc pas une amélioration équivalente de l’activité récurrente.'),p('La CAF est de <b>10 411,3 MDH</b> en 2025. Après distributions, l’autofinancement atteint 9 154,3 MDH. La CAF de l’ESG utilise les dotations et reprises éligibles, distinctes de leurs montants totaux dans le CPC.'),PageBreak()]
    s += [p('3. Financement et trésorerie','ReportTitle'),p('Équilibre financier sur bilan social net','SectionTitle')]
    masses=[('Financement permanent','financement_permanent'),('Actif immobilisé net','actif_immobilise'),('Fonds de roulement fonctionnel','fr'),('Actif circulant hors trésorerie','actif_circulant'),('Passif circulant hors trésorerie','passif_circulant'),('Besoin de financement global (BFG)','bfg'),('Trésorerie nette','tresorerie_nette')]
    s += [tab(['Masses calculées (MDH)','2023','2024','2025'],[[l,*[fmt(a[k]) for a in annual]] for l,k in masses],[295,72,72,72],total_rows=[2,5,6]),p('Calculs : FR = financement permanent - actif immobilisé; BFG = actif circulant - passif circulant hors trésorerie; trésorerie nette = trésorerie actif - trésorerie passif. Écarts d’arrondis possibles de 0,001 MDH avec les masses publiées.','SmallCopy'),p('Tableau de financement résumé','SectionTitle')]
    by={r['libelle']:r for r in fin};frows=[]
    for label,key,side in [('Ressources : autofinancement','Autofinancement','ressources'),('Ressources : cessions et réductions','Cessions et réductions d\'immobilisations','ressources'),('Variation des dettes de financement','Augmentation des dettes de financement','ressources'),('TOTAL RESSOURCES STABLES','TOTAL RESSOURCES STABLES','ressources'),('TOTAL EMPLOIS STABLES','TOTAL EMPLOIS STABLES','emplois')]:frows.append([label,*[fmt(by[key][side+'_'+str(y)]) for y in (2023,2024,2025)]])
    s += [tab(['Emplois / ressources publiés (MDH)','2023','2024','2025'],frows,[295,72,72,72],total_rows=[3,4]),Spacer(1,8),source('238'),p('Interprétation','SectionTitle'),p('La trésorerie nette reste négative, mais s’améliore de <b>-11 885,0 à -1 383,7 MDH</b> entre 2024 et 2025. Cette évolution s’accompagne d’un fort redressement de l’autofinancement et d’une augmentation des dettes de financement permanentes.'),p('Le BFG négatif constitue une ressource liée à la structure du cycle d’exploitation. Il ne suffit cependant pas à conclure à une absence de risque de liquidité : la nature des dettes, les échéances bancaires et le recouvrement des créances doivent aussi être examinés.'),PageBreak()]
    def ratio_page(title,selected):
        result=[p(title,'ReportTitle'),p('Ratios calculés sur les comptes sociaux IAM SA. Les capitaux propres et l’actif sont ceux de clôture; les taux sont exprimés en %, les autres rapports en fois.','SmallCopy')]
        rows=[]
        for r in selected:
            label='<b>'+escape(r['ratio'])+'</b><br/><font size="7.5">'+escape(r['formule'])+'</font>'
            values=[(f'{float(r[str(y)]):.2f}'.replace('.',',')+' x' if r['unite']=='fois' and r[str(y)]!='' else fmt(r[str(y)],r['unite']=='%')) for y in (2023,2024,2025)]
            rows.append([label,*values,escape(r['interpretation'])])
        result += [tab(['Ratio et formule','2023','2024','2025','Explication'],rows,[182,51,51,51,176]),Spacer(1,8),p('Source des données : DEU 2025, pages 233-237. Les formules détaillées et les cellules sources sont consultables dans les onglets Ratios et Analyse du classeur. n.d. : données de comparaison 2022 non intégrées.','SmallCopy')]
        return result
    s += ratio_page('4. Ratios de performance et de structure',rr[:10])+[PageBreak()]
    s += ratio_page('5. Ratios de liquidité et de financement',rr[10:])
    s += [p('Conclusion','SectionTitle'),p('La structure financière se renforce en 2025 et la trésorerie nette se redresse. L’activité sociale présente néanmoins un recul du chiffre d’affaires et de la rentabilité d’exploitation. La hausse du résultat net doit être distinguée de la performance récurrente.'),p('La liquidité générale, à <b>0,52 fois</b> en 2025, reste inférieure à 1. Ce signal justifie une revue des échéances et du cycle d’exploitation, sans constituer à lui seul un diagnostic d’insolvabilité. Le ROE de 27,3 % est affecté par les éléments non courants.'),p('Document de référence : <link href="https://www.ammc.ma/sites/default/files/Maroc_Telecom_Document_enregistrement_universel_2025.pdf" color="black"><u>Maroc Telecom, DEU 2025 (AMMC)</u></link>. États sociaux : p. 233-238; ETIC complet : p. 239-255, non reproduit dans ce résumé. Les comptes du Groupe et le DCF ne sont pas mélangés aux comptes sociaux.','SmallCopy')]
    OUT.parent.mkdir(parents=True,exist_ok=True)
    doc=SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=43,bottomMargin=49,title='Maroc Telecom - États de synthèse et ratios 2023-2025',author='')
    doc.build(s,onFirstPage=footer,onLaterPages=footer)
    print(OUT)
if __name__=='__main__':main()

"""Génère un projet Power BI PBIP/PBIR éditable, sans clé ni service cloud."""
from pathlib import Path
import json,csv
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dashboards/powerbi'
def save(path,obj):
 p=OUT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def schema(p):return 'https://developer.microsoft.com/json-schemas/fabric/item/report/'+p+'/schema.json'
def literal(v):return {'expr':{'Literal':{'Value':str(v).lower() if isinstance(v,bool) else "'"+str(v).replace("'","''")+"'"}}}
def column(table,name):return {'Column':{'Expression':{'SourceRef':{'Entity':table}},'Property':name}}
def measure(name):return {'Measure':{'Expression':{'SourceRef':{'Entity':'Finance'}},'Property':name}}
def projection(field,ref,label=None):
 p={'field':field,'queryRef':ref,'nativeQueryRef':label or ref}
 if label:p['displayName']=label
 return p
def visual(page,name,kind,x,y,w,h,roles=None,title=None,objects=None):
 cfg={'visualType':kind,'drillFilterOtherVisuals':True}
 if roles:cfg['query']={'queryState':{r:{'projections':v} for r,v in roles.items()}}
 if title:cfg['visualContainerObjects']={'title':[{'properties':{'show':literal(True),'text':literal(title),'fontSize':{'expr':{'Literal':{'Value':'14D'}}}}}]}
 if objects:cfg['objects']=objects
 save(f'IAM.Report/definition/pages/{page}/visuals/{name}/visual.json',{'$schema':schema('definition/visualContainer/2.0.0'),'name':name,'position':dict(x=x,y=y,z=0,width=w,height=h,tabOrder=0),'visual':cfg})
def text(page,name,text,x,y,w,h,size=24):
 visual(page,name,'textbox',x,y,w,h,objects={'general':[{'properties':{'paragraphs':[{'textRuns':[{'value':text,'textStyle':{'fontFamily':'Arial','fontSize':str(size)+'pt','color':'#102B46'}}]}]}}]})
def mvalue(v):
 if v is None:return 'null'
 if isinstance(v,(int,float)):return str(v)
 return '"'+str(v).replace('"','""')+'"'
def mtable(name,rows,types):
 columns=[]
 for k,t in types.items():columns.append(dict(name=k,dataType=t,sourceColumn=k,summarizeBy='none',formatString='0' if t=='int64' else '#,0.0;(#,0.0);-')) if t!='string' else columns.append(dict(name=k,dataType=t,sourceColumn=k,summarizeBy='none'))
 mtypes={'int64':'Int64.Type','double':'number','string':'text'}
 expr='#table(type table ['+', '.join('#"'+k+'"='+mtypes[v] for k,v in types.items())+'], {'+', '.join('{'+', '.join(mvalue(r[k]) for k in types)+'}' for r in rows)+'})'
 return dict(name=name,columns=columns,partitions=[dict(name=name,mode='import',source=dict(type='m',expression=[expr]))])
def main():
 d=json.loads((ROOT/'data/processed/dashboard_data.json').read_text(encoding='utf-8'));annual=d['annual']
 types={k:('int64' if k=='annee' else 'double') for k in annual[0]};finance=mtable('Finance',annual,types)
 measures=[]
 names={'CA':'ca','EBE':'ebe','CAF':'caf','Resultat net':'resultat_net','Valeur ajoutee':'valeur_ajoutee','FR':'fr','BFG':'bfg','Tresorerie nette':'tresorerie_nette','Capitaux propres':'capitaux_propres'}
 for label,col in names.items():
  measures.append(dict(name=label,expression=f'SUM(Finance[{col}])',formatString='#,0.0;(#,0.0);-'))
  measures.append(dict(name=label+' exercice selectionne',expression=f'CALCULATE([{label}], Finance[annee] = MAX(Finance[annee]))',formatString='#,0.0;(#,0.0);-'))
 measures.extend([dict(name='Marge EBE',expression='DIVIDE([EBE],[CA])',formatString='0.0%'),dict(name='Marge nette',expression='DIVIDE([Resultat net],[CA])',formatString='0.0%')]);finance['measures']=measures
 tables=[finance]
 for statement,tn in [('Bilan actif','Actif'),('Bilan passif','Passif'),('CPC','CPC'),('ESG TFR','ESG'),('CAF','CAF')]:
  rr=[{'Ordre':i+1,'Poste':r['libelle'],'2023':r['2023'],'2024':r['2024'],'2025':r['2025'],'Page':int(r['page'])} for i,r in enumerate(d['tables'][statement])]
  tb=mtable(tn,rr,{'Ordre':'int64','Poste':'string','2023':'double','2024':'double','2025':'double','Page':'int64'});tb['columns'][1]['sortByColumn']='Ordre';tables.append(tb)
 save('IAM.SemanticModel/definition.pbism',{'version':'1.0','settings':{}})
 save('IAM.SemanticModel/model.bim',{'name':'IAM','compatibilityLevel':1567,'model':{'culture':'fr-FR','defaultPowerBIDataSourceVersion':'powerBI_V3','sourceQueryCulture':'fr-FR','tables':tables,'annotations':[{'name':'PBI_QueryOrder','value':json.dumps([t['name'] for t in tables])}]}})
 save('IAM.Report/definition.pbir',{'$schema':schema('definitionProperties/2.0.0'),'version':'4.0','datasetReference':{'byPath':{'path':'../IAM.SemanticModel'}}})
 save('IAM.pbip',{'version':'1.0','artifacts':[{'report':{'path':'IAM.Report'}}],'settings':{'enableAutoRecovery':True}})
 save('IAM.Report/definition/report.json',{'$schema':schema('definition/report/2.0.0'),'themeCollection':{},'settings':{'useStylableVisualContainerHeader':True}})
 pages=[('synthese','01 · Performance IAM SA'),('bilan','02 · Bilan IAM SA'),('cpc','03 · CPC IAM SA'),('esg','04 · ESG et CAF'),('equilibre','05 · Équilibre financier')]
 save('IAM.Report/definition/pages/pages.json',{'$schema':schema('definition/pagesMetadata/1.0.0'),'pageOrder':[p for p,_ in pages],'activePageName':'synthese'})
 for page,label in pages:
  save(f'IAM.Report/definition/pages/{page}/page.json',{'$schema':schema('definition/page/1.0.0'),'name':page,'displayName':label,'displayOption':'FitToPage','width':1280,'height':800})
  text(page,'title',label,24,12,1232,55)
  text(page,'scope','Comptes sociaux CGNC · IAM SA seule · Millions MAD · Source : DEU 2025, p. 233–237',24,65,1232,40,12)
 def mp(n):return projection(measure(n),'Finance.'+n,n)
 year=projection(column('Finance','annee'),'Finance.annee','Année')
 for i,n in enumerate(['CA','EBE','Resultat net','CAF']):visual('synthese','card'+str(i),'card',24+i*312,115,295,130,{'Values':[mp(n+' exercice selectionne')]},n+' — année sélectionnée / dernière')
 visual('synthese','annee','slicer',24,260,240,100,{'Values':[year]},'Année')
 visual('synthese','trend','lineChart',290,260,960,240,{'Category':[year],'Y':[mp('CA'),mp('EBE'),mp('CAF')]},'CA, EBE et CAF sociaux — MDH')
 visual('synthese','result','clusteredColumnChart',24,510,600,255,{'Category':[year],'Y':[mp('Resultat net')]},'Résultat net social — MDH')
 visual('synthese','margin','lineChart',650,510,600,255,{'Category':[year],'Y':[mp('Marge EBE'),mp('Marge nette')]},'Marges sociales')
 def statement_visual(page,name,table,x,y,w,h):
  pr=[projection(column(table,c),table+'.'+c,c) for c in ['Ordre','Poste','2023','2024','2025']]
  visual(page,name,'tableEx',x,y,w,h,{'Values':pr},table+' — valeurs nettes en MDH')
 statement_visual('bilan','actif','Actif',24,120,610,645);statement_visual('bilan','passif','Passif',650,120,606,645)
 statement_visual('cpc','cpc_table','CPC',24,120,1232,645)
 statement_visual('esg','esg_table','ESG',24,120,710,645);statement_visual('esg','caf_table','CAF',755,120,500,645)
 visual('equilibre','fr_bfg','lineChart',24,120,1232,300,{'Category':[year],'Y':[mp('FR'),mp('BFG'),mp('Tresorerie nette')]},'FR, BFG et trésorerie nette — MDH')
 visual('equilibre','ratios_table','tableEx',24,445,1232,300,{'Values':[year]+[mp(n) for n in ['FR','BFG','Tresorerie nette','Capitaux propres']]},'Calculs sur bilan social net')
 print('Projet PBIP généré : 5 pages et 6 tables incorporées, sans chemins de données externes.')
if __name__=='__main__':main()

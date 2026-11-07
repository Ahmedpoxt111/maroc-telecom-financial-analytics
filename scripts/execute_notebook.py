"""Exécution réelle Jupyter et export HTML, avec noyau Python de l'environnement courant."""
from pathlib import Path
import sys,os,tempfile,json,re,asyncio
if sys.platform=='win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
ROOT=Path(__file__).resolve().parents[1]
try:
    import nbformat
    from nbclient import NotebookClient
    from nbconvert import HTMLExporter
except ImportError as exc:
    raise SystemExit('Jupyter manque dans cet environnement. Exécuter : python -m pip install -r requirements-notebook.txt') from exc

def execute(cwd=None):
    file=ROOT/'notebooks/financial_analysis.ipynb';nb=nbformat.read(file,as_version=4)
    nbformat.validate(nb)
    # Enregistrement temporaire du noyau, sans installation dans le profil utilisateur.
    with tempfile.TemporaryDirectory(prefix='maroc-telecom-kernel-') as td:
        kernels=Path(td)/'kernels'/'maroc-telecom-test';kernels.mkdir(parents=True)
        spec={'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],
              'display_name':'Maroc Telecom test','language':'python'}
        (kernels/'kernel.json').write_text(json.dumps(spec),encoding='utf-8')
        names=['JUPYTER_PATH','JUPYTER_RUNTIME_DIR','JUPYTER_CONFIG_DIR','IPYTHONDIR']
        previous={n:os.environ.get(n) for n in names}
        os.environ['JUPYTER_PATH']=td+(os.pathsep+previous['JUPYTER_PATH'] if previous['JUPYTER_PATH'] else '')
        for name,sub in [('JUPYTER_RUNTIME_DIR','runtime'),('JUPYTER_CONFIG_DIR','config'),('IPYTHONDIR','ipython')]:
            target=Path(td)/sub;target.mkdir();os.environ[name]=str(target)
        try:
            client=NotebookClient(nb,timeout=180,kernel_name='maroc-telecom-test',
                                  resources={'metadata':{'path':str(cwd or ROOT/'notebooks')}})
            client.execute()
        finally:
            for name,old in previous.items():
                if old is None:os.environ.pop(name,None)
                else:os.environ[name]=old
    nb.metadata.kernelspec={'display_name':'Python 3 (ipykernel)','language':'python','name':'python3'}
    nbformat.validate(nb)
    for cell in nb.cells:
        if cell.cell_type=='code':
            assert cell.execution_count is not None
            assert not any(o.output_type=='error' for o in cell.outputs)
    nbformat.write(nb,file)
    exporter=HTMLExporter(template_name='classic');body,_=exporter.from_notebook_node(nb)
    # Lecture hors ligne : les résultats sont statiques, aucun script CDN nécessaire.
    body=re.sub(r'<script\b[^>]*>.*?</script\s*>','',body,flags=re.S|re.I)
    body=body.replace('<html lang="en">','<html lang="fr">')
    neutral='<style>.highlight span{color:#222!important}.highlight,.input_area{background:#f7f7f7!important}body{background:white!important;color:#222!important}a{color:#333!important}</style>'
    body=body.replace('</head>',neutral+'</head>')
    (ROOT/'notebooks/financial_analysis.html').write_text(body,encoding='utf-8')
    print('Jupyter réel : toutes les cellules exécutées; sorties enregistrées; export HTML généré.')
if __name__=='__main__':execute()

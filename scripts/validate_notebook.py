"""Vérification légère de structure et syntaxe; n'est pas un test d'exécution Jupyter."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
nb=json.loads((root/'notebooks/financial_analysis.ipynb').read_text(encoding='utf-8'))
assert nb['nbformat']==4
assert len({cell['id'] for cell in nb['cells']})==len(nb['cells'])
for i,cell in enumerate(nb['cells']):
    if cell['cell_type']=='code':
        compile(''.join(cell['source']),f'cell_{i}','exec')
        assert not any(o.get('output_type')=='error' for o in cell.get('outputs',[]))
print('Structure et syntaxe du notebook valides. Exécution Jupyter : scripts/execute_notebook.py.')

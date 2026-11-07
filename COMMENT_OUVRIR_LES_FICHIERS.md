# Comment ouvrir les fichiers

**Commencer par extraire le ZIP complet.** Sous Windows : clic droit sur le ZIP → Extraire tout. Ne pas exécuter un notebook ou un script directement à l’intérieur du ZIP et ne pas déplacer le notebook seul : il utilise les dossiers `src`, `data`, `config` et `sql` du projet.

## Lire les résultats sans programmer

| Fichier | À ouvrir avec | Résultat |
|---|---|---|
| `LIRE_LES_TABLEAUX.html` | Navigateur | Bilans, CPC, ESG, CAF, financement et 19 ratios |
| `notebooks/financial_analysis.html` | Navigateur | Notebook déjà exécuté, tableaux et graphiques inclus |
| `reports/Rapport_Court_Maroc_Telecom.pdf` | Lecteur PDF | Rapport synthétique en cinq pages |
| `workbook/Maroc_Telecom_Etats_Sociaux.xlsx` | Excel ou LibreOffice | Classeur avec formules et graphiques |
| `dashboards/dashboard.html` | Navigateur | Dashboard interactif local |

## Recalculer le notebook `.ipynb`

Un fichier `.ipynb` n’est pas une application Windows. Il se lit dans Jupyter ou VS Code avec l’extension Jupyter. Il contient du code et des résultats enregistrés. GitHub peut aussi afficher les résultats enregistrés.

Prérequis : **Python 3.10 ou supérieur**. Depuis le dossier racine décompressé :

```sh
python -m venv .venv
# Windows : utiliser directement le Python de cet environnement, sans activation.
.venv\Scripts\python.exe -m pip install -r requirements-notebook.txt
.venv\Scripts\python.exe -m notebook notebooks/financial_analysis.ipynb
```

Sous macOS/Linux, remplacer `.venv\Scripts\python.exe` par `.venv/bin/python`.

Dans Jupyter, sélectionner le noyau Python de cet environnement puis « Restart Kernel and Run All Cells ». Le dossier courant doit être celui du projet ou `notebooks/`. Si le projet ne peut pas être trouvé, renseigner son chemin complet dans `PROJECT_DIR`, première cellule de code. Aucun chemin personnel n’est imposé dans le notebook.

Pour exécuter sans interface et réenregistrer les résultats :

```sh
.venv\Scripts\python.exe scripts/execute_notebook.py
```

Ce script utilise explicitement le Python de l’environnement courant. Il ne crée pas de noyau permanent dans le profil utilisateur.

## Les autres fichiers

- `.py` : scripts Python. Depuis la racine : `python -m src.pipeline`. Ne pas lancer `src/pipeline.py` isolément par double-clic.
- `.sql` : requêtes SQLite, pas des applications à double-cliquer. Le pipeline les exécute et prépare `data/processed/analysis.sqlite`.
- `.csv` : données tabulaires. Importer en UTF-8, séparateur virgule et nombres à décimale point. Les tableaux en français sont dans `data/tables/`.
- `.svg` : graphiques, ouvrables dans un navigateur; ils sont aussi affichés dans le notebook.
- `.pbip` / `.pbir` / `.bim` / fichiers `.json` du projet Power BI : conserver leur arborescence. Ouvrir `dashboards/powerbi/IAM.pbip` dans Power BI Desktop, pas chaque JSON séparément. **Affichage Desktop non validé; aucun PBIX final vérifié n’est fourni.**

## Messages fréquents

| Message | Action |
|---|---|
| `No module named IPython`, `nbclient`, `nbformat` ou noyau introuvable | Installer `requirements-notebook.txt` dans le même environnement Python que Jupyter |
| `No module named src` ou dossier du projet introuvable | Extraire tout le ZIP, conserver l’arborescence et ouvrir Jupyter depuis la racine |
| Python non reconnu | Installer Python 3.10+ puis rouvrir le terminal; le lanceur `py -3` peut remplacer `python` sous Windows |
| Le `.ipynb` s’ouvre comme du texte | Utiliser Jupyter; pour lire immédiatement, ouvrir le `.html` à côté |
| Erreur sur un fichier Power BI | Utiliser d’abord le dashboard HTML; le projet Power BI reste une définition de développement non validée dans Desktop |

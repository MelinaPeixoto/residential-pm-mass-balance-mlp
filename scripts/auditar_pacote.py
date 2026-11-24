"""Conferências básicas do pacote: não substituem revisão humana de privacidade."""
from pathlib import Path
import csv
import json
import sys

root = Path(__file__).resolve().parent.parent
prohibited = {'.xlsx', '.xls', '.pt', '.pth', '.pkl', '.pickle', '.db', '.zip', '.log'}
private_dirs = {'resultados_3_sementes_600_MBB', 'substituicoes_artigo', '.git', '__pycache__', '.venv'}
problems = []
for path in root.rglob('*'):
    if not path.is_file() or any(part in private_dirs for part in path.relative_to(root).parts):
        continue
    if path.suffix.lower() in prohibited:
        problems.append(f'Arquivo que exige revisão: {path.relative_to(root)}')
for notebook in (root / 'notebooks').glob('*.ipynb'):
    obj = json.loads(notebook.read_text(encoding='utf-8'))
    if any(c.get('outputs') or c.get('execution_count') is not None for c in obj.get('cells', []) if c.get('cell_type') == 'code'):
        problems.append(f'Notebook contém saídas de execução: {notebook.name}')
summary = root / 'resultados/tabelas/Tabela03_bootstrap_Finf_kprime_1000.csv'
with summary.open(encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(f))
if len(rows) != 9:
    problems.append(f'Tabela 3: esperados 9 cenários; encontrados {len(rows)}.')
if problems:
    print('\n'.join(problems))
    sys.exit(1)
print('OK: extensões verificadas, notebooks sem saídas e 9 cenários na tabela consolidada.')
print('Examine manualmente os arquivos e o histórico antes da publicação.')

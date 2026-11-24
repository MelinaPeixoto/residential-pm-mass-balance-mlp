"""Importa, para uso local e ignorado pelo Git, os dados do checkpoint verificado."""
import argparse
import csv
import hashlib
import os
import shutil
import stat
import tempfile
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parent.parent
DIRECTORY = 'resultados_3_sementes_600_MBB'
EXPECTED_SHA256 = '16e5143cab9d5f91290b6a55701e8708a6fff6f993b93b357a8b6750fb3831b6'
MAX_BYTES = 250_000_000

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('checkpoint', type=Path, help='ZIP original do checkpoint de 1000 réplicas')
    args = parser.parse_args()
    archive = args.checkpoint.expanduser().resolve(strict=True)
    if digest(archive) != EXPECTED_SHA256:
        raise ValueError('O SHA-256 difere do checkpoint documentado. Nenhum arquivo foi extraído.')
    target = ROOT / DIRECTORY
    if target.exists():
        raise FileExistsError(f'{target} já existe; não será sobrescrito.')
    with tempfile.TemporaryDirectory(prefix='.workspace_local_tmp_', dir=ROOT) as temp:
        stage = Path(temp)
        with ZipFile(archive) as z:
            members = [i for i in z.infolist() if i.filename.startswith(DIRECTORY + '/') and not i.is_dir()]
            if not members or sum(i.file_size for i in members) > MAX_BYTES:
                raise ValueError('Conteúdo ausente ou tamanho inesperado do checkpoint.')
            for entry in members:
                path = PurePosixPath(entry.filename)
                mode = (entry.external_attr >> 16) & 0xFFFF
                if path.is_absolute() or '..' in path.parts or stat.S_ISLNK(mode):
                    raise ValueError(f'Caminho inseguro no arquivo: {entry.filename}')
                dst = stage.joinpath(*path.parts)
                dst.parent.mkdir(parents=True, exist_ok=True)
                with z.open(entry) as src, dst.open('wb') as out:
                    shutil.copyfileobj(src, out)
        for res in ('R5', 'R6', 'R7'):
            for frac in ('PM1', 'PM25', 'PM10'):
                path = stage / DIRECTORY / 'replicas_mbb' / f'{res}_{frac}_B_paired.csv'
                with path.open(newline='', encoding='utf-8') as f:
                    ids = [int(row['rep']) for row in csv.DictReader(f)]
                if len(ids) != 1000 or set(ids) != set(range(1, 1001)):
                    raise ValueError(f'Réplicas incompletas ou duplicadas: {path.name}')
        os.replace(stage / DIRECTORY, target)
    print(f'Arquivos importados para {target}. Esta pasta é ignorada pelo Git.')
    print('Não execute nem publique modelos ou dados de fontes que você não confie.')

if __name__ == '__main__':
    main()

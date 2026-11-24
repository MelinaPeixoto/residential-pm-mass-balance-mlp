# residential-pm-mass-balance-mlp
Reproducible pipeline for modeling indoor particulate matter using mass balance and neural networks.
# Hybrid Modeling of Particulate Matter in Residences

Selected code and results associated with **Article 2, version 15**, concerning the modeling of indoor particulate matter concentrations and infiltration parameters in residential environments. The analysis covers three residences (R5, R6, and R7) and three size fractions: PM₁, PM₂.₅, and PM₁₀.

**Status:** Package prepared for pre-publication review. Reproduction from the original data has not yet been verified; information regarding data, licensing, the article, and certain results must be finalized prior to public release.

## Overview

This study compares a mass balance model (MBM) with a hybrid model that integrates the MBM with a multilayer perceptron (MLP) neural network (MBM + MLP). This repository contains the execution notebooks, verification and consolidation scripts, a set of tables, and one selected figure.

Protocols A and B are evaluated. The bootstrap consolidation—comprising **1,000 replicates**—included in this package pertains to the nine scenarios of **Protocol B**. The point predictions utilized are derived from a set of three random seeds: `123`, `456`, and `789`. This consolidation retains 600 existing replicates and adds 400 more; it does not constitute a complete retraining of the point models.

Training and validation metrics associated with the final, readjusted models should be interpreted with this readjustment in mind; they do not represent an independent evaluation. The test set has already been accessed in previous analyses. For details on provenance and limitations, please refer to [docs/RASTREABILIDADE.md](docs/RASTREABILIDADE.md).

## Contents

- `notebooks/`: Includes the original notebook (containing 600 replicates) and a version configured for 1,000 replicates. The 1,000-run replication was not executed in its entirety from start to finish.
- `scripts/`: local checkpoint import, metric auditing, replica verification, consolidation, and generation of tables and figures.
- `resultados/tabelas/`: selected tables, including the consolidation of 1,000 replicas and test metrics for protocol B.
- `resultados/figuras/`: a selected aggregated figure showing NRMSE (normalized by amplitude) for protocol B.
- `data/`: guidance on data access; does not contain the individual time series.
- `docs/`: traceability, the environment used for the resumed run, and pending tasks for publication.

File names retain the nomenclature used during the preparation of the paper. The provided ablation table should not be assumed to be an exact reproduction of Table 4 from the manuscript without further verification.

## Requirements and installation

The scripts use Python and the libraries listed in `requirements.txt`. The environment in which the run was resumed is documented in [docs/ambiente_retomada_1000.json](docs/ambiente_retomada_1000.json). **A clean, independent installation has not yet been tested**, and the dependencies file does not specify exact versions.

```bash
git clone <URL_OF_ARTICLE_REPOSITORY_2>
cd <REPOSITORY_NAME>
python -m venv .venv
```

Activate the environment in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On Linux or macOS:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Replace the placeholders within `< >` with the actual repository URL and name. The repository address from another paper should not be used automatically.

## Verification from an authorized checkpoint

Individual series and serialized models are not included in this package. The audit below requires an authorized copy of the file `Checkpoint_R5_R7_3sementes_1000MBB_com_tabelas.zip`. The script verifies the expected SHA-256 hash and imports the data into a folder ignored by Git. Serialized models should only be loaded from trusted sources.

```bash
python scripts/preparar_dados_locais.py /path/to/Checkpoint_R5_R7_3sementes_1000MBB_com_tabelas.zip
python scripts/auditar_resultados.py
python scripts/retomar_mbb_1000.py verify
python scripts/consolidar_mbb_1000.py
```

The audit recalculates the metrics for Table 6 based on the stored predictions and verifies the presence of the replicates. The `verify` command recalculates one selected replicate for each scenario; this is not equivalent to re-running all simulations. The consolidation step generates local files in `substituicoes_artigo/`.

To generate Figure 8 and the tables prepared by the script, on Linux or macOS:

```bash
MPLBACKEND=Agg ONLY_FIGS=Fig08 python scripts/figuras_e_tabelas_artigo.py
```

On PowerShell:

```powershell
$env:MPLBACKEND = 'Agg'
$env:ONLY_FIGS = 'Fig08'
python scripts/figuras_e_tabelas_artigo.py
```

These steps rely on the authorized checkpoint and reproduce outputs derived from it. Full reproduction of the study also depends on the input spreadsheets, documentation of corrections, the environment, and the execution of the pipeline. The original spreadsheets are not included in this package.

## Data, privacy, and licensing

Individual residential data and checkpoints are not included, pending a review of the conditions...
sharing conditions and the applicable authorization. Please refer to [data/README.md](data/README.md). Do not add individual files to GitHub without this review.

The code license and data terms of use have yet to be defined by the authors. No license has been automatically assigned to this package. For figures that incorporate third-party content, usage rights must also be verified.

## Citation and contact

**Article:** Article 2, version 15 — insert the final title, full list of authors, journal, year, and DOI upon confirmation/publication.

**Contact:** insert the name and contact address that the authors wish to make public.

Please consult [docs/PUBLICACAO_PENDENCIAS.md](docs/PUBLICACAO_PENDENCIAS.md) before making the repository public.

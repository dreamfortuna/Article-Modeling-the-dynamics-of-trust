# Modeling the Dynamics of Trust

This repository contains analysis code, figure-generation scripts, source data, and Stan model files for the article project on modeling the dynamics of trust in human-automation interaction.

## Repository Structure

- `Analysis_Code/`: Python analysis scripts and derived diagnostic tables.
- `Data/`: participant-level MATLAB `.mat` data files used by the modeling scripts.
- `Figure_Code/`: Python scripts for regenerating article figures. Generated SVG files are written to `Figure_Code/Figure/`.
- `Figure_Source_Data/`: tab-delimited source data used by figure scripts.
- `Figures/`: exported article figure images.
- `Modeling/`: R scripts, Stan models, compiled model artifacts, model fits, and utility functions.

## Data Notes

The `Data/` directory contains participant-level MATLAB files. Files ending in `_t.mat` are the validation-set data used for model validation and diagnostic checks. The remaining participant files without the `_t` suffix are the fitting-set data used to fit the models.

## Python Setup

Install the Python dependencies:

```bash
python -m pip install -r requirements.txt
```

Regenerate all Python figures:

```bash
python Figure_Code/Figure7.py
python Figure_Code/Figure8a.py
python Figure_Code/Figure8b.py
python Figure_Code/Figure9.py
python Figure_Code/Figure10a.py
python Figure_Code/Figure10b.py
python Figure_Code/Figure11.py
python Figure_Code/Figure12.py
python Figure_Code/Figure13a.py
python Figure_Code/Figure13b.py
```

## R and Stan Setup

The modeling scripts require R with these packages:

- `R.matlab`
- `rstan`
- `parallel`

Run the R scripts from either the repository root or the `Modeling/` directory. The scripts resolve repository-relative paths internally.

## Release Notes

Before public release, confirm that the included data files may be redistributed under the MIT license or describe any separate data-use terms here.

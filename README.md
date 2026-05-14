# Modeling the Dynamics of Trust

This repository contains analysis code, figure-generation scripts, source data, and Stan model files for the article project on modeling the dynamics of trust in human-automation interaction.

## Repository Structure

- `Analysis_Code/`: Python analysis scripts and derived diagnostic tables.
- `Data/`: participant-level MATLAB `.mat` data files used by the modeling scripts.
- `Experiment/`: Expyriment scripts, CARLA driving scenarios, steering-wheel configuration, and video stimuli used for the behavioral experiment.
- `Figure_Code/`: Python scripts for regenerating article figures. Generated SVG files are written to `Figure_Code/Figure/`.
- `Figure_Source_Data/`: tab-delimited source data used by figure scripts.
- `Figures/`: exported article figure images.
- `Modeling/`: R scripts, Stan models, compiled model artifacts, model fits, and utility functions.

## Data Notes

The `Data/` directory contains participant-level MATLAB files. Files ending in `_t.mat` are the validation-set data used for model validation and diagnostic checks. The remaining participant files without the `_t` suffix are the fitting-set data used to fit the models.

## Python Setup

Python 3.9 or 3.10 is recommended for the experiment scripts because Expyriment, PsychoPy, video playback backends, pygame, and CARLA Python APIs can be sensitive to Python and binary-wheel versions.

Create and activate a virtual environment, then install the Python dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

On macOS or Linux, activate the environment with `source .venv/bin/activate`.

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

## Experiment Scripts

The `Experiment/` directory contains two parts of the experimental workflow:

- `Experiment/Expyriment/`: participant-facing Expyriment tasks and local `.mpg` video stimuli.
- `Experiment/Carla/`: CARLA manual-driving and switch-to-manual scenarios controlled with a steering wheel.

The Expyriment scripts use repository-relative video paths, so they can be run from any working directory after the repository is cloned. They use a fixed random seed (`42`) for stimulus-order generation.

Run one Expyriment condition:

```bash
python Experiment/Expyriment/1_experiment.py
python Experiment/Expyriment/2_experiment.py
python Experiment/Expyriment/3_experiment.py
```

The three scripts differ in the AI success/failure probability used during the task:

- `1_experiment.py`: 50% success / 50% failure.
- `2_experiment.py`: 70% success / 30% failure.
- `3_experiment.py`: 90% success / 10% failure.

Participant responses are written through Expyriment's data logging mechanism. The scripts expect the video stimuli to remain in `Experiment/Expyriment/mpg/`.

## CARLA Setup

The CARLA scripts require a running CARLA simulator and a compatible CARLA Python API. Install the CARLA Python API that matches the simulator version you use; this is intentionally not pinned in `requirements.txt` because CARLA API packages must match the local simulator build.

Before running a CARLA scenario:

1. Start the CARLA server.
2. Confirm the host and port, which default to `127.0.0.1:2000`.
3. Configure the steering-wheel axis/button indices in `Experiment/Carla/wheel_config.ini`.
4. Connect exactly one steering wheel or joystick device.

Run a manual-driving scenario:

```bash
python Experiment/Carla/manual/manual_control_steeringwheel_01.py
```

Run a switch-to-manual scenario:

```bash
python Experiment/Carla/switch-manual/switch_steeringwheel_01.py
```

Each scenario has five variants (`01` to `05`). CARLA logs are written beside each script under `manual_control_test_log/`, which is created automatically.

You can override the CARLA connection and display resolution:

```bash
python Experiment/Carla/manual/manual_control_steeringwheel_01.py --host 127.0.0.1 --port 2000 --res 3840x1080
```

## R and Stan Setup

The modeling scripts require R with these packages:

- `R.matlab`
- `rstan`
- `parallel`

Run the R scripts from either the repository root or the `Modeling/` directory. The scripts resolve repository-relative paths internally.

## Reproducibility Notes

- The analysis and figure scripts resolve repository-relative paths and should be run from the repository root unless otherwise noted.
- The Expyriment tasks use fixed random seeds for the trial sequence, but they still require interactive participant input.
- CARLA results depend on the CARLA simulator version, map assets, physics timestep, rendering settings, steering-wheel hardware, and OS-level joystick indexing. Record these settings when collecting new experiment data.
- The provided `wheel_config.ini` is configured for a Logitech G29-style racing wheel. Other devices may require different axis/button indices.
- Generated outputs such as Expyriment data files, CARLA driving logs, compiled Stan artifacts, and regenerated figures should be reviewed before public release.



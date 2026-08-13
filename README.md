# Modeling Psychological and Behavioral Trust Dynamics in Human-ADS Interaction: A Cognitive Process Perspective

[English](#english) | [中文](#中文)

## English

This repository accompanies the article *Modeling Psychological and Behavioral Trust Dynamics in Human-ADS Interaction: A Cognitive Process Perspective* by Xing Pan, Jiacheng Liu, Song Ding, and Chongfeng Li.

The study develops an interpretable and personalized model of trust dynamics in human-automated driving system (ADS) interaction. Based on Bayesian decision theory, the model connects driving-scenario complexity and ADS ability with task-decision confidence, psychological trust, and behavioral trust. A personalized trust threshold maps psychological trust to the driver's rely/takeover decision.

### Repository layout

- `Analysis_Code/`: analysis and diagnostic scripts.
- `Data/`: participant-level MATLAB data.
- `Experiment/`: Expyriment tasks, CARLA scenarios, and stimuli.
- `Modeling/`: R scripts, Stan models, and model outputs.
- `Figure_Code/`: scripts for reproducing the figures.
- `Figure_Source_Data/`: source data used by the figure scripts.
- `Figures/`: exported article figures.

Files ending in `_t.mat` are validation data; the other participant files are fitting data.

### Setup and use

Python 3.9 or 3.10 is recommended:

```bash
python -m venv .venv
python -m pip install -r requirements.txt
```

Activate the environment with `.venv\Scripts\activate` on Windows or `source .venv/bin/activate` on macOS/Linux. Figure scripts can then be run from the repository root, for example:

```bash
python Figure_Code/Figure7.py
```

The modeling workflow requires R with `R.matlab`, `rstan`, and `parallel`. Run the scripts in `Modeling/` from either that directory or the repository root.

The experiment programs are under `Experiment/Expyriment/`. CARLA scenarios require a running CARLA server, a matching Python API, and steering-wheel settings in `Experiment/Carla/wheel_config.ini`.

### License

Released under the [MIT License](LICENSE).

## 中文

本仓库是论文 *Modeling Psychological and Behavioral Trust Dynamics in Human-ADS Interaction: A Cognitive Process Perspective* 的配套资源。论文作者为 Xing Pan、Jiacheng Liu、Song Ding 和 Chongfeng Li。

本研究基于贝叶斯决策理论，构建了可解释、个体化的人类-自动驾驶系统（ADS）交互信任动态模型。模型将驾驶场景复杂度和 ADS 能力与任务决策信心、心理信任及行为信任相联系，并通过个体化信任阈值将心理信任映射为驾驶员的依赖/接管决策。

### 仓库结构

- `Analysis_Code/`：分析与诊断脚本。
- `Data/`：参与者级 MATLAB 数据。
- `Experiment/`：Expyriment 实验、CARLA 场景及刺激材料。
- `Modeling/`：R 脚本、Stan 模型及模型输出。
- `Figure_Code/`：论文图表复现脚本。
- `Figure_Source_Data/`：绘图所用源数据。
- `Figures/`：导出的论文图表。

以 `_t.mat` 结尾的文件为验证集数据，其余参与者文件为模型拟合数据。

### 环境与运行

建议使用 Python 3.9 或 3.10：

```bash
python -m venv .venv
python -m pip install -r requirements.txt
```

Windows 使用 `.venv\Scripts\activate` 激活环境，macOS/Linux 使用 `source .venv/bin/activate`。之后可从仓库根目录运行绘图脚本，例如：

```bash
python Figure_Code/Figure7.py
```

模型分析需要 R，以及 `R.matlab`、`rstan` 和 `parallel` 包。可从仓库根目录或 `Modeling/` 目录运行其中的脚本。

实验程序位于 `Experiment/Expyriment/`。CARLA 场景还需要运行中的 CARLA 服务、版本匹配的 Python API，以及 `Experiment/Carla/wheel_config.ini` 中的方向盘配置。

### 许可证

本项目采用 [MIT License](LICENSE)。

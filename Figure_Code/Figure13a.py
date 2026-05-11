from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["svg.fonttype"] = "none"


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR.parent / "Figure_Source_Data" / "Figure13a.txt"
OUTPUT_DIR = BASE_DIR / "Figure"
OUTPUT_FILE = OUTPUT_DIR / "Figure13a.svg"
DPI = 300
FIGURE_SIZE = (12, 3.8)
AXIS_LABEL_SIZE = 28
TICK_LABEL_SIZE = 22
LEGEND_SIZE = 20
AXIS_LINEWIDTH = 1.2
TICK_WIDTH = 1.2
TICK_LENGTH = 4
BAR_LINEWIDTH = 0.8
MEAN_LINEWIDTH = 1.4

plt.rcParams["font.size"] = TICK_LABEL_SIZE


def load_accuracy_data(input_path):
    table = np.genfromtxt(input_path, delimiter="\t", names=True, dtype=float, encoding="utf-8")
    table = np.atleast_1d(table)
    required_columns = ("subject", "fit_data", "validate_data")
    missing_columns = [column for column in required_columns if column not in table.dtype.names]
    if missing_columns:
        raise ValueError(f"Missing required columns in {input_path}: {', '.join(missing_columns)}")

    subjects = table["subject"].astype(int)
    fit_data = np.asarray(table["fit_data"], dtype=float)
    validate_data = np.asarray(table["validate_data"], dtype=float)

    if np.any(~np.isfinite(fit_data)) or np.any(~np.isfinite(validate_data)):
        raise ValueError(f"{input_path} contains non-numeric or missing accuracy values.")
    return subjects, fit_data, validate_data


subjects, data1, data2 = load_accuracy_data(DATA_PATH)
x = np.arange(len(subjects))

bar_width = 0.34
offset = 0.38

mean_data1 = np.mean(data1)
mean_data2 = np.mean(data2)

fig = plt.figure(figsize=FIGURE_SIZE, facecolor="white")
ax = fig.add_axes([0.08, 0.21, 0.90, 0.50])

ax.bar(
    x - offset / 2,
    data1,
    width=bar_width,
    color="lightblue",
    edgecolor="black",
    linewidth=BAR_LINEWIDTH,
    label="Fit data",
)
ax.bar(
    x + offset / 2,
    data2,
    width=bar_width,
    color="grey",
    edgecolor="black",
    linewidth=BAR_LINEWIDTH,
    label="Validate data",
)

ax.axhline(mean_data1, color="blue", linestyle="--", linewidth=MEAN_LINEWIDTH, label="Fit data mean")
ax.axhline(mean_data2, color="black", linestyle="--", linewidth=MEAN_LINEWIDTH, label="Validate data mean")

ax.set_xlabel("Subject", fontweight="bold", fontsize=AXIS_LABEL_SIZE)
ax.set_ylabel("Accuracy (%)", fontweight="bold", fontsize=AXIS_LABEL_SIZE, labelpad=2)
tick_subjects = np.array([1, 5, 10, 15, 20, 25, 27])
tick_indices = np.array([np.where(subjects == subject)[0][0] for subject in tick_subjects if subject in subjects])
ax.set_xticks(tick_indices)
ax.set_xticklabels([str(subjects[index]) for index in tick_indices], fontsize=TICK_LABEL_SIZE)
ax.tick_params(axis="both", which="major", labelsize=TICK_LABEL_SIZE, width=TICK_WIDTH, length=TICK_LENGTH)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
for spine in ax.spines.values():
    spine.set_linewidth(AXIS_LINEWIDTH)

handles, labels = ax.get_legend_handles_labels()
fig.legend(
    handles,
    labels,
    fontsize=LEGEND_SIZE,
    frameon=False,
    ncol=4,
    loc="upper center",
    bbox_to_anchor=(0.5, 0.98),
    columnspacing=1.0,
    handlelength=1.5,
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
fig.savefig(OUTPUT_FILE, format="svg", dpi=DPI)
plt.close(fig)

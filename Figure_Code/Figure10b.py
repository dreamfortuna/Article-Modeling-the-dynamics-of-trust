from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import get_backend
from scipy import stats


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR.parent / "Figure_Source_Data" / "Figure10b.txt"
OUTPUT_PATH = BASE_DIR / "Figure" / "Figure10b.svg"
ABILITY_ORDER = ["Low ability", "Medium ability", "High ability"]

FONT_FAMILY = "Times New Roman"
AXIS_LABEL_SIZE = 28
TICK_LABEL_SIZE = 22
LEGEND_SIZE = 24
PANEL_LABEL_SIZE = 32
TITLE_SIZE = 28
AXIS_LINEWIDTH = 1.2
TICK_WIDTH = 1.2
TICK_LENGTH = 4
FIGURE_SIZE = (12, 6)
PANEL_BOUNDS = [
    [0.105, 0.20, 0.22, 0.52],
    [0.430, 0.20, 0.22, 0.52],
    [0.755, 0.20, 0.22, 0.52],
]

plt.rcParams["font.family"] = FONT_FAMILY
plt.rcParams["font.size"] = TICK_LABEL_SIZE
plt.rcParams["svg.fonttype"] = "none"


def summarize_by_trial(data):
    rows = []
    for (ability, trial), group in data.groupby(["ability", "trial"], sort=False, observed=True):
        values = group["value"].dropna().to_numpy(dtype=float)
        mean = np.mean(values)
        if len(values) > 1:
            ci_low, ci_high = stats.t.interval(
                0.95,
                len(values) - 1,
                loc=mean,
                scale=stats.sem(values),
            )
        else:
            ci_low = ci_high = mean
        rows.append(
            {
                "ability": ability,
                "trial": int(trial),
                "mean": mean,
                "ci_low": ci_low,
                "ci_high": ci_high,
            }
        )
    return pd.DataFrame(rows)


data = pd.read_csv(DATA_PATH, sep="\t")
data["ability"] = pd.Categorical(data["ability"], categories=ABILITY_ORDER, ordered=True)
summary = summarize_by_trial(data).sort_values(["ability", "trial"])

fig = plt.figure(figsize=FIGURE_SIZE, facecolor="white")
axes = [fig.add_axes(bounds) for bounds in PANEL_BOUNDS]

for ax, ability in zip(axes, ABILITY_ORDER):
    plot_data = summary.loc[summary["ability"] == ability].sort_values("trial")
    x = plot_data["trial"].to_numpy()
    mean = plot_data["mean"].to_numpy()
    ci_low = plot_data["ci_low"].to_numpy()
    ci_high = plot_data["ci_high"].to_numpy()

    ax.plot(x, mean, color="#E6C786", lw=2, label="Mean")
    ax.fill_between(x, ci_low, ci_high, color="lightblue", alpha=0.5, label="95% CI")
    ax.set_title(ability, fontsize=TITLE_SIZE, fontweight="bold")
    ax.set_xlabel("trial", fontsize=AXIS_LABEL_SIZE, fontweight="bold")
    ax.set_ylabel("ADS's perceptual noise", fontsize=AXIS_LABEL_SIZE, fontweight="bold")
    ax.set_xticks(np.arange(5, x.max() + 1, 5))
    ax.tick_params(
        axis="both",
        which="major",
        labelsize=TICK_LABEL_SIZE,
        width=TICK_WIDTH,
        length=TICK_LENGTH,
    )

    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(AXIS_LINEWIDTH)

y_min = summary["ci_low"].min()
y_max = summary["ci_high"].max()
for ax in axes:
    ax.set_ylim(y_min, y_max)

axes[-1].legend(loc="upper right", fontsize=LEGEND_SIZE, frameon=False)
fig.text(0.01, 0.93, "(b)", fontsize=PANEL_LABEL_SIZE, fontweight="bold")

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(OUTPUT_PATH, dpi=300, format="svg")
if "agg" not in get_backend().lower():
    plt.show()
else:
    plt.close(fig)

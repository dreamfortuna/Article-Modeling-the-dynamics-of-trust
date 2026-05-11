from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
SOURCE_TXT = ROOT_DIR / "Figure_Source_Data" / "Figure12.txt"
FIGURE_DIR = BASE_DIR / "Figure"
OUTPUT_FIGURE = FIGURE_DIR / "Figure12.svg"
DPI = 300

FONT_FAMILY = "Times New Roman"
TITLE_SIZE = 28
AXIS_LABEL_SIZE = 28
TICK_LABEL_SIZE = 22
LEGEND_SIZE = 22
PANEL_LABEL_SIZE = 32
AXIS_LINEWIDTH = 1.2
TICK_WIDTH = 1.2
TICK_LENGTH = 4
MEAN_LINEWIDTH = 2.0
ERRORBAR_LINEWIDTH = 1.8

METRIC_LABELS = {
    "accuracy": "Accuracy",
    "balanced_accuracy": "Balanced accuracy",
    "precision": "Precision",
    "f1": "F1-score",
}
METHOD_ORDER = [
    "personalized",
    "fixed_0.5",
    "pooled_youden_threshold",
]
METHOD_SHORT_LABELS = {
    "personalized": "Personalized",
    "fixed_0.5": "Fixed 0.5",
    "pooled_youden_threshold": "Pooled\nYouden",
}
METHOD_FILL_COLORS = {
    "personalized": "#D7E8F4",
    "fixed_0.5": "#E8E8E8",
    "pooled_youden_threshold": "#F6D8C8",
}

plt.rcParams["font.family"] = FONT_FAMILY
plt.rcParams["svg.fonttype"] = "none"


def load_plot_data(input_path: Path) -> pd.DataFrame:
    data = pd.read_csv(input_path, sep="\t")
    required_columns = {"participant", "method", *METRIC_LABELS.keys()}
    missing = sorted(required_columns.difference(data.columns))
    if missing:
        raise ValueError(f"Missing required columns in {input_path}: {', '.join(missing)}")
    data["participant"] = pd.to_numeric(data["participant"], errors="raise").astype(int)
    for metric in METRIC_LABELS:
        data[metric] = pd.to_numeric(data[metric], errors="raise")
    return data


def plot_validation_metric_comparison(participant_metrics: pd.DataFrame, output_path: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14.0, 9.8), sharey=True)
    axes = axes.ravel()
    rng = np.random.default_rng(42)
    panel_labels = ["(a)", "(b)", "(c)", "(d)"]

    for ax, metric, panel_label in zip(axes, METRIC_LABELS, panel_labels):
        means = []
        ci_half_widths = []
        values_by_method = []
        positions = np.arange(len(METHOD_ORDER), dtype=float)

        for method in METHOD_ORDER:
            values = participant_metrics.loc[participant_metrics["method"] == method, metric].to_numpy(dtype=float)
            if len(values) == 0:
                raise ValueError(f"No rows found for method '{method}' in {SOURCE_TXT}")
            values_by_method.append(values)
            means.append(values.mean())
            ci_half_widths.append(1.96 * values.std(ddof=1) / np.sqrt(len(values)))

        violins = ax.violinplot(
            values_by_method,
            positions=positions + 0.18,
            widths=0.50,
            showmeans=False,
            showmedians=False,
            showextrema=False,
        )
        for body, position, method in zip(violins["bodies"], positions + 0.18, METHOD_ORDER):
            body.set_facecolor(METHOD_FILL_COLORS[method])
            body.set_edgecolor("#555555")
            body.set_linewidth(0.75)
            body.set_alpha(0.92)
            vertices = body.get_paths()[0].vertices
            vertices[:, 0] = np.maximum(vertices[:, 0], position)

        for method_index, values in enumerate(values_by_method):
            jitter = rng.uniform(-0.20, -0.04, size=len(values))
            ax.scatter(
                np.full(len(values), positions[method_index]) + jitter,
                values,
                s=24,
                color="#9A9A9A",
                alpha=0.72,
                edgecolors="none",
                zorder=2,
            )

        ax.plot(positions, means, color="black", linewidth=MEAN_LINEWIDTH, zorder=4)
        ax.errorbar(
            positions,
            means,
            yerr=ci_half_widths,
            color="black",
            marker="o",
            markersize=7.0,
            linestyle="none",
            elinewidth=ERRORBAR_LINEWIDTH,
            capsize=5,
            capthick=ERRORBAR_LINEWIDTH,
            markeredgecolor="black",
            markerfacecolor="black",
            markeredgewidth=1.0,
            zorder=5,
        )

        ax.set_title(METRIC_LABELS[metric], fontsize=TITLE_SIZE, fontweight="bold", pad=10)
        ax.set_xticks(positions)
        ax.set_xticklabels(
            [METHOD_SHORT_LABELS[method] for method in METHOD_ORDER],
            fontsize=TICK_LABEL_SIZE,
            fontweight="bold",
        )
        ax.set_xlim(-0.55, len(METHOD_ORDER) - 0.35)
        ax.set_ylim(0, 1.05)
        ax.set_yticks(np.arange(0, 1.01, 0.2))
        ax.tick_params(axis="y", labelsize=TICK_LABEL_SIZE, width=TICK_WIDTH, length=TICK_LENGTH)
        ax.tick_params(axis="x", width=TICK_WIDTH, length=TICK_LENGTH)
        ax.grid(axis="y", color="#E7E7E7", linewidth=0.8)
        ax.set_axisbelow(True)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        for spine in ax.spines.values():
            spine.set_linewidth(AXIS_LINEWIDTH)
        ax.text(
            -0.14,
            1.05,
            panel_label,
            transform=ax.transAxes,
            fontsize=PANEL_LABEL_SIZE,
            fontweight="bold",
            va="bottom",
            ha="left",
            clip_on=False,
        )

    axes[0].set_ylabel("Validation metric", fontweight="bold", fontsize=AXIS_LABEL_SIZE)
    axes[2].set_ylabel("Validation metric", fontweight="bold", fontsize=AXIS_LABEL_SIZE)
    legend_handles = [
        plt.Rectangle((0, 0), 1, 1, facecolor=METHOD_FILL_COLORS["personalized"], edgecolor="#555555", label="Participant distributions"),
        plt.Line2D([0], [0], marker="o", color="black", linestyle="none", markersize=7, label="Mean +/- 95% CI"),
    ]
    axes[0].legend(
        handles=legend_handles,
        frameon=False,
        loc="lower left",
        bbox_to_anchor=(0.02, 0.02),
        fontsize=LEGEND_SIZE,
        handlelength=1.5,
        borderaxespad=0,
    )
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.11, top=0.91, wspace=0.25, hspace=0.46)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, format="svg", dpi=DPI)
    plt.close(fig)


def main() -> None:
    participant_metrics = load_plot_data(SOURCE_TXT)
    plot_validation_metric_comparison(participant_metrics, OUTPUT_FIGURE)
    print(f"Loaded source data: {SOURCE_TXT}")
    print(f"Saved validation metric comparison figure: {OUTPUT_FIGURE}")


if __name__ == "__main__":
    main()

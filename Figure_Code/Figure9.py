from pathlib import Path
import warnings

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.tools.sm_exceptions import ConvergenceWarning


BASE_DIR = Path(__file__).resolve().parent
SOURCE_TXT = BASE_DIR.parent / "Figure_Source_Data" / "Figure9.txt"
OUTPUT_DIR = BASE_DIR / "Figure"
OUTPUT_FILE = OUTPUT_DIR / "Figure9.svg"
DPI = 300

FIGURE_SIZE = (12, 9.2)
AXIS_LABEL_SIZE = 28
TICK_LABEL_SIZE = 22
XTICK_LABEL_SIZE = 24
LEGEND_SIZE = 24
PANEL_LABEL_SIZE = 32
TITLE_SIZE = 28
AXIS_LINEWIDTH = 1.2
TICK_WIDTH = 1.2
TICK_LENGTH = 4
VIOLIN_WIDTH = 0.62
VIOLIN_ALPHA = 0.45
SCATTER_MARKER_SIZE = 4
SCATTER_ALPHA = 0.55
MODEL_LINEWIDTH = 2.2
CI_ALPHA = 0.5
SUMMARY_LINEWIDTH = 1.2
SUMMARY_CAPSIZE = 5
SUMMARY_MARKER_SIZE = 5

plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = TICK_LABEL_SIZE
plt.rcParams["svg.fonttype"] = "none"
warnings.filterwarnings("ignore", category=ConvergenceWarning)


PANEL_ORDER = [1, 3, 2]
PANEL_LABELS = {1: "(a)", 3: "(b)", 2: "(c)"}
PANEL_TITLES = {
    1: "ADS's task reliability",
    2: "Driving scenario complexity",
    3: "Previous choice accuracy",
}
CONDITION_ORDER = {
    1: ["Low", "Med", "High"],
    2: ["Simple", "Relatively Simple", "Average", "Relatively Complex", "Complex"],
    3: ["Wrong", "Right"],
}
CONDITION_CODES = {
    1: [1, 2, 3],
    2: [1, 2, 3, 4, 5],
    3: [0, 1],
}
CONDITION_LABELS = {
    "Relatively Simple": "Rel.\nSimple",
    "Relatively Complex": "Rel.\nComplex",
}
CONDITION_COLORS = {
    1: ["#9ECAE1", "#A1D99B", "#FDD0A2"],
    2: ["#9ECAE1", "#9ED9D3", "#BFD59B", "#F4C97F", "#E79682"],
    3: ["#E79682", "#9ECAE1"],
}


def load_plot_data(input_path: Path) -> pd.DataFrame:
    data = pd.read_csv(input_path, sep="\t")
    required_columns = {"panel", "participant", "trial", "condition_code", "condition", "trust"}
    if not required_columns.issubset(data.columns):
        missing = sorted(required_columns.difference(data.columns))
        raise ValueError(f"Missing required columns in {input_path}: {', '.join(missing)}")
    data["panel"] = pd.to_numeric(data["panel"], errors="raise").astype(int)
    data["participant"] = pd.to_numeric(data["participant"], errors="raise").astype(int)
    data["condition_code"] = pd.to_numeric(data["condition_code"], errors="raise").astype(int)
    data["trust"] = pd.to_numeric(data["trust"], errors="raise")
    return data


def fit_mixedlm(data: pd.DataFrame):
    model = smf.mixedlm("trust ~ condition_code", data, groups=data["participant"])
    return model.fit(reml=False, method="lbfgs", maxiter=1000, disp=False)


def summarize_subject_means(data: pd.DataFrame, condition_order: list[str]) -> pd.DataFrame:
    summary = (
        data.groupby(["condition", "participant"], as_index=False, observed=False)["trust"]
        .mean()
        .assign(condition=lambda df: pd.Categorical(df["condition"], categories=condition_order, ordered=True))
        .sort_values(["condition", "participant"])
    )
    return summary


def prediction_frame(condition_order: list[str], condition_codes: list[int], result) -> pd.DataFrame:
    prediction = pd.DataFrame({"condition": condition_order, "condition_code": condition_codes})
    prediction["predicted"] = result.predict(prediction)
    fixed_cov = result.cov_params().loc[["Intercept", "condition_code"], ["Intercept", "condition_code"]].to_numpy()
    design_matrix = np.column_stack([np.ones(len(condition_codes)), condition_codes])
    prediction_se = np.sqrt(np.diag(design_matrix @ fixed_cov @ design_matrix.T))
    prediction["ci_lower"] = prediction["predicted"] - 1.96 * prediction_se
    prediction["ci_upper"] = prediction["predicted"] + 1.96 * prediction_se
    return prediction


def add_panel_label(fig: plt.Figure, ax: plt.Axes, label: str) -> None:
    bbox = ax.get_position()
    fig.text(
        bbox.x0 - 0.055,
        bbox.y1 + 0.075,
        label,
        fontsize=PANEL_LABEL_SIZE,
        fontweight="bold",
        va="top",
        ha="left",
    )


def draw_half_violin(
    ax: plt.Axes,
    values_by_condition: list[np.ndarray],
    positions: np.ndarray,
    colors: list[str],
) -> None:
    violins = ax.violinplot(
        values_by_condition,
        positions=positions,
        widths=VIOLIN_WIDTH,
        showmeans=False,
        showmedians=False,
        showextrema=False,
    )
    for body, position, color in zip(violins["bodies"], positions, colors):
        body.set_facecolor(color)
        body.set_edgecolor("black")
        body.set_linewidth(0.8)
        body.set_alpha(VIOLIN_ALPHA)
        vertices = body.get_paths()[0].vertices
        center = position
        vertices[:, 0] = np.maximum(vertices[:, 0], center)


def plot_panel(ax: plt.Axes, panel_data: pd.DataFrame, panel: int, rng: np.random.Generator) -> None:
    conditions = CONDITION_ORDER[panel]
    condition_codes = CONDITION_CODES[panel]
    panel_data = panel_data.copy()
    panel_data["condition"] = pd.Categorical(panel_data["condition"], categories=conditions, ordered=True)
    result = fit_mixedlm(panel_data)
    summary = summarize_subject_means(panel_data, conditions)
    prediction = prediction_frame(conditions, condition_codes, result)

    x_positions = np.arange(len(conditions))
    values_by_condition = [
        summary.loc[summary["condition"] == condition, "trust"].to_numpy(dtype=float)
        for condition in conditions
    ]
    draw_half_violin(ax, values_by_condition, x_positions, CONDITION_COLORS[panel])

    for x_position, values in zip(x_positions, values_by_condition):
        jitter = rng.uniform(-0.20, -0.04, size=len(values))
        ax.scatter(
            np.full(len(values), x_position) + jitter,
            values,
            s=SCATTER_MARKER_SIZE ** 2,
            color="gray",
            alpha=SCATTER_ALPHA,
            edgecolors="none",
            zorder=3,
        )
        mean = values.mean()
        sem = values.std(ddof=1) / np.sqrt(len(values))
        ci_half_width = 1.96 * sem
        ax.errorbar(
            x_position - 0.16,
            mean,
            yerr=ci_half_width,
            fmt="o",
            color="black",
            markersize=SUMMARY_MARKER_SIZE,
            elinewidth=SUMMARY_LINEWIDTH,
            capsize=SUMMARY_CAPSIZE,
            capthick=SUMMARY_LINEWIDTH,
            zorder=4,
        )

    predicted = prediction["predicted"].to_numpy()
    ci_lower = prediction["ci_lower"].to_numpy()
    ci_upper = prediction["ci_upper"].to_numpy()
    ax.fill_between(
        x_positions,
        ci_lower,
        ci_upper,
        color="lightblue",
        alpha=CI_ALPHA,
        linewidth=0,
        zorder=1,
    )
    ax.plot(x_positions, predicted, color="black", linewidth=MODEL_LINEWIDTH, zorder=5)

    tick_labels = [CONDITION_LABELS.get(condition, condition) for condition in conditions]
    ax.set_xticks(x_positions)
    ax.set_xticklabels(tick_labels, fontsize=XTICK_LABEL_SIZE, fontweight="bold")
    ax.set_title(PANEL_TITLES[panel], fontsize=TITLE_SIZE, fontweight="bold")
    ax.set_xlim(-0.55, len(conditions) - 0.35)
    ax.set_ylim(0.5, 1.0)
    ax.set_yticks(np.arange(0.5, 1.01, 0.1))
    ax.tick_params(axis="x", which="major", labelsize=XTICK_LABEL_SIZE, width=TICK_WIDTH, length=TICK_LENGTH)
    ax.tick_params(axis="y", which="major", labelsize=TICK_LABEL_SIZE, width=TICK_WIDTH, length=TICK_LENGTH)
    ax.tick_params(axis="y", labelleft=True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for spine in ax.spines.values():
        spine.set_linewidth(AXIS_LINEWIDTH)


def plot_figure(data: pd.DataFrame, output_path: Path) -> None:
    fig = plt.figure(figsize=FIGURE_SIZE, facecolor="white")
    axes = [
        fig.add_axes([0.11, 0.62, 0.34, 0.28]),
        fig.add_axes([0.58, 0.62, 0.31, 0.28]),
        fig.add_axes([0.11, 0.13, 0.78, 0.33]),
    ]
    axes[1].sharey(axes[0])
    axes[2].sharey(axes[0])
    rng = np.random.default_rng(42)
    for ax, panel in zip(axes, PANEL_ORDER):
        plot_panel(ax, data[data["panel"] == panel], panel, rng)
        add_panel_label(fig, ax, PANEL_LABELS[panel])

    for ax in axes:
        ax.set_ylabel("P(Trust)", fontsize=AXIS_LABEL_SIZE, fontweight="bold", labelpad=2)
    legend_handles = [
        Patch(facecolor="#CFEAF1", edgecolor="black", alpha=VIOLIN_ALPHA, label="Participant distributions"),
        Line2D([0], [0], marker="o", color="black", linestyle="none", markersize=SUMMARY_MARKER_SIZE, label="Mean ± 95% CI"),
        Line2D([0], [0], color="black", linewidth=MODEL_LINEWIDTH, label="Mixed-model prediction"),
        Patch(facecolor="lightblue", edgecolor="none", alpha=CI_ALPHA, label="Mixed-model 95% CI"),
    ]
    axes[2].legend(
        handles=[legend_handles[0], legend_handles[2], legend_handles[3]],
        loc="lower left",
        bbox_to_anchor=(0.02, 0.06),
        frameon=False,
        fontsize=LEGEND_SIZE,
        handlelength=1.2,
        borderaxespad=0,
        labelspacing=0.25,
        ncol=1,
        columnspacing=1.0,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, format="svg", dpi=DPI)
    plt.close(fig)


def main() -> None:
    data = load_plot_data(SOURCE_TXT)
    plot_figure(data, OUTPUT_FILE)
    print(f"Loaded source data: {SOURCE_TXT}")
    print(f"Saved raincloud mixed-effects Figure 9: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

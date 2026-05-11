import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from matplotlib import get_backend
from pathlib import Path


FIGURE_SIZE = (8, 6)
FONT_FAMILY = "Times New Roman"
AXIS_LABEL_SIZE = 28
TICK_LABEL_SIZE = 22
PANEL_LABEL_SIZE = 32
XTICK_LABEL_SIZE = 24
ANNOTATION_SIZE = 20
AXIS_LINEWIDTH = 1.2
TICK_WIDTH = 1.2
TICK_LENGTH = 4

plt.rcParams["font.family"] = FONT_FAMILY
plt.rcParams["font.size"] = 12
plt.rcParams["svg.fonttype"] = "none"


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR.parent / "Figure_Source_Data" / "Figure8b.txt"
OUTPUT_PATH = BASE_DIR / "Figure" / "Figure8b.svg"


def load_metric_data(input_path):
    table = np.genfromtxt(input_path, delimiter="\t", names=True, dtype=float, encoding="utf-8")
    table = np.atleast_1d(table)
    required_columns = ("V_WAIC", "V_LOO", "U_WAIC", "U_LOO")
    missing_columns = [column for column in required_columns if column not in table.dtype.names]
    if missing_columns:
        raise ValueError(f"Missing required columns in {input_path}: {', '.join(missing_columns)}")

    data = {column: np.asarray(table[column], dtype=float) for column in required_columns}
    for column, values in data.items():
        if np.any(~np.isfinite(values)):
            raise ValueError(f"Column {column} in {input_path} contains non-numeric or missing values.")
    return data


def mean_diff_ci(diff, confidence=0.95):
    n = len(diff)
    mean_diff = np.mean(diff)
    sem_diff = stats.sem(diff)
    ci = stats.t.interval(confidence, df=n - 1, loc=mean_diff, scale=sem_diff)
    return mean_diff, ci


def rank_biserial_from_wilcoxon(diff):
    non_zero_diff = diff[diff != 0]
    if len(non_zero_diff) == 0:
        return np.nan

    ranks = stats.rankdata(np.abs(non_zero_diff))
    positive_rank_sum = np.sum(ranks[non_zero_diff > 0])
    negative_rank_sum = np.sum(ranks[non_zero_diff < 0])
    total_rank_sum = len(non_zero_diff) * (len(non_zero_diff) + 1) / 2
    return (positive_rank_sum - negative_rank_sum) / total_rank_sum


def paired_model_comparison(model_v, model_u, metric_name):
    # Positive values mean the value-based model has lower WAIC/LOO and is descriptively better.
    diff = model_u - model_v

    wilcoxon_result = stats.wilcoxon(model_u, model_v, zero_method="wilcox", alternative="two-sided")
    ttest_result = stats.ttest_rel(model_u, model_v)
    mean_diff, ci = mean_diff_ci(diff)
    effect_size = mean_diff / np.std(diff, ddof=1)
    rank_biserial = rank_biserial_from_wilcoxon(diff)
    relative_diff = mean_diff / np.mean(model_u) * 100

    print(f"\n{'=' * 15} {metric_name} {'=' * 15}")
    print(f"N subjects: {len(diff)}")
    print(f"Value model mean: {np.mean(model_v):.3f}")
    print(f"Utility model mean: {np.mean(model_u):.3f}")
    print(f"Mean paired difference (U - V): {mean_diff:.3f}")
    print(f"Relative mean difference: {relative_diff:.2f}%")
    print(f"95% CI of mean difference: [{ci[0]:.3f}, {ci[1]:.3f}]")
    print(f"Median paired difference (U - V): {np.median(diff):.3f}")
    print(f"Wilcoxon signed-rank: W = {wilcoxon_result.statistic:.3f}, p = {wilcoxon_result.pvalue:.6f}")
    print(f"Paired t-test: t = {ttest_result.statistic:.3f}, p = {ttest_result.pvalue:.6f}")
    print(f"Cohen's dz: {effect_size:.3f}")
    print(f"Rank-biserial correlation: {rank_biserial:.3f}")

    if wilcoxon_result.pvalue >= 0.05:
        interpretation = (
            f"For {metric_name}, the value-based model showed only a slight descriptive advantage, "
            "and the paired difference was too small relative to its uncertainty to support a strong superiority claim."
        )
    else:
        interpretation = (
            f"For {metric_name}, the value-based model showed a modest but statistically reliable descriptive advantage, "
            "although the absolute improvement was small."
        )

    print("Interpretation:", interpretation)
    return {
        "diff": diff,
        "wilcoxon": wilcoxon_result,
        "ttest": ttest_result,
        "mean_diff": mean_diff,
        "ci": ci,
        "effect_size": effect_size,
        "rank_biserial": rank_biserial,
        "relative_diff": relative_diff,
        "interpretation": interpretation,
    }


def format_p_value(p_value):
    if p_value < 0.001:
        return "p < 0.001"
    return f"p = {p_value:.3f}"


def add_paired_comparison(ax, x1, x2, y, label, height=0.8):
    ax.plot(
        [x1, x1, x2, x2],
        [y, y + height, y + height, y],
        color="black",
        linewidth=AXIS_LINEWIDTH,
        clip_on=False,
    )
    ax.text(
        (x1 + x2) / 2,
        y + height + 0.3,
        label,
        ha="center",
        va="bottom",
        fontsize=ANNOTATION_SIZE,
    )


def plot_metrics(data_dict, waic_results, loo_results):
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    rng = np.random.default_rng(42)
    colors = ["#FFBE7A", "#FFBE7A", "#CFEAF1", "#CFEAF1"]
    x_positions = np.array([0, 1.5, 3.0, 4.5])
    bar_specs = [
        ("Model_V\nWAIC", "V_WAIC"),
        ("Model_V\nPSIS-LOO", "V_LOO"),
        ("Model_U\nWAIC", "U_WAIC"),
        ("Model_U\nPSIS-LOO", "U_LOO"),
    ]

    means = [np.mean(data_dict[key]) for _, key in bar_specs]
    sems = [stats.sem(data_dict[key]) for _, key in bar_specs]
    ax.bar(
        x_positions,
        means,
        width=0.58,
        color=colors,
        edgecolor="black",
        linewidth=1.2,
        zorder=2,
    )

    ax.errorbar(
        x_positions,
        means,
        yerr=sems,
        fmt="none",
        ecolor="black",
        elinewidth=1.2,
        capsize=4,
        capthick=1.2,
        zorder=4,
    )

    for x_position, (_, key) in zip(x_positions, bar_specs):
        values = data_dict[key]
        jitter = rng.uniform(-0.16, 0.16, size=len(values))
        ax.scatter(
            np.full(len(values), x_position) + jitter,
            values,
            s=24,
            color="#7F7F7F",
            alpha=0.85,
            edgecolors="none",
            zorder=5,
        )

    add_paired_comparison(
        ax,
        x_positions[0],
        x_positions[2],
        145.0,
        f"paired {format_p_value(waic_results['wilcoxon'].pvalue)}",
    )
    add_paired_comparison(
        ax,
        x_positions[1],
        x_positions[3],
        155.0,
        f"paired {format_p_value(loo_results['wilcoxon'].pvalue)}",
    )

    ax.set_ylabel("Value", fontsize=AXIS_LABEL_SIZE, fontweight="bold")
    ax.set_xticks(x_positions)
    ax.set_xticklabels([label for label, _ in bar_specs], fontsize=XTICK_LABEL_SIZE, fontweight="bold")
    ax.set_xlim(-0.8, 5.2)
    ax.set_ylim(50, 166)
    ax.set_yticks(np.arange(60, 151, 20))
    ax.tick_params(axis="y", which="major", labelsize=TICK_LABEL_SIZE, width=TICK_WIDTH, length=TICK_LENGTH)
    ax.tick_params(axis="x", which="major", width=TICK_WIDTH, length=TICK_LENGTH)
    ax.text(
        -0.13,
        1.04,
        "(b)",
        transform=ax.transAxes,
        fontsize=PANEL_LABEL_SIZE,
        fontweight="bold",
        va="bottom",
        ha="left",
        clip_on=False,
    )
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for spine in ax.spines.values():
        spine.set_linewidth(AXIS_LINEWIDTH)

    output_path = OUTPUT_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    plt.savefig(output_path, format="svg", dpi=300)
    print(f"\nFigure saved to: {output_path}")
    if "agg" not in get_backend().lower():
        plt.show()
    else:
        plt.close(fig)


metric_data = load_metric_data(DATA_PATH)

waic_results = paired_model_comparison(metric_data["V_WAIC"], metric_data["U_WAIC"], "WAIC")
loo_results = paired_model_comparison(metric_data["V_LOO"], metric_data["U_LOO"], "PSIS-LOO")


plot_metrics(metric_data, waic_results, loo_results)

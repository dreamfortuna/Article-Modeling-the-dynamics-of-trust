from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats


BASE_DIR = Path(__file__).resolve().parent
SOURCE_TXT = (
    BASE_DIR.parent
    / "Figure_Source_Data"
    / "Figure8a.txt"
)
FIGURE_OUTPUT = BASE_DIR / "Figure" / "Figure8a.svg"

FIGURE_SIZE = (8, 6)
FONT_FAMILY = "Times New Roman"
AXIS_LABEL_SIZE = 28
TICK_LABEL_SIZE = 22
LEGEND_SIZE = 24
PANEL_LABEL_SIZE = 32
AXIS_LINEWIDTH = 1.2
TICK_WIDTH = 1.2
TICK_LENGTH = 4

plt.rcParams["font.family"] = FONT_FAMILY
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["font.size"] = 12


def load_source_data(input_path: Path) -> pd.DataFrame:
    """Load the tab-delimited source data exported from the original workbook."""
    data = pd.read_csv(input_path, sep="\t")
    required_columns = {"measure", "subject"}
    if not required_columns.issubset(data.columns):
        raise ValueError("The source text file must contain measure and subject columns.")

    trial_columns = [column for column in data.columns if column.startswith("trial_")]
    if not trial_columns:
        raise ValueError("The source text file must contain trial columns.")

    data["subject"] = pd.to_numeric(data["subject"], errors="raise").astype(int)
    for column in trial_columns:
        data[column] = pd.to_numeric(data[column], errors="raise")

    return data


def compute_correlation_data(source_data: pd.DataFrame) -> pd.DataFrame:
    """Compute subject-level Pearson correlations from the source text data."""
    trial_columns = [column for column in source_data.columns if column.startswith("trial_")]
    value_data = source_data[source_data["measure"] == "Value"].set_index("subject")
    utility_data = source_data[source_data["measure"] == "Utility"].set_index("subject")

    if value_data.empty or utility_data.empty:
        raise ValueError("The source text file must contain Value and Utility rows.")

    subjects = sorted(set(value_data.index).intersection(utility_data.index))
    if not subjects:
        raise ValueError("No matching subjects were found between Value and Utility rows.")

    rows = []
    for subject in subjects:
        value_row = value_data.loc[subject, trial_columns].to_numpy(dtype=float)
        utility_row = utility_data.loc[subject, trial_columns].to_numpy(dtype=float)
        r_value, _ = stats.pearsonr(value_row, utility_row)
        rows.append({"subject": subject, "r": r_value})

    return pd.DataFrame(rows)


def plot_correlations(data: pd.DataFrame, output_path: Path) -> None:
    """Plot subject-level correlations and their mean."""
    subjects = data["subject"].to_numpy()
    correlations = data["r"].to_numpy()
    mean_correlation = correlations.mean()

    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    ax.scatter(
        subjects,
        correlations,
        alpha=0.7,
        edgecolors="w",
        linewidth=0.5,
        label="Subject-level r",
        s=50,
    )
    ax.plot(subjects, correlations, alpha=0.7, color="gray", linestyle="-")
    ax.axhline(
        y=mean_correlation,
        color="r",
        linestyle="--",
        linewidth=1.5,
        label="Mean r",
    )

    ax.set_xlabel("Subject", fontsize=AXIS_LABEL_SIZE, fontweight="bold")
    ax.set_ylabel("Pearson's r", fontsize=AXIS_LABEL_SIZE, fontweight="bold")
    ax.set_xticks([subjects.min(), 5, 10, 15, 20, 25, subjects.max()])
    ax.set_ylim(0, 1.0)
    ax.set_yticks(np.arange(0, 1.1, 0.2))
    ax.tick_params(axis="both", which="major", labelsize=TICK_LABEL_SIZE, width=TICK_WIDTH, length=TICK_LENGTH)
    ax.grid(True, linewidth=0.5, alpha=0.3)
    ax.legend(fontsize=LEGEND_SIZE, frameon=False, loc="lower right")
    ax.text(
        -0.12,
        1.04,
        "(a)",
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

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, format="svg", dpi=300)
    plt.close(fig)


def main() -> None:
    source_data = load_source_data(SOURCE_TXT)
    plot_data = compute_correlation_data(source_data)
    plot_correlations(plot_data, FIGURE_OUTPUT)

    print(f"Loaded source data: {SOURCE_TXT}")
    print(f"Saved figure: {FIGURE_OUTPUT}")
    print(f"Mean r: {plot_data['r'].mean():.6f}")


if __name__ == "__main__":
    main()

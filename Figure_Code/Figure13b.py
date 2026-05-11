from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
SOURCE_TXT = ROOT_DIR / "Figure_Source_Data" / "Figure13b.txt"
OUTPUT_DIR = BASE_DIR / "Figure"
OUTPUT_FILE = OUTPUT_DIR / "Figure13b.svg"
DPI = 300

plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["svg.fonttype"] = "none"

AXIS_LABEL_SIZE = 26
TICK_LABEL_SIZE = 22
LEGEND_SIZE = 17
LEGEND_TITLE_SIZE = 18
AXIS_LINEWIDTH = 1.2
TICK_WIDTH = 1.2
TICK_LENGTH = 4
FIGURE_SIZE = (11, 4.5)

PANEL_ORDER = [1, 2, 3]
CONDITION_ORDER = {
    1: ["Low", "Med", "High"],
    2: ["Simple", "Relatively Simple", "Average", "Relatively Complex", "Complex"],
    3: ["Wrong", "Right"],
}
CONDITION_COLORS = {
    1: {
        "Low": "#8FBBD9",
        "Med": "#4D92BE",
        "High": "#0B5E8E",
    },
    2: {
        "Simple": "#B9D78B",
        "Relatively Simple": "#8DBD6B",
        "Average": "#E5BC74",
        "Relatively Complex": "#D98C74",
        "Complex": "#B64B3B",
    },
    3: {
        "Wrong": "#B9A0D6",
        "Right": "#6C4E9B",
    },
}
PANEL_MARKERS = {
    1: "^",
    2: "o",
    3: "s",
}
SHORT_CONDITION_LABELS = {
    "Relatively Simple": "Rel. simple",
    "Relatively Complex": "Rel. complex",
}


def load_plot_data(input_path: Path) -> pd.DataFrame:
    data = pd.read_csv(input_path, sep="\t")
    required_columns = {
        "panel",
        "condition",
        "condition_code",
        "original_ptrust_mean",
        "validation_ptrust_mean",
    }
    missing = sorted(required_columns.difference(data.columns))
    if missing:
        raise ValueError(f"Missing required columns in {input_path}: {', '.join(missing)}")

    data["panel"] = pd.to_numeric(data["panel"], errors="raise").astype(int)
    data["condition_code"] = pd.to_numeric(data["condition_code"], errors="raise")
    data["original_ptrust_mean"] = pd.to_numeric(data["original_ptrust_mean"], errors="raise")
    data["validation_ptrust_mean"] = pd.to_numeric(data["validation_ptrust_mean"], errors="raise")
    return data.sort_values(["panel", "condition_code"])


def plot_figure(data: pd.DataFrame, output_path: Path) -> None:
    fig = plt.figure(figsize=FIGURE_SIZE, facecolor="white")
    ax = fig.add_axes([0.155, 0.20, 0.455, 0.68])
    legend_ax = fig.add_axes([0.655, 0.21, 0.32, 0.65])
    legend_ax.axis("off")

    for panel in PANEL_ORDER:
        panel_data = data.loc[data["panel"] == panel]
        for row in panel_data.itertuples():
            ax.scatter(
                row.original_ptrust_mean,
                row.validation_ptrust_mean,
                s=105,
                marker=PANEL_MARKERS[panel],
                color=CONDITION_COLORS[panel][row.condition],
                edgecolor="black",
                linewidth=0.7,
                alpha=0.95,
            )

    lower = min(data["original_ptrust_mean"].min(), data["validation_ptrust_mean"].min()) - 0.025
    upper = max(data["original_ptrust_mean"].max(), data["validation_ptrust_mean"].max()) + 0.025
    ax.plot([lower, upper], [lower, upper], linestyle="--", color="#777777", linewidth=AXIS_LINEWIDTH)
    ax.set_xlim(lower, upper)
    ax.set_ylim(lower, upper)

    ax.set_xlabel("Fitting set mean P(Trust)", fontsize=AXIS_LABEL_SIZE, fontweight="bold")
    ax.set_ylabel("Validation set mean\nP(Trust)", fontsize=AXIS_LABEL_SIZE, fontweight="bold", labelpad=4)
    ax.tick_params(axis="both", labelsize=TICK_LABEL_SIZE, width=TICK_WIDTH, length=TICK_LENGTH)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for spine in ax.spines.values():
        spine.set_linewidth(AXIS_LINEWIDTH)

    add_grouped_legend(legend_ax)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, format="svg", dpi=DPI)
    plt.close(fig)


def add_grouped_legend(ax: plt.Axes) -> None:
    legend_layout = [
        {
            "panel": 1,
            "title": "ADS's reliability",
            "title_xy": (0.02, 0.96),
            "marker_x": 0.04,
            "label_x": 0.11,
            "item_ys": [0.84, 0.74, 0.64],
        },
        {
            "panel": 3,
            "title": "Previous accuracy",
            "title_xy": (0.02, 0.44),
            "marker_x": 0.04,
            "label_x": 0.11,
            "item_ys": [0.32, 0.22],
        },
        {
            "panel": 2,
            "title": "Scenario complexity",
            "title_xy": (0.55, 0.96),
            "marker_x": 0.57,
            "label_x": 0.65,
            "item_ys": [0.84, 0.74, 0.64, 0.54, 0.44],
        },
    ]

    for group in legend_layout:
        panel = group["panel"]
        ax.text(
            *group["title_xy"],
            group["title"],
            transform=ax.transAxes,
            fontsize=LEGEND_TITLE_SIZE,
            fontweight="bold",
            ha="left",
            va="top",
            zorder=6,
        )
        for condition, y_position in zip(CONDITION_ORDER[panel], group["item_ys"]):
            ax.scatter(
                group["marker_x"],
                y_position,
                transform=ax.transAxes,
                s=72,
                marker=PANEL_MARKERS[panel],
                color=CONDITION_COLORS[panel][condition],
                edgecolor="black",
                linewidth=0.7,
                zorder=6,
            )
            ax.text(
                group["label_x"],
                y_position,
                SHORT_CONDITION_LABELS.get(condition, condition),
                transform=ax.transAxes,
                fontsize=LEGEND_SIZE,
                ha="left",
                va="center",
                zorder=6,
            )


def main() -> None:
    data = load_plot_data(SOURCE_TXT)
    plot_figure(data, OUTPUT_FILE)
    print(f"Loaded source data: {SOURCE_TXT}")
    print(f"Saved Figure 13b: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize_scalar


BASE_DIR = Path(__file__).resolve().parent
SOURCE_TXT = BASE_DIR.parent / "Figure_Source_Data" / "Figure11.txt"
OUTPUT_DIR = BASE_DIR / "Figure"
OUTPUT_FILE = OUTPUT_DIR / "Figure11.svg"
DPI = 300

FIGURE_SIZE = (14, 6)
AXIS_LABEL_SIZE = 28
TICK_LABEL_SIZE = 22
LEGEND_SIZE = 24
PANEL_LABEL_SIZE = 32
TITLE_SIZE = 28
ANNOTATION_SIZE = 24
AXIS_LINEWIDTH = 1.2
TICK_WIDTH = 1.2
TICK_LENGTH = 4
SCATTER_SIZE = 50
SCATTER_EDGE_WIDTH = 0.5
THRESHOLD_LINEWIDTH = 1.5

plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = TICK_LABEL_SIZE
plt.rcParams["svg.fonttype"] = "none"


def load_plot_data(input_path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Load participant 009 plotting data from a tab-delimited source file."""
    table = np.genfromtxt(input_path, delimiter="\t", names=True, dtype=float, encoding="utf-8")
    table = np.atleast_1d(table)
    required_columns = ("trial", "p_trust", "true_label")
    missing_columns = [column for column in required_columns if column not in table.dtype.names]
    if missing_columns:
        raise ValueError(f"Missing required columns in {input_path}: {', '.join(missing_columns)}")

    x_values = np.asarray(table["p_trust"], dtype=float)
    y_values = np.asarray(table["true_label"], dtype=int)
    if np.any(~np.isfinite(x_values)) or np.any(~np.isin(y_values, [0, 1])):
        raise ValueError(f"{input_path} contains invalid P(trust) or true-label values.")

    return x_values, y_values


def find_optimal_threshold(x_values: np.ndarray, y_values: np.ndarray) -> float:
    """Find the threshold that maximizes binary-classification accuracy."""
    def objective_function(threshold: float) -> float:
        y_pred = (x_values > threshold).astype(int)
        return -binary_accuracy(y_values, y_pred)

    result = minimize_scalar(
        objective_function,
        bounds=(x_values.min(), x_values.max()),
        method="bounded",
        options={"xatol": 1e-8},
    )
    return float(result.x)


def binary_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(y_true == y_pred))


def binary_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    matrix = np.zeros((2, 2), dtype=int)
    for true_label, predicted_label in zip(y_true, y_pred):
        matrix[int(true_label), int(predicted_label)] += 1
    return matrix


def add_panel_label(ax: plt.Axes, label: str) -> None:
    """Add a panel label outside the upper-left corner of an axis."""
    ax.text(
        -0.13,
        1.04,
        label,
        transform=ax.transAxes,
        fontsize=PANEL_LABEL_SIZE,
        fontweight="bold",
        va="bottom",
        ha="left",
        clip_on=False,
    )


def draw_threshold_panel(ax: plt.Axes, x_values: np.ndarray, y_values: np.ndarray, threshold: float) -> None:
    """Draw participant 009 labels and the fitted decision threshold."""
    ax.scatter(
        x_values,
        y_values,
        label="True labels",
        alpha=0.65,
        edgecolors="white",
        linewidth=SCATTER_EDGE_WIDTH,
        s=SCATTER_SIZE,
    )
    ax.axvline(threshold, color="red", linestyle="--", linewidth=THRESHOLD_LINEWIDTH, label="Threshold")

    ax.set_xlabel("P(trust)", fontsize=AXIS_LABEL_SIZE, fontweight="bold")
    ax.set_ylabel("Truth", fontsize=AXIS_LABEL_SIZE, fontweight="bold")
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["Distrust", "Trust"], fontsize=TICK_LABEL_SIZE)
    ax.tick_params(axis="x", labelsize=TICK_LABEL_SIZE, width=TICK_WIDTH, length=TICK_LENGTH)
    ax.tick_params(axis="y", width=TICK_WIDTH, length=TICK_LENGTH)
    ax.set_title("Participant 009", fontsize=TITLE_SIZE, fontweight="bold")
    ax.legend(fontsize=LEGEND_SIZE, frameon=False, loc="best")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for spine in ax.spines.values():
        spine.set_linewidth(AXIS_LINEWIDTH)
    add_panel_label(ax, "(a)")


def draw_confusion_matrix_panel(fig: plt.Figure, ax: plt.Axes, y_values: np.ndarray, y_pred: np.ndarray) -> None:
    """Draw the confusion matrix for participant 009."""
    matrix = binary_confusion_matrix(y_values, y_pred)
    image = ax.imshow(matrix, cmap="Blues")

    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(["Distrust", "Trust"], fontsize=TICK_LABEL_SIZE)
    ax.set_yticklabels(["Distrust", "Trust"], fontsize=TICK_LABEL_SIZE)
    ax.set_xlabel("Predicted", fontsize=AXIS_LABEL_SIZE, fontweight="bold")
    ax.set_ylabel("Truth", fontsize=AXIS_LABEL_SIZE, fontweight="bold")

    text_threshold = matrix.max() / 2
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            text_color = "white" if matrix[row, column] > text_threshold else "black"
            ax.text(
                column,
                row,
                f"{matrix[row, column]:d}",
                ha="center",
                va="center",
                color=text_color,
                fontsize=ANNOTATION_SIZE,
            )

    ax.tick_params(axis="both", width=TICK_WIDTH, length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)

    colorbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    colorbar.ax.tick_params(labelsize=TICK_LABEL_SIZE, width=TICK_WIDTH, length=TICK_LENGTH)
    add_panel_label(ax, "(b)")


def plot_combined_figure(x_values: np.ndarray, y_values: np.ndarray, threshold: float, output_path: Path) -> None:
    """Save a combined Figure 11 SVG with threshold and confusion-matrix panels."""
    y_pred = (x_values > threshold).astype(int)
    fig, axes = plt.subplots(
        1,
        2,
        figsize=FIGURE_SIZE,
        gridspec_kw={"width_ratios": [1.25, 1.0]},
    )

    draw_threshold_panel(axes[0], x_values, y_values, threshold)
    draw_confusion_matrix_panel(fig, axes[1], y_values, y_pred)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.subplots_adjust(left=0.08, right=0.96, bottom=0.18, top=0.84, wspace=0.38)
    fig.savefig(output_path, format="svg", dpi=DPI)
    plt.close(fig)


def main() -> None:
    x_values, y_values = load_plot_data(SOURCE_TXT)
    threshold = find_optimal_threshold(x_values, y_values)
    y_pred = (x_values > threshold).astype(int)
    accuracy = binary_accuracy(y_values, y_pred)

    plot_combined_figure(x_values, y_values, threshold, OUTPUT_FILE)

    print(f"Loaded source data: {SOURCE_TXT}")
    print(f"Participant 009 optimal threshold: {threshold:.6f}")
    print(f"Participant 009 accuracy: {accuracy:.6f}")
    print(f"Saved combined Figure 11: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import splev, splrep


DPI = 300
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "Figure"
OUTPUT_FILE = OUTPUT_DIR / "Figure7.svg"

plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 12
plt.rcParams["svg.fonttype"] = "none"

lambda_ = 2.237256
alpha = 0.38651
beta = 0.382152
x_range = np.linspace(-4, 4, 100)


def value_function(x, alpha, lambda_, beta):
    """Compute the prospect theory value function v(x)."""
    y = np.empty_like(x)
    gains = x >= 0
    y[gains] = x[gains] ** alpha
    y[~gains] = -lambda_ * (-x[~gains]) ** beta
    return y


y_value = value_function(x_range, alpha, lambda_, beta)

spl = splrep(x_range, y_value, s=0)
y_smooth = splev(x_range, spl)

plt.figure(figsize=(6, 6))

plt.plot(
    x_range,
    y_smooth,
    label=f"Value Function\nalpha={alpha:.4f}, beta={beta:.4f}, lambda={lambda_:.4f}",
    color="#F27970",
    linewidth=2,
)

plt.axhline(0, color="black", linewidth=2)
plt.axvline(0, color="black", linewidth=2)

plt.plot([-4, 4], [-4, -4], color="black", linewidth=4)
plt.plot([-4, 4], [4, 4], color="black", linewidth=4)
plt.plot([-4, -4], [-4, 4], color="black", linewidth=4)
plt.plot([4, 4], [-4, 4], color="black", linewidth=4)

plt.xlim(-4, 4)
plt.ylim(-4, 4)

plt.xticks(np.arange(-4, 5, 1), fontsize=18)
plt.yticks(np.arange(-4, 5, 1), fontsize=18)

plt.xlabel("Value", fontsize=24, fontweight="bold")
plt.ylabel("Utility", fontsize=24, fontweight="bold")

plt.grid(False)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
plt.tight_layout()
plt.savefig(OUTPUT_FILE, format="svg", dpi=DPI)

plt.close()
print(f"Saved SVG figure: {OUTPUT_FILE.resolve()}")

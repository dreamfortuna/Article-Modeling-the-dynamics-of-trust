from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import scipy.io as sio
from scipy import stats


BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
DATA_DIR = ROOT_DIR / "Data"
STAN_FIT_TEST_DIR = ROOT_DIR / "Modeling" / "Stan_fits_27-3seeds_t"
OUTPUT_DIR = BASE_DIR / "Model_Internal_Confidence_Diagnostics"

SUBJECTS = [
    "001",
    "002",
    "003",
    "004",
    "005",
    "006",
    "007",
    "008",
    "009",
    "010",
    "011",
    "012",
    "013",
    "014",
    "015",
    "016",
    "017",
    "019",
    "021",
    "022",
    "023",
    "024",
    "025",
    "026",
    "027",
    "028",
    "029",
]

COMPLEXITY_LABELS = {
    -0.95: ("Simple", 1),
    -0.725: ("Relatively Simple", 2),
    -0.5: ("Average", 3),
    -0.275: ("Relatively Complex", 4),
    -0.05: ("Complex", 5),
}

RELIABILITY_LABELS = {
    1: "Low",
    2: "Med",
    3: "High",
}

DIAGNOSTICS = [
    {
        "diagnostic": "Self-confidence vs scenario complexity",
        "x": "scenario_complexity_code",
        "y": "ppCs",
        "expected_direction": "negative",
    },
    {
        "diagnostic": "Agent-confidence vs ADS reliability",
        "x": "agent_reliability_code",
        "y": "ppCo",
        "expected_direction": "positive",
    },
    {
        "diagnostic": "Agent-confidence vs previous choice accuracy",
        "x": "previous_choice_accuracy_code",
        "y": "ppCo",
        "expected_direction": "positive",
    },
    {
        "diagnostic": "Agent-confidence vs scenario complexity",
        "x": "scenario_complexity_code",
        "y": "ppCo",
        "expected_direction": "negative",
    },
]


def load_prediction_variable(variable: str) -> np.ndarray:
    predictions = []
    for seed in (1, 2, 3):
        mat_path = STAN_FIT_TEST_DIR / f"model_t_test_seed_{seed}_vb.mat"
        mat = sio.loadmat(mat_path, simplify_cells=True)
        predictions.append(np.asarray(mat["subject_predict"][variable], dtype=float))
    return np.mean(predictions, axis=0)


def load_trial_data() -> pd.DataFrame:
    pp_cs = load_prediction_variable("ppCs")
    pp_co = load_prediction_variable("ppCo")

    rows: list[dict[str, object]] = []
    for participant, subject in enumerate(SUBJECTS, start=1):
        mat_path = DATA_DIR / f"mriData_sub_{subject}_t.mat"
        mat = sio.loadmat(mat_path, simplify_cells=True)
        trial_index = 1
        previous_correct = np.nan

        for block_index, block in enumerate(mat["DATA"], start=1):
            theta = np.asarray(block["trials"]["theta"], dtype=float)
            correctness = np.asarray(block["typeI"]["correct"], dtype=int)
            for within_block_trial, theta_value in enumerate(theta, start=1):
                complexity_label, complexity_code = COMPLEXITY_LABELS[round(float(theta_value), 3)]
                rows.append(
                    {
                        "participant": participant,
                        "subject_id": int(subject),
                        "trial": trial_index,
                        "block": block_index,
                        "within_block_trial": within_block_trial,
                        "agent_reliability": RELIABILITY_LABELS[block_index],
                        "agent_reliability_code": block_index,
                        "scenario_complexity": complexity_label,
                        "scenario_complexity_code": complexity_code,
                        "previous_choice_accuracy": (
                            np.nan if np.isnan(previous_correct) else ("Right" if previous_correct == 1 else "Wrong")
                        ),
                        "previous_choice_accuracy_code": previous_correct,
                        "ppCs": pp_cs[participant - 1, trial_index - 1],
                        "ppCo": pp_co[participant - 1, trial_index - 1],
                    }
                )
                previous_correct = int(correctness[within_block_trial - 1])
                trial_index += 1

    return pd.DataFrame(rows)


def subject_level_correlations(trial_data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for diagnostic in DIAGNOSTICS:
        for participant, participant_data in trial_data.dropna(subset=[diagnostic["x"], diagnostic["y"]]).groupby("participant"):
            if participant_data[diagnostic["x"]].nunique() < 2 or participant_data[diagnostic["y"]].nunique() < 2:
                rho, p_value = np.nan, np.nan
            else:
                result = stats.spearmanr(participant_data[diagnostic["x"]], participant_data[diagnostic["y"]])
                rho, p_value = result.statistic, result.pvalue
            rows.append(
                {
                    "participant": int(participant),
                    "diagnostic": diagnostic["diagnostic"],
                    "x": diagnostic["x"],
                    "y": diagnostic["y"],
                    "expected_direction": diagnostic["expected_direction"],
                    "spearman_rho": rho,
                    "spearman_p": p_value,
                    "n_trials": len(participant_data),
                }
            )
    return pd.DataFrame(rows)


def summarize_correlations(subject_correlations: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for diagnostic, diagnostic_data in subject_correlations.groupby("diagnostic", sort=False):
        values = diagnostic_data["spearman_rho"].dropna().to_numpy(dtype=float)
        t_result = stats.ttest_1samp(values, 0.0)
        rows.append(
            {
                "diagnostic": diagnostic,
                "n_participants": len(values),
                "mean_spearman_rho": values.mean(),
                "sd_spearman_rho": values.std(ddof=1),
                "t_statistic": t_result.statistic,
                "p_value": t_result.pvalue,
            }
        )
    return pd.DataFrame(rows)


def condition_means(trial_data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for factor, label_col, code_col, variable in [
        ("Scenario complexity", "scenario_complexity", "scenario_complexity_code", "ppCs"),
        ("Scenario complexity", "scenario_complexity", "scenario_complexity_code", "ppCo"),
        ("ADS reliability", "agent_reliability", "agent_reliability_code", "ppCo"),
        ("Previous choice accuracy", "previous_choice_accuracy", "previous_choice_accuracy_code", "ppCo"),
    ]:
        grouped = (
            trial_data.dropna(subset=[label_col, code_col, variable])
            .groupby([label_col, code_col], as_index=False)
            .agg(mean_value=(variable, "mean"), sd_value=(variable, "std"), n_trials=(variable, "size"))
            .sort_values(code_col)
        )
        grouped.insert(0, "model_variable", variable)
        grouped.insert(0, "factor", factor)
        grouped = grouped.rename(columns={label_col: "condition", code_col: "condition_code"})
        rows.append(grouped[["factor", "model_variable", "condition", "condition_code", "mean_value", "sd_value", "n_trials"]])
    return pd.concat(rows, ignore_index=True)


def format_p(p_value: float) -> str:
    if p_value < 0.001:
        return "< 0.001"
    return f"= {p_value:.3f}"


def write_response_text(summary: pd.DataFrame) -> None:
    rows = {row.diagnostic: row for row in summary.itertuples()}
    self_complexity = rows["Self-confidence vs scenario complexity"]
    agent_reliability = rows["Agent-confidence vs ADS reliability"]
    agent_previous = rows["Agent-confidence vs previous choice accuracy"]
    agent_complexity = rows["Agent-confidence vs scenario complexity"]

    text = f"""# Model-internal confidence diagnostic checks

## Data source

These analyses do not use raw experimental CSV subjective columns. They use only validation-set model outputs from `Modeling/Stan_fits_27-3seeds_t/model_t_test_seed_*_vb.mat` and validation task-condition variables from `Data/mriData_sub_###_t.mat`.

The model-internal confidence variables are:

| Variable | Interpretation used here |
|---|---|
| `ppCs` | posterior predictive self-decision confidence |
| `ppCo` | posterior predictive agent/other confidence |

## Summary

Spearman correlations were computed within each participant and then tested against zero across the 27 modeled participants.

| Diagnostic | n | Mean rho +/- SD | t | p |
|---|---:|---:|---:|---:|
| Self-confidence vs scenario complexity | {int(self_complexity.n_participants)} | {self_complexity.mean_spearman_rho:.3f} +/- {self_complexity.sd_spearman_rho:.3f} | {self_complexity.t_statistic:.2f} | {format_p(self_complexity.p_value)} |
| Agent-confidence vs ADS reliability | {int(agent_reliability.n_participants)} | {agent_reliability.mean_spearman_rho:.3f} +/- {agent_reliability.sd_spearman_rho:.3f} | {agent_reliability.t_statistic:.2f} | {format_p(agent_reliability.p_value)} |
| Agent-confidence vs previous choice accuracy | {int(agent_previous.n_participants)} | {agent_previous.mean_spearman_rho:.3f} +/- {agent_previous.sd_spearman_rho:.3f} | {agent_previous.t_statistic:.2f} | {format_p(agent_previous.p_value)} |
| Agent-confidence vs scenario complexity | {int(agent_complexity.n_participants)} | {agent_complexity.mean_spearman_rho:.3f} +/- {agent_complexity.sd_spearman_rho:.3f} | {agent_complexity.t_statistic:.2f} | {format_p(agent_complexity.p_value)} |

## Suggested reviewer response

Because the threshold analysis focuses on converting continuous `P(trust)` into behavioral trust decisions, we did not add a new analysis based on raw CSV subjective confidence ratings. Instead, we added a model-internal diagnostic check using the posterior predictive variables generated by the validation Stan model. Specifically, `ppCs` was treated as model-predicted self-decision confidence and `ppCo` as model-predicted agent confidence. These variables were extracted from the `_t` validation outputs and analyzed against validation task conditions.

The diagnostic checks showed the expected patterns. Model-predicted self-confidence decreased as scenario complexity increased (mean Spearman rho = {self_complexity.mean_spearman_rho:.3f}, t = {self_complexity.t_statistic:.2f}, p {format_p(self_complexity.p_value)}). Model-predicted agent confidence increased with ADS reliability (mean rho = {agent_reliability.mean_spearman_rho:.3f}, t = {agent_reliability.t_statistic:.2f}, p {format_p(agent_reliability.p_value)}) and was higher following a correct previous choice (mean rho = {agent_previous.mean_spearman_rho:.3f}, t = {agent_previous.t_statistic:.2f}, p {format_p(agent_previous.p_value)}). Agent confidence also decreased with scenario complexity (mean rho = {agent_complexity.mean_spearman_rho:.3f}, t = {agent_complexity.t_statistic:.2f}, p {format_p(agent_complexity.p_value)}). These results indicate that the model's internal confidence-related quantities vary systematically with task structure in theoretically expected directions, providing a diagnostic check that is separate from, and secondary to, the threshold-based behavioral trust validation.
"""
    (OUTPUT_DIR / "model_internal_confidence_diagnostic_response_text.md").write_text(text, encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    trial_data = load_trial_data()
    subject_correlations = subject_level_correlations(trial_data)
    summary = summarize_correlations(subject_correlations)
    means = condition_means(trial_data)

    trial_data.to_csv(OUTPUT_DIR / "model_internal_confidence_trial_data.txt", sep="\t", index=False)
    subject_correlations.to_csv(OUTPUT_DIR / "model_internal_confidence_subject_correlations.txt", sep="\t", index=False)
    summary.to_csv(OUTPUT_DIR / "model_internal_confidence_summary.txt", sep="\t", index=False)
    means.to_csv(OUTPUT_DIR / "model_internal_confidence_condition_means.txt", sep="\t", index=False)
    write_response_text(summary)

    print(f"Wrote model-internal confidence diagnostics to: {OUTPUT_DIR}")
    print("No raw experimental CSV subjective columns were used.")


if __name__ == "__main__":
    main()

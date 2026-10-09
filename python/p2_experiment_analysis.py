"""P2: Onboarding checklist A/B experiment readout."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "outputs"
FIG = OUT / "figures"


def proportion_test(success_a: int, n_a: int, success_b: int, n_b: int) -> dict:
    """Two-proportion z-test (treatment vs control)."""
    p_a = success_a / n_a
    p_b = success_b / n_b
    p_pool = (success_a + success_b) / (n_a + n_b)
    se = np.sqrt(p_pool * (1 - p_pool) * (1 / n_a + 1 / n_b))
    z = (p_b - p_a) / se if se > 0 else 0.0
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))
    # Normal approx CI for difference
    se_unpooled = np.sqrt(p_a * (1 - p_a) / n_a + p_b * (1 - p_b) / n_b)
    ci_low = (p_b - p_a) - 1.96 * se_unpooled
    ci_high = (p_b - p_a) + 1.96 * se_unpooled
    return {
        "control_rate": p_a,
        "treatment_rate": p_b,
        "lift_abs": p_b - p_a,
        "lift_rel": (p_b / p_a - 1) if p_a else None,
        "z": float(z),
        "p_value": float(p_value),
        "ci95_low": float(ci_low),
        "ci95_high": float(ci_high),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)

    flags = pd.read_csv(OUT / "p1_user_product_flags.csv")
    metrics = ["activated", "adopted_any_feature", "retained_d1", "retained_d7", "retained_d30"]

    rows = []
    readout = {}
    for m in metrics:
        g = flags.groupby("experiment_variant")[m].agg(["sum", "count"])
        control = g.loc["control"]
        treatment = g.loc["treatment"]
        res = proportion_test(
            int(control["sum"]), int(control["count"]), int(treatment["sum"]), int(treatment["count"])
        )
        res["metric"] = m
        res["n_control"] = int(control["count"])
        res["n_treatment"] = int(treatment["count"])
        rows.append(res)
        readout[m] = res

    results = pd.DataFrame(rows)
    results.to_csv(OUT / "p2_experiment_results.csv", index=False)

    # Decision rule: primary = activation; guardrails = d7 retention
    primary = readout["activated"]
    guardrail = readout["retained_d7"]
    if primary["p_value"] < 0.05 and primary["lift_abs"] > 0 and guardrail["lift_abs"] >= -0.01:
        decision = "SHIP"
        rationale = "Activation lift is significant with non-negative D7 retention guardrail."
    elif primary["p_value"] < 0.05 and primary["lift_abs"] > 0:
        decision = "ITERATE"
        rationale = "Activation improved but guardrail retention movement needs review."
    else:
        decision = "HOLD / KILL"
        rationale = "No clear significant activation win under the pre-registered primary metric."

    decision_doc = {
        "experiment": "onboarding_checklist_v1",
        "hypothesis": "A guided onboarding checklist increases activation_success within 3 days without harming D7 retention.",
        "primary_metric": "activated",
        "guardrail_metrics": ["retained_d7"],
        "decision": decision,
        "rationale": rationale,
        "primary_result": primary,
        "guardrail_result": guardrail,
    }
    (OUT / "p2_experiment_decision.json").write_text(json.dumps(decision_doc, indent=2), encoding="utf-8")

    plot_df = results.set_index("metric")[["control_rate", "treatment_rate"]]
    ax = plot_df.plot(kind="bar", figsize=(9, 4.5), color=["#6B7280", "#0B3D5C"])
    ax.set_ylabel("Rate")
    ax.set_title("P2 Experiment Readout: Control vs Treatment")
    ax.set_ylim(0, 1)
    ax.legend(loc="upper right")
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(FIG / "p2_experiment.png", dpi=150)
    plt.close()

    print(json.dumps({"decision": decision, "primary_lift_abs": primary["lift_abs"], "p_value": primary["p_value"]}, indent=2))


if __name__ == "__main__":
    main()

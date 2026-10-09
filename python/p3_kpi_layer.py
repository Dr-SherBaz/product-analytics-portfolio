"""P3: Build certified-style KPI marts (dbt-equivalent tables in pandas/SQL outputs)."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
PROC = ROOT / "data" / "processed"


def main() -> None:
    PROC.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    flags = pd.read_csv(OUT / "p1_user_product_flags.csv", parse_dates=["signup_date"])

    # Mart: daily product health
    daily = (
        flags.groupby("signup_date")
        .agg(
            signups=("user_id", "count"),
            activated_users=("activated", "sum"),
            adopted_users=("adopted_any_feature", "sum"),
            retained_d7_users=("retained_d7", "sum"),
        )
        .reset_index()
        .rename(columns={"signup_date": "metric_date"})
    )
    daily["activation_rate"] = daily["activated_users"] / daily["signups"]
    daily["adoption_rate"] = daily["adopted_users"] / daily["signups"]
    daily["d7_retention_rate"] = daily["retained_d7_users"] / daily["signups"]

    # Mart: user grain certified flags
    fct_user_product = flags[
        [
            "user_id",
            "signup_date",
            "experiment_variant",
            "acquisition_channel",
            "country",
            "activated",
            "adopted_any_feature",
            "tts",
            "voice_clone",
            "api",
            "retained_d1",
            "retained_d7",
            "retained_d30",
        ]
    ].copy()

    # Simple data tests (dbt-test analogues)
    tests = {
        "unique_user_id": int(fct_user_product["user_id"].is_unique),
        "not_null_signup_date": int(fct_user_product["signup_date"].notna().all()),
        "activation_in_0_1": int(fct_user_product["activated"].isin([0, 1]).all()),
        "retention_lte_activation_share": float(
            fct_user_product.loc[fct_user_product["retained_d7"] == 1, "activated"].mean()
        ),
    }

    daily.to_csv(PROC / "mart_daily_product_health.csv", index=False)
    fct_user_product.to_csv(PROC / "fct_user_product_kpis.csv", index=False)
    (OUT / "p3_data_tests.json").write_text(json.dumps(tests, indent=2), encoding="utf-8")

    metric_dictionary = {
        "activation_success": "User completes first valuable generation within 3 days of signup.",
        "feature_adoption": "User uses at least one core feature (tts, voice_clone, api) after activation.",
        "retained_d7": "User starts a session on day 7 relative to activation date.",
        "activation_rate": "activated_users / signups for the cohort date.",
        "certified_layer": "fct_user_product_kpis + mart_daily_product_health with uniqueness/range tests.",
    }
    (ROOT / "docs" / "metric_dictionary.json").write_text(
        json.dumps(metric_dictionary, indent=2), encoding="utf-8"
    )
    print(json.dumps(tests, indent=2))


if __name__ == "__main__":
    main()

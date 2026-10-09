"""P1: Activation & onboarding funnel + cohort retention."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "outputs"
FIG = OUT / "figures"


def load() -> tuple[pd.DataFrame, pd.DataFrame]:
    users = pd.read_csv(RAW / "users.csv", parse_dates=["signup_date"])
    events = pd.read_csv(RAW / "events.csv", parse_dates=["event_ts"])
    return users, events


def build_user_flags(users: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    activated = (
        events.loc[events["event_name"] == "activation_success", ["user_id", "event_ts"]]
        .groupby("user_id", as_index=False)
        .agg(activated_at=("event_ts", "min"))
    )
    features = events.loc[events["event_name"] == "feature_used"].copy()
    features["feature"] = features["properties_json"].str.extract(r'"feature":"([^"]+)"')
    feature_flags = (
        features.pivot_table(index="user_id", columns="feature", values="event_id", aggfunc="count")
        .fillna(0)
        .gt(0)
        .astype(int)
        .reset_index()
    )
    sessions = events.loc[events["event_name"] == "session_start"].copy()
    sessions["retention_day"] = sessions["properties_json"].str.extract(r'"retention_day":(\d+)').astype(float)
    ret = (
        sessions.pivot_table(index="user_id", columns="retention_day", values="event_id", aggfunc="count")
        .fillna(0)
        .gt(0)
        .astype(int)
    )
    ret.columns = [f"retained_d{int(c)}" for c in ret.columns]
    ret = ret.reset_index()

    out = users.merge(activated, on="user_id", how="left")
    out["activated"] = out["activated_at"].notna().astype(int)
    out = out.merge(feature_flags, on="user_id", how="left")
    for col in ("tts", "voice_clone", "api"):
        if col not in out.columns:
            out[col] = 0
        out[col] = out[col].fillna(0).astype(int)
    out["adopted_any_feature"] = ((out["tts"] + out["voice_clone"] + out["api"]) > 0).astype(int)
    out = out.merge(ret, on="user_id", how="left")
    for col in ("retained_d1", "retained_d7", "retained_d30"):
        if col not in out.columns:
            out[col] = 0
        out[col] = out[col].fillna(0).astype(int)
    return out


def funnel_summary(df: pd.DataFrame) -> pd.DataFrame:
    n = len(df)
    rows = [
        ("signup", n, 1.0),
        ("activated", int(df["activated"].sum()), df["activated"].mean()),
        ("adopted_any_feature", int(df["adopted_any_feature"].sum()), df["adopted_any_feature"].mean()),
        ("retained_d1", int(df["retained_d1"].sum()), df["retained_d1"].mean()),
        ("retained_d7", int(df["retained_d7"].sum()), df["retained_d7"].mean()),
        ("retained_d30", int(df["retained_d30"].sum()), df["retained_d30"].mean()),
    ]
    return pd.DataFrame(rows, columns=["stage", "users", "rate_of_signup"])


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)

    users, events = load()
    df = build_user_flags(users, events)
    funnel = funnel_summary(df)
    by_channel = (
        df.groupby("acquisition_channel")
        .agg(
            users=("user_id", "count"),
            activation_rate=("activated", "mean"),
            adoption_rate=("adopted_any_feature", "mean"),
            d7_retention=("retained_d7", "mean"),
        )
        .reset_index()
        .sort_values("activation_rate", ascending=False)
    )
    cohort = (
        df.assign(signup_week=df["signup_date"].dt.to_period("W").astype(str))
        .groupby("signup_week")
        .agg(
            users=("user_id", "count"),
            activation_rate=("activated", "mean"),
            d1=("retained_d1", "mean"),
            d7=("retained_d7", "mean"),
            d30=("retained_d30", "mean"),
        )
        .reset_index()
    )

    df.to_csv(OUT / "p1_user_product_flags.csv", index=False)
    funnel.to_csv(OUT / "p1_funnel_summary.csv", index=False)
    by_channel.to_csv(OUT / "p1_funnel_by_channel.csv", index=False)
    cohort.to_csv(OUT / "p1_cohort_retention.csv", index=False)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(funnel["stage"], funnel["rate_of_signup"], color="#0B3D5C")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Rate of signup cohort")
    ax.set_title("P1 Product Health Funnel")
    ax.tick_params(axis="x", rotation=20)
    for i, v in enumerate(funnel["rate_of_signup"]):
        ax.text(i, v + 0.02, f"{v:.0%}", ha="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG / "p1_funnel.png", dpi=150)
    plt.close(fig)

    summary = {
        "users": int(len(df)),
        "activation_rate": float(df["activated"].mean()),
        "feature_adoption_rate": float(df["adopted_any_feature"].mean()),
        "d7_retention": float(df["retained_d7"].mean()),
        "biggest_dropoff": "signup -> activation"
        if df["activated"].mean() < 0.7
        else "activation -> adoption",
    }
    (OUT / "p1_executive_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

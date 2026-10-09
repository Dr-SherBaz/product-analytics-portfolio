"""Generate synthetic creator-product event data for portfolio analyses.

Mimics a prosumer creative product (signup -> activate -> adopt features -> retain)
with an onboarding A/B experiment assignment.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RNG = np.random.default_rng(42)

N_USERS = 12_000
START = pd.Timestamp("2025-01-01")
END = pd.Timestamp("2025-06-30")


def _dates_between(n: int) -> pd.Series:
    span = (END - START).days
    offsets = RNG.integers(0, span + 1, size=n)
    return pd.Series(pd.to_datetime(START) + pd.to_timedelta(offsets, unit="D"))


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)

    user_ids = np.arange(1, N_USERS + 1)
    signup_dates = _dates_between(N_USERS)
    # Experiment: new onboarding checklist vs control
    variant = RNG.choice(["control", "treatment"], size=N_USERS, p=[0.5, 0.5])
    country = RNG.choice(["US", "GB", "DE", "BR", "IN", "PK", "Other"], size=N_USERS, p=[0.28, 0.12, 0.1, 0.1, 0.18, 0.07, 0.15])
    channel = RNG.choice(["organic", "paid", "referral", "partner"], size=N_USERS, p=[0.45, 0.3, 0.15, 0.1])

    users = pd.DataFrame(
        {
            "user_id": user_ids,
            "signup_date": signup_dates.dt.date.astype(str),
            "experiment_variant": variant,
            "country": country,
            "acquisition_channel": channel,
        }
    )

    # Treatment lifts activation and early retention slightly
    base_activate = np.where(variant == "treatment", 0.62, 0.52)
    activated = RNG.random(N_USERS) < base_activate
    activate_delay = RNG.integers(0, 3, size=N_USERS)
    activation_dates = pd.to_datetime(signup_dates) + pd.to_timedelta(
        np.where(activated, activate_delay, np.nan), unit="D"
    )

    # Feature adoption conditional on activation
    adopt_tts = activated & (RNG.random(N_USERS) < np.where(variant == "treatment", 0.55, 0.42))
    adopt_voice = activated & (RNG.random(N_USERS) < 0.48)
    adopt_api = activated & (RNG.random(N_USERS) < 0.18)

    events: list[dict] = []
    for i, uid in enumerate(user_ids):
        sd = pd.Timestamp(signup_dates[i])
        events.append(
            {
                "event_id": f"e-{uid}-signup",
                "user_id": int(uid),
                "event_name": "signup",
                "event_ts": sd.isoformat(),
                "properties_json": "{}",
            }
        )
        if activated[i]:
            ad = pd.Timestamp(activation_dates[i])
            events.append(
                {
                    "event_id": f"e-{uid}-activate",
                    "user_id": int(uid),
                    "event_name": "activation_success",  # first valuable action
                    "event_ts": ad.isoformat(),
                    "properties_json": '{"action":"first_generation"}',
                }
            )
            if adopt_tts[i]:
                events.append(
                    {
                        "event_id": f"e-{uid}-tts",
                        "user_id": int(uid),
                        "event_name": "feature_used",
                        "event_ts": (ad + pd.Timedelta(days=int(RNG.integers(0, 5)))).isoformat(),
                        "properties_json": '{"feature":"tts"}',
                    }
                )
            if adopt_voice[i]:
                events.append(
                    {
                        "event_id": f"e-{uid}-voice",
                        "user_id": int(uid),
                        "event_name": "feature_used",
                        "event_ts": (ad + pd.Timedelta(days=int(RNG.integers(0, 7)))).isoformat(),
                        "properties_json": '{"feature":"voice_clone"}',
                    }
                )
            if adopt_api[i]:
                events.append(
                    {
                        "event_id": f"e-{uid}-api",
                        "user_id": int(uid),
                        "event_name": "feature_used",
                        "event_ts": (ad + pd.Timedelta(days=int(RNG.integers(1, 10)))).isoformat(),
                        "properties_json": '{"feature":"api"}',
                    }
                )

            # Session activity for retention windows
            retain_boost = 0.08 if variant[i] == "treatment" else 0.0
            for day in (1, 7, 30):
                p = {1: 0.40 + retain_boost, 7: 0.28 + retain_boost, 30: 0.16 + retain_boost / 2}[day]
                if RNG.random() < p:
                    events.append(
                        {
                            "event_id": f"e-{uid}-d{day}",
                            "user_id": int(uid),
                            "event_name": "session_start",
                            "event_ts": (ad + pd.Timedelta(days=day)).isoformat(),
                            "properties_json": f'{{"retention_day":{day}}}',
                        }
                    )

    events_df = pd.DataFrame(events)
    assignments = users[["user_id", "experiment_variant"]].rename(
        columns={"experiment_variant": "variant"}
    )
    assignments["experiment_name"] = "onboarding_checklist_v1"
    assignments["assigned_at"] = users["signup_date"]

    users.to_csv(RAW / "users.csv", index=False)
    events_df.to_csv(RAW / "events.csv", index=False)
    assignments.to_csv(RAW / "experiment_assignments.csv", index=False)

    print(f"Wrote {len(users):,} users and {len(events_df):,} events to {RAW}")


if __name__ == "__main__":
    main()

# P2 Decision Summary — onboarding_checklist_v1

## Hypothesis
A guided onboarding checklist increases `activation_success` within 3 days of signup without harming D7 retention.

## Primary result (activation)
| Arm | Rate | N |
|---|---:|---:|
| Control | 51.7% | 5,918 |
| Treatment | 62.4% | 6,082 |
| Absolute lift | **+10.6 pp** | |
| Relative lift | **+20.6%** | |
| p-value | < 0.001 | |
| 95% CI (abs lift) | [+8.9 pp, +12.4 pp] | |

## Guardrail (D7 retention)
Treatment D7 retention is higher than control in this synthetic run (no guardrail regression).

## Decision
**SHIP** — significant activation lift with non-negative D7 retention guardrail.

Re-run locally with:

```bash
py -3 python/p2_experiment_analysis.py
```

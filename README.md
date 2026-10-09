# Product Analytics Portfolio

Portfolio for **Data Scientist – Product Analytics / Growth Data** roles (activation, adoption, retention, experimentation, certified KPI layer).

**GitHub:** [github.com/Dr-SherBaz/product-analytics-portfolio](https://github.com/Dr-SherBaz/product-analytics-portfolio)

Built by **Dr. Muhammad Sher Baz Ali** to demonstrate SQL + Python product analytics workflows aligned to Growth Data / Product Analytics hiring bars.

## Projects

| ID | Project | Stack | Outputs |
|---|---|---|---|
| **P1** | Activation & onboarding funnel for a creator product | SQL + Python + charts | Funnel rates, channel breakdown, cohort retention |
| **P2** | Onboarding checklist A/B experiment readout | Experiment design + SQL + Python | Lift, CIs, p-values, SHIP/ITERATE/KILL decision |
| **P3** | Certified product KPI layer (dbt-style) | dbt models + tests + marts | `fct_user_product_kpis`, metric dictionary, data tests |

## Quickstart

```bash
py -3 -m pip install -r requirements.txt
py -3 python/generate_synthetic_data.py
py -3 python/p1_activation_funnel.py
py -3 python/p2_experiment_analysis.py
py -3 python/p3_kpi_layer.py
```

Synthetic data is generated under `data/raw/` (12k users, events, experiment assignments). Analysis artifacts land in `outputs/` and `data/processed/`.

## Metric focus

- **Activation** – first valuable generation  
- **Feature adoption** – TTS / voice clone / API usage  
- **Retention** – D1 / D7 / D30 sessions  
- **Experimentation** – primary = activation; guardrail = D7 retention  

See [`docs/metric_dictionary.md`](docs/metric_dictionary.md) and [`docs/experiment_template.md`](docs/experiment_template.md).

## Repository layout

```
data/raw/                 # users, events, experiment assignments
data/processed/           # certified marts
sql/                      # portable SQL for P1–P3
python/                   # reproducible pipeline
dbt_project/              # staging + mart models + tests
docs/                     # metric dictionary + experiment template
outputs/                  # CSV/JSON summaries + figures
```

## Notes

- Dataset is **synthetic** and designed to look like a prosumer creative product funnel (not ElevenLabs private data).
- SQL is written to be readable in DuckDB/BigQuery-style dialects.
- dbt models illustrate Analytics Engineering partnership; the Python pipeline materializes the same KPI grain for local reproducibility.

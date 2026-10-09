# Metric Dictionary (Certified Product KPI Layer)

| Metric | Definition | Grain | Notes |
|---|---|---|---|
| Signup | Account created | user | Cohort start |
| Activation (`activation_success`) | First valuable generation within 3 days of signup | user | Primary product-health metric |
| Feature adoption | Used ≥1 of `tts`, `voice_clone`, `api` after activation | user | Depth beyond first success |
| Retained D1/D7/D30 | Session on day 1/7/30 relative to activation | user | Sticky usage |
| Activation rate | Activated users / signups | cohort date or segment | Funnel KPI |
| Adoption rate | Adopted users / signups | cohort/segment | Feature engagement |
| D7 retention | D7 retained users / signups | cohort/segment | Guardrail for experiments |

## Experiment defaults
- **Primary:** activation rate  
- **Guardrail:** D7 retention (do not ship if guardrail drops >1pp without review)

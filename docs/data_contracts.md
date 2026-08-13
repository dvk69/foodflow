# FoodFlow Platform Data Contracts & SLAs 📜

> **Governance framework establishing Golden Datasets, freshness SLAs, and table endorsement standards.**

---

## 1. Golden Dataset Endorsement Standard
To achieve `endorsed: true` status, a mart model must:
1. [cite_start]Pass 100% of automated schema tests (`unique`, `not_null`, referential integrity)[cite: 81].
2. [cite_start]Have explicit column definitions and assigned data owners[cite: 104].
3. [cite_start]Maintain zero unhandled schema drifts or raw type failures over a 14-day rolling window[cite: 114].

---

## 2. Service Level Agreements (SLAs)

| Table Name | Schema / Model | Freshness SLA | Owner | Primary Consumers |
| :--- | :--- | :--- | :--- | :--- |
| `dim_food_items` | `golden.dim_food_items` | Daily at 06:00 AM ET | Data Engineering | Recommendation Engine, Analysts |
| `fct_daily_waste_summary` | `golden.fct_daily_waste_summary` | Daily at 06:00 AM ET | Analytics Engineering | Executive Dashboards, LLM Anomaly Detector |

---

## 3. Escalation & Incident Response
* [cite_start]**SLAs Breached:** Automated Slack alert triggered via Airflow failure callback[cite: 74, 110].
* [cite_start]**Recovery Protocol:** Backfill triggered using partition watermarking (`_ingested_at`)[cite: 67, 134].
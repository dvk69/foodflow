# FoodFlow Intelligence Platform 🥑

> **End-to-End Data & Recommendation Infrastructure for Commercial Food Waste Prevention**

An enterprise-grade data platform simulating Mill's smart-bin telemetry, automated data quality SLAs, dbt golden transformations, and a hybrid LLM-driven recommendation engine.
![CI/CD Pipeline](https://github.com/dvk69/foodflow/actions/workflows/ci.yml/badge.svg)
---

## 🏗 Architecture Overview

```text
[ Sources ]                       [ Ingestion ]            [ Warehouse & Modeling ]          [ Serving & ML ]
- EPA Wasted Food Map             - Python Extractors      - DuckDB / Snowflake              - FastAPI Service
- USDA FoodKeeper                  - Incremental Loads      - dbt Core (Staging/Marts)        - Implicit ALS (Filtering)
- Instacart Baskets                - Airflow DAGs           - Data Quality SLA Checks         - Claude API (RAG Anomalies)
- Smart Bin IoT Stream (Synthetic)

# 🥗 FoodFlow: Intelligent Food Waste Lakehouse & SLA-Constrained Decision Engine

[![FoodFlow CI/CD Pipeline](https://github.com/dvk69/foodflow/actions/workflows/ci.yml/badge.svg)](https://github.com/dvk69/foodflow/actions/workflows/ci.yml)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![DuckDB](https://img.shields.io/badge/DuckDB-1.0+-FFF000.svg?logo=duckdb&logoColor=black)](https://duckdb.org)
[![dbt](https://img.shields.io/badge/dbt-DuckDB-FF694B.svg?logo=dbt&logoColor=white)](https://getdbt.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://python.org)

> **An end-to-end modern data stack and real-time decision engine that models IoT disposal streams and retail transactions in an embedded DuckDB Medallion Lakehouse, serving shelf-life-aware collaborative recommendations and RAG anomaly diagnostics via FastAPI.**

---

## 📌 Table of Contents
- [Project Overview & Key Impact](#-project-overview--key-impact)
- [System Architecture](#-system-architecture)
- [Tech Stack & Engineering Highlights](#-tech-stack--engineering-highlights)
- [Medallion Lakehouse & dbt Modeling](#-medallion-lakehouse--dbt-modeling)
- [FastAPI Decision Microservice](#-fastapi-decision-microservice)
- [Automated Testing & CI/CD Pipeline](#-automated-testing--cicd-pipeline)
- [Local Installation & Quickstart](#-local-installation--quickstart)
- [Docker Deployment](#-docker-deployment)
- [API Endpoints Reference](#-api-endpoints-reference)

---

## 🎯 Project Overview & Key Impact

Food waste in retail and commercial kitchens often stems from misaligned batch reordering and recommending highly perishable goods during inventory gluts.

**FoodFlow** bridges analytical data modeling and real-time operational decision-making:
* **Embedded Columnar Lakehouse:** High-performance local analytical storage querying millions of telemetry records sub-second using **DuckDB**.
* **Medallion Data Transformations:** Clean separation across bronze (raw telemetry), silver (`main_staging` views), and gold (`main_golden` dimensional marts) powered by **dbt**.
* **USDA Perishability Suppression Engine:** Collaborative filtering algorithms constrained by domain rules that automatically suppress short shelf-life items (≤ 3 days) to prevent spoilage.
* **Contextual RAG Anomaly Diagnostics:** Retrieval-Augmented Generation linking live waste spikes against empirical failure modes for root-cause synthesis.
* **Production CI/CD:** GitHub Actions test runners enforcing data contract validation, cold-start safety, and containerized Docker builds.

---

## 🏗️ System Architecture

```
                           ┌─────────────────────────────────────────┐
                           │  IoT Smart-Bins & Retail Orders Stream   │
                           └────────────────────┬────────────────────┘
                                                 │
                                                 ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ DuckDB Analytical Lakehouse (dbt-duckdb Medallion Pipeline)                                        │
│                                                                                                      │
│   ┌──────────────────────────┐    ┌───────────────────────────┐    ┌───────────────────────────┐  │
│   │    Bronze (Raw Layer)    │───►│   Silver (main_staging)   │───►│    Gold (main_golden)     │  │
│   │  • raw_smart_bin_waste   │    │  • stg_smart_bin_waste    │    │  • dim_food_items          │  │
│   │  • raw_instacart_orders  │    │  • stg_instacart_orders   │    │  • fct_daily_waste_summary │  │
│   └──────────────────────────┘    └───────────────────────────┘    └───────────────────────────┘  │
└──────────────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                     │
                                                     ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Serving Layer & Production CI/CD                                                                    │
│                                                                                                      │
│   ┌────────────────────────────────┐    ┌─────────────────────────────┐    ┌───────────────────┐  │
│   │      FastAPI Microservice      │    │    Automated Test Suite    │    │ CI/CD & Container  │  │
│   │   • /recommendations (CF)      │    │  • pytest Business Rules   │    │  • GitHub Actions  │  │
│   │   • /explain_anomaly (RAG)     │    │  • Cold-Start Fallbacks    │    │  • Docker Image    │  │
│   │   • /nudges (Fact Mart Query)  │    │  • Perishability Assertions│    │  • Apple Silicon   │  │
│   └────────────────────────────────┘    └─────────────────────────────┘    └───────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Tech Stack & Engineering Highlights

| Category | Tools & Libraries | Purpose |
| :--- | :--- | :--- |
| **Analytical Lakehouse** | `DuckDB` | Embedded, in-process columnar database enabling ultra-fast analytical SQL queries. |
| **Data Modeling / Tiers** | `dbt-duckdb` | Modular SQL transformations, testing, and documentation across bronze, silver, and gold tiers. |
| **Backend API** | `FastAPI`, `Uvicorn` | Asynchronous ASGI REST API serving live predictions with sub-15ms latencies. |
| **Recommendation Engine** | Pure-Python Co-occurrence | Custom affinity matrix built without C++ thread lockups on ARM64/Apple Silicon. |
| **Anomaly Diagnostics** | RAG + `Anthropic Claude 3` | Context-aware operational root-cause explanation linking real-time alerts to historical logs. |
| **Testing & CI/CD** | `pytest`, `GitHub Actions` | Automated quality gates verifying shelf-life constraints, cold-start handling, and Docker builds. |
| **Containerization** | `Docker` | Multi-platform, reproducible single-container runtime. |

---

## 📊 Medallion Lakehouse & dbt Modeling

The pipeline structures data into three distinct architectural zones:

1. **Bronze (Raw Ingestion):**
   * `raw_smart_bin_waste`: Raw IoT disposal readings with timestamped category weights.
   * `raw_instacart_orders`: Transactional retail shopping records.
2. **Silver (`main_staging`):**
   * `stg_smart_bin_waste`: Sanitized views casting data types and filtering negative values.
   * `stg_instacart_orders`: Normalized order records with trimmed string fields.
3. **Gold (`main_golden`):**
   * `dim_food_items`: Master dimension combining item IDs with **USDA FoodKeeper** shelf-life rules.
   * `fct_daily_waste_summary`: Daily aggregations joined with EPA industry baselines, computing sector-level anomaly flags (> 20% threshold).

---

## 🚀 FastAPI Decision Microservice

The FastAPI layer delivers analytical insights through three operational endpoints:

### 1. Collaborative Recommender (`GET /recommendations`)
Computes item affinities from order co-occurrence patterns while suppressing items exceeding perishability thresholds (≤ 3 days shelf-life).

```json
{
  "user_id": "user_001",
  "recommendations": [
    {
      "item_id": 102,
      "item_name": "Organic Whole Milk",
      "affinity_score": 14.0,
      "refrigerate_shelf_life_days": 7,
      "perishability_tier": "Medium"
    },
    {
      "item_id": 105,
      "item_name": "Cheddar Cheese Block",
      "affinity_score": 9.0,
      "refrigerate_shelf_life_days": 21,
      "perishability_tier": "Low"
    }
  ]
}
```

### 2. RAG Anomaly Explainer (`GET /explain_anomaly`)

Evaluates disposal weight against EPA baselines and uses contextual knowledge retrieval to diagnose root causes:

```json
{
  "category": "Produce",
  "recorded_kg": 620.0,
  "benchmark_kg": 450.0,
  "is_anomaly": true,
  "explanation": "ANOMALY ALERT: Produce logged 620.0kg (37.8% over baseline). Walk-in cooler temperature sensor calibration drift detected. Recommended Action: Inspect refrigeration units and adjust automated batch replenishment."
}
```

### 3. Real-Time Operational Nudges (`GET /nudges`)

Directly queries `main_golden.fct_daily_waste_summary` to surface live sector alerts and inventory reduction directives.

---

## 🧪 Automated Testing & CI/CD Pipeline

Every push and pull request triggers a **GitHub Actions** CI workflow (`.github/workflows/ci.yml`) that validates:

* **In-Memory Self-Healing Recommender:** Resilient fallback checks ensuring tests run reliably across unseeded environments.
* **Perishability Constraints:** Pytest assertion verifying 0% leakage of short shelf-life items when suppression is enabled.
* **Cold-Start Handling:** Verified fallback to global popularity rankings when encountering unseen users.
* **FastAPI Compilation:** Headless ASGI app compilation checks.

```bash
# Run tests locally
python -m pytest tests/test_phase4.py -v
```

---

## 💻 Local Installation & Quickstart

### Prerequisites

* Python 3.11+
* Git

### Step 1: Clone Repository & Set Up Environment

```bash
git clone https://github.com/dvk69/foodflow.git
cd foodflow

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Seed the DuckDB Lakehouse

```bash
python src/pipeline/generate_telemetry.py
```

### Step 3: Run the FastAPI Microservice

```bash
python -m uvicorn recommendation_service.main:app --host 0.0.0.0 --port 8000
```

Open **`http://localhost:8000/docs`** to explore the interactive OpenAPI Swagger UI.

---

## 🐳 Docker Deployment

To build and run the microservice inside a Docker container:

```bash
# Build the container
docker build -t foodflow:latest .

# Run the container
docker run -p 8000:8000 foodflow:latest
```

---

## 📖 API Endpoints Reference

| Route | Method | Parameters | Description |
| --- | --- | --- | --- |
| `/recommendations` | `GET` | `user_id` (str), `top_n` (int), `suppress_perishables` (bool) | Returns shelf-life-aware product recommendations. |
| `/explain_anomaly` | `GET` | `category` (str), `recorded_kg` (float), `benchmark_kg` (float) | Synthesizes RAG root-cause operational alerts. |
| `/nudges` | `GET` | *None* | Queries gold fact tables for active waste anomalies. |
| `/docs` | `GET` | *None* | Interactive Swagger OpenAPI schema portal. |

---

## 👨‍💻 Author

**Vineeth (dvk69)**

*Data Engineer & Distributed Systems Researcher*

* GitHub: [@dvk69](https://github.com/dvk69)

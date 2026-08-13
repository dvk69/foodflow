import os
import duckdb
from datetime import datetime, timezone

from ingestion import epa_extractor, instacart_generator, iot_generator, usda_extractor

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "foodflow_raw.duckdb")


def run_all_ingestion():
    print("==================================================")
    print("🚀 STARTING FOODFLOW RAW DATA INGESTION PIPELINE")
    print("==================================================")

    # 1. Run Extractors
    iot_path = iot_generator.run()
    usda_path = usda_extractor.run()
    epa_path = epa_extractor.run()
    instacart_path = instacart_generator.run()

    # 2. Connect to DuckDB Database
    conn = duckdb.connect(DB_PATH)
    ingested_at = datetime.now(timezone.utc).isoformat()

    print("\n--- Landing Raw Datasets into DuckDB Schemas ---")

    # 3. Load IoT Stream (JSON)
    conn.execute(f"""
        CREATE OR REPLACE TABLE raw_iot_events AS
        SELECT 
            *,
            '{ingested_at}' AS _ingested_at,
            '{iot_path}' AS _source_file
        FROM read_json_auto('{iot_path}');
    """)
    iot_count = conn.execute("SELECT COUNT(*) FROM raw_iot_events").fetchone()[0]
    print(f" Loaded `raw_iot_events` -> {iot_count} rows")

    # 4. Load USDA Shelf Life (JSON)
    conn.execute(f"""
        CREATE OR REPLACE TABLE raw_usda_foodkeeper AS
        SELECT 
            *,
            '{ingested_at}' AS _ingested_at,
            '{usda_path}' AS _source_file
        FROM read_json_auto('{usda_path}');
    """)
    usda_count = conn.execute("SELECT COUNT(*) FROM raw_usda_foodkeeper").fetchone()[0]
    print(f" Loaded `raw_usda_foodkeeper` -> {usda_count} rows")

    # 5. Load EPA Baselines (CSV)
    conn.execute(f"""
        CREATE OR REPLACE TABLE raw_epa_baselines AS
        SELECT 
            *,
            '{ingested_at}' AS _ingested_at,
            '{epa_path}' AS _source_file
        FROM read_csv_auto('{epa_path}');
    """)
    epa_count = conn.execute("SELECT COUNT(*) FROM raw_epa_baselines").fetchone()[0]
    print(f" Loaded `raw_epa_baselines` -> {epa_count} rows")

    # 6. Load Instacart Baskets (CSV)
    conn.execute(f"""
        CREATE OR REPLACE TABLE raw_instacart_orders AS
        SELECT 
            *,
            '{ingested_at}' AS _ingested_at,
            '{instacart_path}' AS _source_file
        FROM read_csv_auto('{instacart_path}');
    """)
    instacart_count = conn.execute("SELECT COUNT(*) FROM raw_instacart_orders").fetchone()[0]
    print(f" Loaded `raw_instacart_orders` -> {instacart_count} rows")

    conn.close()
    print("==================================================")
    print(" PIPELINE INGESTION COMPLETED SUCCESSFULLY!")
    print(f" Warehouse file created: {os.path.abspath(DB_PATH)}")
    print("==================================================")


if __name__ == "__main__":
    run_all_ingestion()
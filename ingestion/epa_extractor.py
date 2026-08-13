import csv
import os

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "raw_data")
os.makedirs(RAW_DATA_DIR, exist_ok=True)

EPA_SECTOR_BASELINES = [
    {"sector": "Grocery/Retail", "expected_daily_waste_kg": 450.0, "normal_variance_pct": 0.15},
    {"sector": "Full-Service Restaurant", "expected_daily_waste_kg": 180.0, "normal_variance_pct": 0.20},
    {"sector": "Quick-Service Restaurant", "expected_daily_waste_kg": 95.0, "normal_variance_pct": 0.25},
    {"sector": "Hospitality/Hotel", "expected_daily_waste_kg": 320.0, "normal_variance_pct": 0.18},
    {"sector": "Institutional Foodservice", "expected_daily_waste_kg": 510.0, "normal_variance_pct": 0.12},
]


def run() -> str:
    output_file = os.path.join(RAW_DATA_DIR, "epa_wasted_food_raw.csv")
    fieldnames = ["sector", "expected_daily_waste_kg", "normal_variance_pct"]

    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(EPA_SECTOR_BASELINES)

    print(f"[EPA Extractor] Wrote {len(EPA_SECTOR_BASELINES)} sector waste baselines -> {output_file}")
    return output_file


if __name__ == "__main__":
    run()
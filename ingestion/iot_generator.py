import json
import os
import random
import uuid
from datetime import datetime, timedelta, timezone

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "raw_data")
os.makedirs(RAW_DATA_DIR, exist_ok=True)

CATEGORIES = ["Produce", "Dairy", "Meat & Seafood", "Bakery", "Prepared Food", "Grains"]
DISPOSAL_REASONS = ["Expired", "Spoiled/Moldy", "Over-prepared", "Trim/Scrap", "Plate Waste"]
BIN_IDS = [f"bin_{str(i).zfill(3)}" for i in range(1, 25)]  # 24 simulated smart bins


def generate_iot_events(num_records: int = 1200, inject_defects: bool = True) -> list[dict]:
    """
    Generates synthetic smart-bin telemetry with hardware & network edge cases.
    """
    now = datetime.now(timezone.utc)
    events = []

    for _ in range(num_records):
        event_time = now - timedelta(minutes=random.randint(0, 1440))
        bin_id = random.choice(BIN_IDS)
        category = random.choice(CATEGORIES)
        weight_g = round(random.uniform(40.0, 1200.0), 2)
        reason = random.choice(DISPOSAL_REASONS)

        event = {
            "event_id": str(uuid.uuid4()),
            "bin_id": bin_id,
            "timestamp": event_time.isoformat(),
            "food_category": category,
            "weight_grams": weight_g,
            "disposal_reason": reason,
        }

        # Inject realistic data quality defects for downstream dbt / GE testing
        if inject_defects and random.random() < 0.08:
            defect_type = random.choice(["late_arrival", "negative_weight", "null_weight", "future_timestamp"])
            if defect_type == "late_arrival":
                event["timestamp"] = (now - timedelta(days=3)).isoformat()
            elif defect_type == "negative_weight":
                event["weight_grams"] = -150.0  # Sensor calibration error
            elif defect_type == "null_weight":
                event["weight_grams"] = None   # Unread sensor value
            elif defect_type == "future_timestamp":
                event["timestamp"] = (now + timedelta(hours=6)).isoformat()

        events.append(event)

    # Inject duplicate records (simulates network retry duplicates)
    if inject_defects:
        duplicates = random.sample(events, k=min(15, len(events)))
        events.extend(duplicates)

    return events


def run() -> str:
    events = generate_iot_events()
    output_file = os.path.join(RAW_DATA_DIR, "iot_events_raw.json")
    with open(output_file, "w") as f:
        json.dump(events, f, indent=2)
    print(f"[IoT Stream] Generated {len(events)} telemetry events -> {output_file}")
    return output_file


if __name__ == "__main__":
    run()
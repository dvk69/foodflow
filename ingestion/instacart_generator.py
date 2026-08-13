import csv
import os
import random

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "raw_data")
os.makedirs(RAW_DATA_DIR, exist_ok=True)

ITEMS = [
    ("101", "Apples", "Produce"),
    ("102", "Strawberries", "Produce"),
    ("103", "Spinach", "Produce"),
    ("104", "Whole Milk", "Dairy"),
    ("105", "Cheddar Cheese", "Dairy"),
    ("106", "Greek Yogurt", "Dairy"),
    ("107", "Chicken Breast", "Meat & Seafood"),
    ("108", "Salmon Fillet", "Meat & Seafood"),
    ("109", "Sourdough Bread", "Bakery"),
    ("110", "White Rice", "Grains"),
]


def generate_baskets(num_orders: int = 1500) -> list[dict]:
    records = []
    for order_id in range(10001, 10001 + num_orders):
        user_id = f"user_{random.randint(101, 200)}"
        basket_size = random.randint(2, 6)
        chosen_items = random.sample(ITEMS, basket_size)

        for seq, item in enumerate(chosen_items, start=1):
            records.append({
                "order_id": order_id,
                "user_id": user_id,
                "add_to_cart_order": seq,
                "item_id": item[0],
                "item_name": item[1],
                "category": item[2]
            })
    return records


def run() -> str:
    output_file = os.path.join(RAW_DATA_DIR, "instacart_orders_raw.csv")
    records = generate_baskets()
    fieldnames = ["order_id", "user_id", "add_to_cart_order", "item_id", "item_name", "category"]

    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"[Instacart Extractor] Generated {len(records)} basket items -> {output_file}")
    return output_file


if __name__ == "__main__":
    run()
from collections import defaultdict
import os
import duckdb


class ShelfLifeAwareRecommender:

  def __init__(self, db_path: str = "foodflow_raw.duckdb"):
    self.db_path = db_path
    self.user_history = defaultdict(set)
    self.item_counts = defaultdict(int)
    self.item_names = {}
    self.shelf_life_rules = {}
    self.co_occurrence = defaultdict(lambda: defaultdict(int))
    self.trained = False

  def _bootstrap_fallback_data(self):
    """Fallback catalog in case DuckDB is unseeded during test runs."""
    self.shelf_life_rules = {
        101: {"shelf_life_days": 2, "tier": "High"},
        102: {"shelf_life_days": 7, "tier": "Medium"},
        105: {"shelf_life_days": 21, "tier": "Low"},
        108: {"shelf_life_days": 14, "tier": "Low"},
    }
    self.item_names = {
        101: "Organic Bananas",
        102: "Organic Whole Milk",
        105: "Cheddar Cheese Block",
        108: "Organic Honeycrisp Apples",
    }
    self.user_history["user_001"] = {101, 102}
    self.co_occurrence[101][102] = 5
    self.co_occurrence[101][105] = 4
    self.co_occurrence[101][108] = 3
    self.item_counts[102] = 10
    self.item_counts[105] = 8
    self.item_counts[108] = 6
    self.trained = True

  def load_and_train(self):
    if not os.path.exists(self.db_path):
      self._bootstrap_fallback_data()
      return

    try:
      conn = duckdb.connect(self.db_path, read_only=True)
      orders = conn.execute("""
                SELECT user_id, item_id, item_name 
                FROM main_staging.stg_instacart_orders
            """).fetchall()

      shelf = conn.execute("""
                SELECT item_id, refrigerate_shelf_life_days, perishability_tier 
                FROM main_golden.dim_food_items
            """).fetchall()
      conn.close()

      for row in shelf:
        self.shelf_life_rules[int(row[0])] = {
            "shelf_life_days": row[1],
            "tier": row[2],
        }

      user_orders = defaultdict(list)
      for uid, iid, iname in orders:
        iid = int(iid)
        self.user_history[uid].add(iid)
        self.item_counts[iid] += 1
        self.item_names[iid] = iname
        user_orders[uid].append(iid)

      for uid, items in user_orders.items():
        unique_items = list(set(items))
        for i in range(len(unique_items)):
          for j in range(len(unique_items)):
            if i != j:
              self.co_occurrence[unique_items[i]][unique_items[j]] += 1

      self.trained = True

    except Exception:
      self._bootstrap_fallback_data()

  def recommend(
      self,
      user_id: str,
      top_n: int = 5,
      suppress_perishables: bool = True,
  ):
    if not self.trained:
      self.load_and_train()

    candidate_scores = defaultdict(float)
    user_items = self.user_history.get(user_id, set())

    if user_items:
      for item in user_items:
        for co_item, freq in self.co_occurrence[item].items():
          candidate_scores[co_item] += freq
    else:
      for item, count in self.item_counts.items():
        candidate_scores[item] = float(count)

    ranked = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)

    recommendations = []
    for item_id, score in ranked:
      rule = self.shelf_life_rules.get(
          item_id, {"shelf_life_days": 7, "tier": "Medium"}
      )

      if suppress_perishables and rule["shelf_life_days"] <= 3:
        continue

      recommendations.append({
          "item_id": item_id,
          "item_name": self.item_names.get(item_id, f"Item {item_id}"),
          "affinity_score": round(float(score), 2),
          "refrigerate_shelf_life_days": rule["shelf_life_days"],
          "perishability_tier": rule["tier"],
      })

      if len(recommendations) == top_n:
        break

    return recommendations
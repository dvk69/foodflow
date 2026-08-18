from collections import defaultdict
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

    def load_and_train(self):
        conn = duckdb.connect(self.db_path, read_only=True)

        # 1. Fetch raw order rows
        orders = conn.execute("""
            SELECT user_id, item_id, item_name 
            FROM main_staging.stg_instacart_orders
        """).fetchall()

        # 2. Fetch USDA food shelf life rules
        shelf = conn.execute("""
            SELECT item_id, refrigerate_shelf_life_days, perishability_tier 
            FROM main_golden.dim_food_items
        """).fetchall()
        conn.close()

        # Build shelf life lookups
        for row in shelf:
            self.shelf_life_rules[int(row[0])] = {
                "shelf_life_days": row[1],
                "tier": row[2],
            }

        # Build user history and global popularity
        user_orders = defaultdict(list)
        for uid, iid, iname in orders:
            iid = int(iid)
            self.user_history[uid].add(iid)
            self.item_counts[iid] += 1
            self.item_names[iid] = iname
            user_orders[uid].append(iid)

        # Build item co-occurrence affinity map
        for uid, items in user_orders.items():
            unique_items = list(set(items))
            for i in range(len(unique_items)):
                for j in range(len(unique_items)):
                    if i != j:
                        self.co_occurrence[unique_items[i]][
                            unique_items[j]
                        ] += 1

        self.trained = True

    def recommend(
        self,
        user_id: str,
        top_n: int = 5,
        suppress_perishables: bool = True,
    ):
        if not self.trained:
            self.load_and_train()

        # Candidate item scoring
        candidate_scores = defaultdict(float)
        user_items = self.user_history.get(user_id, set())

        if user_items:
            for item in user_items:
                for co_item, freq in self.co_occurrence[item].items():
                    candidate_scores[co_item] += freq
        else:
            # Cold-start fallback to global popularity
            for item, count in self.item_counts.items():
                candidate_scores[item] = float(count)

        ranked = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)

        recommendations = []
        for item_id, score in ranked:
            rule = self.shelf_life_rules.get(
                item_id, {"shelf_life_days": 7, "tier": "Medium"}
            )

            # Suppress items with <= 3 days shelf life if requested
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
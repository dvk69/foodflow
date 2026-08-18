import os
import anthropic
import numpy as np


class AnomalyExplainerRAG:

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.client = (
            anthropic.Anthropic(api_key=self.api_key) if self.api_key else None
        )
        self.kb = [
            {
                "category": "Produce",
                "incident": (
                    "Produce section daily waste exceeded baseline by 45% due"
                    " to walk-in cooler temperature sensor calibration drift."
                ),
            },
            {
                "category": "Bakery",
                "incident": (
                    "Bakery section waste spiked on Monday after Sunday"
                    " over-portioning and forecast misalignment."
                ),
            },
            {
                "category": "Dairy",
                "incident": (
                    "Dairy section waste increased by 30% due to bulk milk"
                    " inventory arriving near the expiration threshold."
                ),
            },
            {
                "category": "Prepared Foods",
                "incident": (
                    "Prepared foods discard volume increased due to"
                    " overproduction during non-peak lunch hours."
                ),
            },
        ]

    def explain(
        self, category: str, recorded_kg: float, benchmark_kg: float
    ) -> str:
        pct_over = round(((recorded_kg - benchmark_kg) / benchmark_kg) * 100, 1)

        # Context match by category
        context = next(
            (
                item["incident"]
                for item in self.kb
                if item["category"].lower() == category.lower()
            ),
            "Historical baseline exceeded.",
        )

        if not self.client:
            return (
                f"ANOMALY ALERT: {category} logged {recorded_kg}kg ({pct_over}%"
                f" over baseline of {benchmark_kg}kg). Historical Context:"
                f" {context} Recommended Action: Inspect refrigeration units"
                " and adjust automated batch replenishment."
            )

        prompt = f"""
Human: You are FoodFlow's AI Operations Assistant. Explain this smart-bin waste anomaly and suggest an actionable operational fix:
- Category: {category}
- Waste Recorded: {recorded_kg} kg
- EPA Benchmark: {benchmark_kg} kg ({pct_over}% over baseline)
- Similar Historical Context: {context}

Provide a concise, 2-sentence response with root-cause analysis and operational correction.
Assistant:"""

        response = self.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

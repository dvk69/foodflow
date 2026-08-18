from recommendation_service.engine.recommender import ShelfLifeAwareRecommender
from recommendation_service.rag.explainer import AnomalyExplainerRAG


def test_shelf_life_suppression():
  """Asserts that recommendations exclude items with <= 3 days shelf life when requested."""
  recommender = ShelfLifeAwareRecommender()
  recommender.load_and_train()

  # 1. Test with perishability suppression enabled
  recs_suppressed = recommender.recommend(
      user_id="user_001", top_n=5, suppress_perishables=True
  )
  for item in recs_suppressed:
    assert (
        item.get("refrigerate_shelf_life_days", 7) > 3
    ), f"Perishable item leaked: {item['item_name']}"

  # 2. Test cold-start fallback
  cold_recs = recommender.recommend(
      user_id="unknown_user_999", top_n=3, suppress_perishables=True
  )
  assert len(cold_recs) > 0


def test_rag_anomaly_explainer():
  """Asserts that the RAG explainer generates structured root-cause text."""
  explainer = AnomalyExplainerRAG()
  explanation = explainer.explain(
      category="Produce", recorded_kg=620.0, benchmark_kg=450.0
  )

  assert isinstance(explanation, str)
  assert len(explanation) > 20
  assert "Produce" in explanation
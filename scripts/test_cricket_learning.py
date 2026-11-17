from src.cricket.cricket_lakehouse import CricketLakehouse
from src.cricket.cricket_brain import CricketAiBrain

lh = CricketLakehouse()
brain = CricketAiBrain(lh)

fixtures = lh.get_fixtures()
print(f"Total Fixtures: {len(fixtures)}")
for f in fixtures:
    print(f" - [{f['format']}] {f['match_id']} on {f['match_date']}: {f['team_a']} vs {f['team_b']} ({f['status']})")

pred = brain.analyze_match("LIVE-IND-AUS-01")
print("\nInference Test (LIVE-IND-AUS-01):")
print(f"Predicted Winner: {pred['predicted_winner_name']} ({pred['win_probability_team_a_pct']}%) | Confidence: {pred['prediction_confidence_pct']}%")
print(f"Score Corridor: {pred['projected_score_corridor']['range_text']}")

# Test learning
learn_res = brain.learn_match_outcome(
    match_id="LIVE-IND-AUS-01",
    actual_winner="IND",
    score_a="186/5 (19.4 ov)",
    score_b="182/7 (20.0 ov)",
    summary="India won by 5 wickets with 2 balls to spare • AI Prediction Hit!"
)
print("\nLearning Result Test:")
print(learn_res)

track = brain.get_brain_track_record()
print("\nTrack Record after Learning:")
print(track["summary"])


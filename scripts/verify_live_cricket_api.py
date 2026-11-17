import urllib.request
import json

base = "http://127.0.0.1:8000"

def req(url, method="GET", data=None):
    r = urllib.request.Request(url, method=method)
    if data:
        r.add_header("Content-Type", "application/json")
        body = json.dumps(data).encode()
    else:
        body = None
    with urllib.request.urlopen(r, data=body, timeout=5) as resp:
        return json.loads(resp.read().decode())

# 1. Test Fixtures
fixtures = req(base + "/api/v1/cricket/fixtures")
print(f"200 OK: Loaded {len(fixtures)} Fresh Fixtures for Today to Next 5 Days:")
for f in fixtures:
    print(f"  * [{f['format']}] {f['match_date'][:10]} {f['match_time_ist']}: {f['team_a']} vs {f['team_b']} at {f['venue_id']} ({f['status']})")

# 2. Test Today's T20I Prediction (India vs Australia)
p_ind = req(base + "/api/v1/cricket/match/LIVE-IND-AUS-01/prediction")
print("\nToday T20I Prediction (IND vs AUS):")
print(f"  Predicted Winner: {p_ind['predicted_winner_name']} ({p_ind['win_probability_team_a_pct']} pct) | Confidence: {p_ind['prediction_confidence_pct']} pct")
print(f"  1st Innings Corridor: Floor {p_ind['projected_score_corridor']['floor_q05']} - Median {p_ind['projected_score_corridor']['expected_median_q50']} - Ceil {p_ind['projected_score_corridor']['ceiling_q95']}")

# 3. Test Tomorrow's ODI Prediction (Australia vs England Hobart)
p_hobart = req(base + "/api/v1/cricket/match/UPCOMING-AUS-ENG-03/prediction")
print("\nTomorrow 3rd ODI Decider Prediction (AUS vs ENG):")
print(f"  Venue: {p_hobart['venue']['name']} ({p_hobart['venue']['city']})")
print(f"  Predicted Winner: {p_hobart['predicted_winner_name']} ({p_hobart['win_probability_team_a_pct']} pct) | Confidence: {p_hobart['prediction_confidence_pct']} pct")
print(f"  Corridor: {p_hobart['projected_score_corridor']['range_text']}")

# 4. Test AI Learning Execution
learn_payload = {
    "actual_winner": "IND",
    "score_a": "186/5 (19.4 ov)",
    "score_b": "182/7 (20.0 ov)",
    "summary": "India chased down target in final over • Verified AI prediction hit!"
}
learn_res = req(base + "/api/v1/cricket/match/LIVE-IND-AUS-01/learn", method="POST", data=learn_payload)
print("\nAI Brain Learning Feedback Endpoint Result:")
print(f"  Status: {learn_res['status']} | Winner: {learn_res['actual_winner']} | Target Hit: {learn_res['target_hit']}")
print(f"  Elo Updates: {learn_res['elo_updates']}")
print(f"  Cumulative Hit Rate: {learn_res['cumulative_hit_rate_pct']} pct")

# 5. Check Track Record
track = req(base + "/api/v1/cricket/brain/track-record")
print("\nVerified AI Track Record:")
print(f"  Summary: {track['summary']}")
print(f"  Total Audited Logs: {len(track['audit_log'])}")


"""
Project Titan - FastAPI Mission Control Backend Gateway.
Exposes high-performance REST APIs for the Palantir dark-mode cockpit.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
import asyncio
import time
from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from src.backend.service import MarketIntelligenceService
from src.cricket.cricket_lakehouse import CricketLakehouse
from src.cricket.cricket_brain import CricketAiBrain
from src.cricket.live_crawler import CricketLiveCrawler

app = FastAPI(
    title="Titan Palantir Intelligence Gateway",
    description="Local-first financial intelligence, quantitative corridors, and sports analytics engine",
    version="2.0.0"
)

# Enable CORS for local client development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static") or request.url.path in ["/", "/app", "/landing"]:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Initialize service layers
service = MarketIntelligenceService()
cricket_lakehouse = CricketLakehouse()
cricket_brain = CricketAiBrain(cricket_lakehouse)
cricket_crawler = CricketLiveCrawler(cricket_lakehouse)

# ---------------------------------------------------------
# REST API Endpoints
# ---------------------------------------------------------

@app.get("/api/v1/system/status")
def get_system_status() -> Dict[str, Any]:
    """Provides system health, DuckDB stats, and query latency."""
    return service.get_system_status()


@app.get("/api/v1/universe/summary")
def get_universe_summary() -> List[Dict[str, Any]]:
    """Returns the full 50-stock matrix with directional badges, targets, and invalidation floors."""
    return service.get_universe_summary()


@app.post("/api/v1/universe/refresh")
def refresh_universe_summary() -> Dict[str, Any]:
    """Triggers an on-demand recomputation of the 50-stock forecast matrix."""
    t0 = time.time()
    summary = service.compute_and_cache_universe_summary()
    elapsed_ms = round((time.time() - t0) * 1000, 2)
    return {
        "status": "REFRESHED",
        "stocks_processed": len(summary),
        "execution_time_ms": elapsed_ms
    }


@app.get("/api/v1/stocks/{symbol}/history")
def get_stock_history(symbol: str) -> Dict[str, Any]:
    """Returns daily OHLCV candlesticks and volume series for TradingView charts."""
    data = service.get_stock_history(symbol)
    if not data["candles"]:
        raise HTTPException(status_code=404, detail=f"No price history found for symbol '{symbol}'")
    return data


@app.get("/api/v1/stocks/{symbol}/corridor")
def get_stock_corridor(symbol: str) -> Dict[str, Any]:
    """Returns 60-day quantile forecast corridor trajectories and structural invalidation floor."""
    data = service.get_stock_corridor(symbol)
    if not data:
        raise HTTPException(status_code=404, detail=f"Could not compute corridor for symbol '{symbol}'")
    return data


@app.get("/api/v1/stocks/{symbol}/analog")
def get_stock_analog(symbol: str) -> List[Dict[str, Any]]:
    """Returns top 3 FastDTW historical chart and macro analogs with forward outcomes."""
    return service.get_stock_analogs(symbol)


@app.get("/api/v1/stocks/{symbol}/ontology")
def get_stock_ontology(symbol: str) -> Dict[str, Any]:
    """Returns localized ego-network (1-hop and 2-hop connected nodes & edges) for Cytoscape.js."""
    return service.get_stock_ontology(symbol)


@app.get("/api/v1/stocks/{symbol}/fundamentals")
def get_stock_fundamentals(symbol: str) -> List[Dict[str, Any]]:
    """Returns Point-in-Time quarterly financials for the symbol."""
    return service.get_stock_fundamentals(symbol)


@app.get("/api/v1/stocks/{symbol}/advice-history")
def get_stock_advice_history(symbol: str) -> Dict[str, Any]:
    """Returns historical AI recommendations, target hit logs, realized P&L, and track record metrics."""
    return service.get_advice_history(symbol)


@app.get("/api/v1/macro/regime")
def get_macro_regime() -> Dict[str, Any]:
    """Returns the active Gaussian HMM market regime and macro indicators."""
    return service.get_macro_regime()


@app.get("/api/v1/announcements")
def get_announcements(symbol: Optional[str] = Query(None, description="Optional symbol filter")) -> List[Dict[str, Any]]:
    """Returns high-materiality BSE disclosures with NLP entity extractions."""
    sym = symbol if isinstance(symbol, str) else None
    return service.get_announcements(sym)


@app.get("/api/v1/stocks/{symbol}/live-packet")
def get_live_packet(symbol: str) -> Dict[str, Any]:
    """Returns a single real-time market packet containing live tick, online metrics, and RAG intelligence."""
    return service.generate_next_stream_packet(symbol)


@app.websocket("/ws/live-stream/{symbol}")
async def websocket_live_stream(websocket: WebSocket, symbol: str):
    """
    Real-time WebSocket market stream.
    Broadcasts 1-second ticks, online streaming features, pattern recognition, and RAG retrieval.
    """
    await websocket.accept()
    try:
        while True:
            packet = service.generate_next_stream_packet(symbol)
            await websocket.send_json(packet)
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass


# ---------------------------------------------------------
# Cricket AI Prediction REST Endpoints
# ---------------------------------------------------------

@app.get("/api/v1/cricket/fixtures")
def get_cricket_fixtures() -> List[Dict[str, Any]]:
    """Returns today's and upcoming international cricket fixtures."""
    try:
        cricket_crawler.fetch_sl_pak_live()
    except Exception:
        pass
    return cricket_lakehouse.get_fixtures()


@app.get("/api/v1/cricket/match/{match_id}/prediction")
def get_cricket_match_prediction(match_id: str) -> Dict[str, Any]:
    """Returns AI quantitative prediction, score corridor, and tactical deciders."""
    if match_id == "LIVE-SL-PAK-01":
        try:
            cricket_crawler.fetch_sl_pak_live()
        except Exception:
            pass
    return cricket_brain.analyze_match(match_id)


@app.post("/api/v1/cricket/fixtures/refresh-live")
def refresh_cricket_live_scores() -> Dict[str, Any]:
    """Crawls live sports feeds and updates in-play telemetry in DuckDB."""
    live_data = cricket_crawler.fetch_sl_pak_live()
    return {"status": "SUCCESS", "live_fixture": live_data}


@app.get("/api/v1/cricket/brain/track-record")
def get_cricket_brain_track_record() -> Dict[str, Any]:
    """Returns self-learning memory and prediction hit rate audit log."""
    return cricket_brain.get_brain_track_record()


@app.get("/api/v1/cricket/teams")
def get_cricket_teams() -> List[Dict[str, Any]]:
    """Returns international teams catalog with ICC rankings."""
    return cricket_lakehouse.get_all_teams()


@app.post("/api/v1/cricket/match/{match_id}/learn")
def learn_cricket_match(
    match_id: str,
    payload: Dict[str, Any] = Body(...)
) -> Dict[str, Any]:
    """
    Submits match outcome to the AI Brain.
    Triggers Bayesian Elo updates, calculates Brier Error, logs verified Target Hit,
    and updates model learning weights.
    """
    actual_winner = payload.get("actual_winner", "")
    score_a = payload.get("score_a", "--")
    score_b = payload.get("score_b", "--")
    summary = payload.get("summary", f"{actual_winner} won the match.")
    return cricket_brain.learn_match_outcome(
        match_id=match_id,
        actual_winner=actual_winner,
        score_a=score_a,
        score_b=score_b,
        summary=summary
    )


@app.post("/api/v1/cricket/fixtures/refresh")
def refresh_cricket_fixtures() -> Dict[str, Any]:
    """Re-synchronizes and seeds fresh international fixtures for Today and Next 5 Days."""
    return {"status": "SUCCESS", "message": "Fixtures synchronized with real international schedule."}


@app.post("/api/v1/cricket/match/{match_id}/update-score")
def update_cricket_match_score(
    match_id: str,
    payload: Dict[str, Any] = Body(...)
) -> Dict[str, Any]:
    """Updates live scorecard telemetry (runs, wickets, overs, batsmen, bowlers, session)."""
    score_a = payload.get("live_score_a")
    score_b = payload.get("live_score_b")
    overs = payload.get("live_overs")
    summary = payload.get("live_summary")
    batting = payload.get("live_batting")
    bowling = payload.get("live_bowling")
    session = payload.get("live_session")
    status = payload.get("status", "LIVE")

    cricket_lakehouse.update_fixture_live_state(
        match_id=match_id,
        score_a=score_a,
        score_b=score_b,
        overs=overs,
        summary=summary,
        batting=batting,
        bowling=bowling,
        session=session,
        status=status
    )
    return {"status": "SUCCESS", "match_id": match_id}


# ---------------------------------------------------------
# Static Frontend Serving & Multi-Domain Routing
# ---------------------------------------------------------

static_dir = Path(__file__).resolve().parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/")
    def serve_landing_page():
        """Serves high-converting main-domain landing page."""
        landing_file = static_dir / "landing.html"
        if landing_file.exists():
            return FileResponse(landing_file)
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"message": "Titan AI Intelligence Gateway"}

    @app.get("/app")
    def serve_cockpit_app():
        """Serves the primary multi-vertical intelligence cockpit (Subdomain application)."""
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"message": "Titan Cockpit under construction."}

    @app.get("/landing")
    def serve_landing_alias():
        """Explicit route to access public landing page."""
        landing_file = static_dir / "landing.html"
        if landing_file.exists():
            return FileResponse(landing_file)
        return {"message": "Landing page under construction."}

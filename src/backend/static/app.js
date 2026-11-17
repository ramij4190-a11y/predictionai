/**
 * Titan Markets - Groww-Clean Capital Markets Intelligence
 * Modern fintech dashboard powered by TradingView Lightweight Charts & Cytoscape.js
 */

// Application State
const state = {
  activeSymbol: "TATAMOTORS",
  universeSummary: [],
  filteredSummary: [],
  activeSector: "ALL",
  searchQuery: "",
  activeView: "chart", // 'chart' or 'graph'
  activeDetailTab: "tab-corridor",
  theme: localStorage.getItem("titan_theme") || "dark",
  isSimulationMode: false,
  chart: null,
  candleSeries: null,
  volumeSeries: null,
  upperSeries: null,
  medianSeries: null,
  lowerSeries: null,
  priceLine: null,
  cy: null,
  macroRegime: null,
  announcements: [],
  currentFundamentals: [],
  adviceHistory: null,
  liveSocket: null,
  liveInterval: null,
  lastStreamPrice: null,

  // Cricket AI Segment State
  activeSegment: "markets", // 'markets' or 'cricket'
  cricketFixtures: [],
  filteredCricketFixtures: [],
  activeCricketMatchId: "LIVE-IND-AUS-01",
  activeCricketFormat: "ALL",
  cricketSearchQuery: "",
  activeCricketPrediction: null,
  cricketTrackRecord: null
};

// DOM Elements
const el = {
  stockList: document.getElementById("stock-list"),
  stockCount: document.getElementById("stock-count-label"),
  searchInput: document.getElementById("watchlist-search"),
  sectorChips: document.getElementById("sector-chips-container"),
  btnRefresh: document.getElementById("btn-refresh-all"),
  themeToggleBtn: document.getElementById("theme-toggle-btn"),
  themeIcon: document.getElementById("theme-icon"),
  marketStatusBadge: document.getElementById("market-status-badge"),
  marketStatusDot: document.getElementById("market-status-dot"),
  marketStatusText: document.getElementById("market-status-text"),
  simStreamBtn: document.getElementById("sim-stream-btn"),
  tabChart: document.getElementById("tab-chart"),
  tabGraph: document.getElementById("tab-graph"),
  chartViewport: document.getElementById("chart-viewport"),
  graphViewport: document.getElementById("graph-viewport"),
  chartContainer: document.getElementById("chart-container"),
  cyContainer: document.getElementById("cy-container"),
  cyBtnFit: document.getElementById("cy-btn-fit"),
  cyBtnZoomIn: document.getElementById("cy-btn-zoom-in"),
  cyBtnZoomOut: document.getElementById("cy-btn-zoom-out"),
  heroAvatar: document.getElementById("hero-avatar"),
  canvasSym: document.getElementById("canvas-symbol"),
  canvasName: document.getElementById("canvas-company-name"),
  canvasSector: document.getElementById("canvas-sector"),
  canvasPrice: document.getElementById("canvas-curr-price"),
  heroReturnPill: document.getElementById("hero-return-pill"),
  canvasCorridorSpan: document.getElementById("canvas-corridor-span"),
  headerRegime: document.getElementById("header-regime-label"),
  headerLatency: document.getElementById("header-latency-text"),
  dockActiveSymbol: document.getElementById("dock-active-symbol"),
  dockTotalBars: document.getElementById("dock-total-bars"),
  dockStorage: document.getElementById("dock-storage-size"),
  clockDisplay: document.getElementById("clock-display"),

  // AI Verdict Bar
  cardTiltBadge: document.getElementById("card-tilt-badge"),
  cardConfidence: document.getElementById("card-confidence"),
  cardMedianTarget: document.getElementById("card-median-target"),
  cardFloorQ05: document.getElementById("card-floor-q05"),
  cardCurrentLabel: document.getElementById("card-current-label"),
  cardCeilingQ95: document.getElementById("card-ceiling-q95"),
  cardInvalPrice: document.getElementById("card-inval-price"),
  cardThesisStatus: document.getElementById("card-thesis-status"),
  corridorPin: document.getElementById("corridor-pin"),
  statUpside: document.getElementById("stat-upside"),
  statDownside: document.getElementById("stat-downside"),
  statRrRatio: document.getElementById("stat-rr-ratio"),
  statInvalBuffer: document.getElementById("stat-inval-buffer"),

  // Dedicated 2-3 Month AI Future Projection Section
  futureOutlookSection: document.getElementById("future-outlook-section"),
  futureBullPrice: document.getElementById("future-bull-price"),
  futureBullPct: document.getElementById("future-bull-pct"),
  futureMedPrice: document.getElementById("future-med-price"),
  futureMedPct: document.getElementById("future-med-pct"),
  futureBearPrice: document.getElementById("future-bear-price"),
  futureBearPct: document.getElementById("future-bear-pct"),
  futureVerdictText: document.getElementById("future-verdict-text"),
  futureInvalText: document.getElementById("future-inval-text"),
  futureRrText: document.getElementById("future-rr-text"),
  futureConfidenceBadge: document.getElementById("future-confidence-badge"),

  // Tab Contents
  analogsContainer: document.getElementById("analogs-container"),
  revenueChartSvg: document.getElementById("revenue-chart-svg"),
  profitChartSvg: document.getElementById("profit-chart-svg"),
  cardFundFiling: document.getElementById("card-fund-filing"),
  cardFundRev: document.getElementById("card-fund-rev"),
  cardFundMargin: document.getElementById("card-fund-margin"),
  cardFundPat: document.getElementById("card-fund-pat"),
  cardFundDe: document.getElementById("card-fund-de"),
  cardFundPromoter: document.getElementById("card-fund-promoter"),
  cardFundPledged: document.getElementById("card-fund-pledged"),
  announcementsContainer: document.getElementById("announcements-container"),
  adviceStockLabel: document.getElementById("advice-stock-label"),
  statHitRate: document.getElementById("stat-hit-rate"),
  statHitFraction: document.getElementById("stat-hit-fraction"),
  statAvgReturn: document.getElementById("stat-avg-return"),
  statAvgDuration: document.getElementById("stat-avg-duration"),
  statProfitFactor: document.getElementById("stat-profit-factor"),
  adviceListContainer: document.getElementById("advice-list-container"),

  // Live Stream & RAG Co-Pilot Card
  liveTickerSymbol: document.getElementById("live-ticker-symbol"),
  liveTickerPrice: document.getElementById("live-ticker-price"),
  liveTickerSpread: document.getElementById("live-ticker-spread"),
  liveLearningStatus: document.getElementById("live-learning-status"),
  livePatternChip: document.getElementById("live-pattern-chip"),
  livePatternIcon: document.getElementById("live-pattern-icon"),
  livePatternName: document.getElementById("live-pattern-name"),
  livePatternDesc: document.getElementById("live-pattern-desc"),
  liveRsiVal: document.getElementById("live-rsi-val"),
  liveVwapVal: document.getElementById("live-vwap-val"),
  liveVolRatio: document.getElementById("live-vol-ratio"),
  liveBayesianVal: document.getElementById("live-bayesian-val"),
  ragPrecedentTitle: document.getElementById("rag-precedent-title"),
  ragWinRateVal: document.getElementById("rag-win-rate-val"),
  ragEpisodeSubtitle: document.getElementById("rag-episode-subtitle"),
  ragExpectedReturn: document.getElementById("rag-expected-return"),
  ragEntryRule: document.getElementById("rag-entry-rule"),
  ragStopPrice: document.getElementById("rag-stop-price"),
  ragTarget1: document.getElementById("rag-target-1"),
  ragMechanicsText: document.getElementById("rag-mechanics-text"),

  // Segment Switcher Elements
  segBtnMarkets: document.getElementById("seg-btn-markets"),
  segBtnCricket: document.getElementById("seg-btn-cricket"),
  marketsWatchlistContainer: document.getElementById("markets-watchlist-container"),
  cricketWatchlistContainer: document.getElementById("cricket-watchlist-container"),
  marketsWorkspaceContainer: document.getElementById("markets-workspace-container"),
  cricketWorkspaceContainer: document.getElementById("cricket-workspace-container"),

  // Cricket Watchlist Elements
  cricketMatchList: document.getElementById("cricket-match-list"),
  cricketCountLabel: document.getElementById("cricket-count-label"),
  cricketFormatChips: document.getElementById("cricket-format-chips"),

  // Cricket Hero Banner Elements
  cricketHeroBanner: document.getElementById("cricket-hero-banner"),
  cricketAvatarA: document.getElementById("cricket-avatar-a"),
  cricketAvatarB: document.getElementById("cricket-avatar-b"),
  cricketSeriesTitle: document.getElementById("cricket-series-title"),
  cricketTeamsTitle: document.getElementById("cricket-teams-title"),
  cricketFormatBadge: document.getElementById("cricket-format-badge"),
  cricketVenueText: document.getElementById("cricket-venue-text"),
  cricketTimeText: document.getElementById("cricket-time-text"),
  cricketStatusPill: document.getElementById("cricket-status-pill"),
  cricketStatusText: document.getElementById("cricket-status-text"),
  cricketLiveScore: document.getElementById("cricket-live-score"),
  cricketTossInfo: document.getElementById("cricket-toss-info"),
  cricketTeamNameA: document.getElementById("cricket-team-name-a"),
  cricketTeamNameB: document.getElementById("cricket-team-name-b"),
  cricketScoreValA: document.getElementById("cricket-score-val-a"),
  cricketScoreValB: document.getElementById("cricket-score-val-b"),
  cricketOversValA: document.getElementById("cricket-overs-val-a"),
  cricketOversValB: document.getElementById("cricket-overs-val-b"),
  cricketSessionBadge: document.getElementById("cricket-session-badge"),
  cricketLiveStatsStrip: document.getElementById("cricket-live-stats-strip"),
  cricketBattingHeader: document.getElementById("cricket-batting-header"),
  cricketBowlingHeader: document.getElementById("cricket-bowling-header"),
  cricketBatP1: document.getElementById("cricket-bat-p1"),
  cricketBatS1: document.getElementById("cricket-bat-s1"),
  cricketBatP2: document.getElementById("cricket-bat-p2"),
  cricketBatS2: document.getElementById("cricket-bat-s2"),
  cricketBowlP1: document.getElementById("cricket-bowl-p1"),
  cricketBowlS1: document.getElementById("cricket-bowl-s1"),
  cricketBowlP2: document.getElementById("cricket-bowl-p2"),
  cricketBowlS2: document.getElementById("cricket-bowl-s2"),

  // Cricket Win Probability Card Elements
  cricketWinCard: document.getElementById("cricket-win-card"),
  cricketConfidenceTag: document.getElementById("cricket-confidence-tag"),
  cricketMeterSideA: document.getElementById("cricket-meter-side-a"),
  cricketMeterSideB: document.getElementById("cricket-meter-side-b"),
  cricketMeterSideDraw: document.getElementById("cricket-meter-side-draw"),
  cricketProbLabelA: document.getElementById("cricket-prob-label-a"),
  cricketProbLabelB: document.getElementById("cricket-prob-label-b"),
  cricketProbLabelDraw: document.getElementById("cricket-prob-label-draw"),
  cricketPredictedWinner: document.getElementById("cricket-predicted-winner"),
  cricketRiskRating: document.getElementById("cricket-risk-rating"),
  cricketTacticalThesis: document.getElementById("cricket-tactical-thesis"),

  // Cricket Score Corridors Elements
  cricketCorridorQ95: document.getElementById("cricket-corridor-q95"),
  cricketCorridorQ50: document.getElementById("cricket-corridor-q50"),
  cricketCorridorQ05: document.getElementById("cricket-corridor-q05"),

  // Cricket Detail Tab Elements
  cricketH2hSummaryText: document.getElementById("cricket-h2h-summary-text"),
  cricketH2hPill: document.getElementById("cricket-h2h-pill"),
  cricketH2hMatchesList: document.getElementById("cricket-h2h-matches-list"),
  cricketVenueNameBold: document.getElementById("cricket-venue-name-bold"),
  cricketPitchTypePill: document.getElementById("cricket-pitch-type-pill"),
  cricketVenueAvgT20: document.getElementById("cricket-venue-avg-t20"),
  cricketVenueBat1stPct: document.getElementById("cricket-venue-bat1st-pct"),
  cricketVenueDew: document.getElementById("cricket-venue-dew"),
  cricketVenuePaceSpin: document.getElementById("cricket-venue-pace-spin"),
  cricketFactorsContainer: document.getElementById("cricket-factors-container"),
  cricketStatHitRate: document.getElementById("cricket-stat-hit-rate"),
  cricketStatFraction: document.getElementById("cricket-stat-fraction"),
  cricketStatConf: document.getElementById("cricket-stat-conf"),
  cricketAuditList: document.getElementById("cricket-audit-list"),

  // AI Learning Controls
  cricketRefreshLiveBtn: document.getElementById("cricket-refresh-live-btn"),
  cricketLearnBtn: document.getElementById("cricket-learn-btn"),
  cricketLearningAlert: document.getElementById("cricket-learning-alert"),
  btnLearnWinnerA: document.getElementById("btn-learn-winner-a"),
  btnLearnWinnerB: document.getElementById("btn-learn-winner-b")
};

// -------------------------------------------------------------
// Initialization
// -------------------------------------------------------------

async function init() {
  applyTheme(state.theme);
  initClock();
  initChart();
  setupEventListeners();

  // Load backend data in parallel
  await Promise.all([
    fetchSystemStatus(),
    fetchMacroRegime(),
    fetchAnnouncements(),
    loadUniverseSummary()
  ]);

  // Select initial stock
  selectStock(state.activeSymbol);

  // Auto-detect cricket segment parameter
  const urlParams = new URLSearchParams(window.location.search);
  const requestedSegment = urlParams.get("segment");
  if (requestedSegment === "cricket" || window.location.hash === "#cricket") {
    switchSegment("cricket");
  }
}

// -------------------------------------------------------------
// Indian Market Trading Hours (NSE / BSE IST)
// -------------------------------------------------------------

function getMarketSessionStatus() {
  // IST is UTC+5:30
  const now = new Date();
  const istString = now.toLocaleString("en-US", { timeZone: "Asia/Kolkata" });
  const istDate = new Date(istString);
  const day = istDate.getDay(); // 0 = Sunday, 6 = Saturday
  const hours = istDate.getHours();
  const minutes = istDate.getMinutes();
  const timeInMinutes = hours * 60 + minutes;

  // Trading days: Mon (1) to Fri (5)
  const isWeekday = day >= 1 && day <= 5;

  // Pre-market: 09:00 - 09:15 IST (540 to 555 min)
  const isPreMarket = isWeekday && timeInMinutes >= 540 && timeInMinutes < 555;

  // Regular trading: 09:15 - 15:30 IST (555 to 930 min)
  const isOpen = isWeekday && timeInMinutes >= 555 && timeInMinutes < 930;

  let label = "Market Closed (EOD)";
  let badgeClass = "status-closed";

  if (isOpen) {
    label = "NSE / BSE Active (09:15 - 15:30)";
    badgeClass = "status-open";
  } else if (isPreMarket) {
    label = "Pre-Open Session (09:00 - 09:15)";
    badgeClass = "status-pre";
  } else if (!isWeekday) {
    label = "Weekend Closed (NSE / BSE)";
    badgeClass = "status-closed";
  }

  return { isOpen, isPreMarket, isWeekday, label, badgeClass };
}

function updateMarketSessionBadge() {
  const session = getMarketSessionStatus();
  if (el.marketStatusBadge && el.marketStatusText) {
    el.marketStatusBadge.className = `status-badge ${session.badgeClass}`;
    if (state.isSimulationMode) {
      el.marketStatusText.textContent = `${session.label} • Sim Mode Active`;
    } else {
      el.marketStatusText.textContent = session.label;
    }
  }
}

// -------------------------------------------------------------
// Theme Management (Groww Dark / Light)
// -------------------------------------------------------------

function applyTheme(theme) {
  state.theme = theme;
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("titan_theme", theme);

  if (el.themeIcon) {
    el.themeIcon.textContent = theme === "dark" ? "☀️" : "🌙";
  }

  // Update chart colors if initialized
  if (state.chart) {
    const isDark = theme === "dark";
    state.chart.applyOptions({
      layout: {
        background: { color: isDark ? "#151B26" : "#FFFFFF" },
        textColor: isDark ? "#94A3B8" : "#4A5568"
      },
      grid: {
        vertLines: { color: isDark ? "#1C2433" : "#F0F3F7" },
        horzLines: { color: isDark ? "#1C2433" : "#F0F3F7" }
      },
      timeScale: {
        borderColor: isDark ? "#232C3D" : "#E2E8F0"
      },
      rightPriceScale: {
        borderColor: isDark ? "#232C3D" : "#E2E8F0"
      }
    });
  }
}

function toggleTheme() {
  const nextTheme = state.theme === "dark" ? "light" : "dark";
  applyTheme(nextTheme);
}

// -------------------------------------------------------------
// Live Clock
// -------------------------------------------------------------

function initClock() {
  function update() {
    const now = new Date();
    if (el.clockDisplay) {
      el.clockDisplay.textContent = now.toLocaleTimeString("en-GB") + " IST";
    }
    updateMarketSessionBadge();
  }
  update();
  setInterval(update, 1000);
}

// -------------------------------------------------------------
// TradingView Lightweight Charts Setup
// -------------------------------------------------------------

function initChart() {
  if (!window.LightweightCharts) {
    console.error("TradingView Lightweight Charts library not found.");
    return;
  }

  const isDark = state.theme === "dark";
  const initialWidth = el.chartContainer.clientWidth || 800;
  const initialHeight = el.chartContainer.clientHeight || 440;

  const chart = LightweightCharts.createChart(el.chartContainer, {
    width: initialWidth,
    height: initialHeight,
    layout: {
      background: { color: isDark ? "#151B26" : "#FFFFFF" },
      textColor: isDark ? "#94A3B8" : "#4A5568",
      fontFamily: "'Inter', -apple-system, sans-serif",
      fontSize: 11
    },
    grid: {
      vertLines: { color: isDark ? "#1C2433" : "#F0F3F7" },
      horzLines: { color: isDark ? "#1C2433" : "#F0F3F7" }
    },
    crosshair: {
      mode: LightweightCharts.CrosshairMode.Normal,
      vertLine: { color: "#00D09C", width: 1, style: LightweightCharts.LineStyle.Dotted },
      horzLine: { color: "#00D09C", width: 1, style: LightweightCharts.LineStyle.Dotted }
    },
    timeScale: {
      borderColor: isDark ? "#232C3D" : "#E2E8F0",
      timeVisible: false, // Prevents 00:00 and single-day display artifacts on daily charts
      secondsVisible: false
    },
    rightPriceScale: {
      borderColor: isDark ? "#232C3D" : "#E2E8F0",
      autoScale: true,
      scaleMargins: { top: 0.08, bottom: 0.20 }
    }
  });

  // Candlestick Series (Groww Emerald & Coral)
  const candleSeries = chart.addCandlestickSeries({
    upColor: "#00D09C",
    downColor: "#EB5757",
    borderVisible: false,
    wickUpColor: "#00D09C",
    wickDownColor: "#EB5757"
  });

  // Volume Histogram Series
  const volumeSeries = chart.addHistogramSeries({
    priceFormat: { type: "volume" },
    priceScaleId: "",
    scaleMargins: { top: 0.82, bottom: 0 }
  });

  // Quantile Corridor Forward Projections
  const upperSeries = chart.addLineSeries({
    color: "#00D09C",
    lineWidth: 2,
    lineStyle: LightweightCharts.LineStyle.Dashed,
    title: "Bullish Ceiling"
  });

  const medianSeries = chart.addLineSeries({
    color: "#00F0FF",
    lineWidth: 2,
    lineStyle: LightweightCharts.LineStyle.Solid,
    title: "Expected Target"
  });

  const lowerSeries = chart.addLineSeries({
    color: "#EB5757",
    lineWidth: 2,
    lineStyle: LightweightCharts.LineStyle.Dashed,
    title: "Bearish Floor"
  });

  state.chart = chart;
  state.candleSeries = candleSeries;
  state.volumeSeries = volumeSeries;
  state.upperSeries = upperSeries;
  state.medianSeries = medianSeries;
  state.lowerSeries = lowerSeries;

  // ResizeObserver guarantees responsive resizing on all screens
  if (window.ResizeObserver) {
    const ro = new ResizeObserver(entries => {
      for (const entry of entries) {
        if (entry.contentRect.width > 0 && entry.contentRect.height > 0) {
          chart.applyOptions({
            width: entry.contentRect.width,
            height: entry.contentRect.height
          });
        }
      }
    });
    ro.observe(el.chartContainer);
  }
}

// -------------------------------------------------------------
// API Data Fetching
// -------------------------------------------------------------

async function fetchSystemStatus() {
  try {
    const res = await fetch("/api/v1/system/status");
    const data = await res.json();
    if (el.headerLatency) el.headerLatency.textContent = `${data.query_latency_ms}ms`;
    if (el.dockTotalBars) el.dockTotalBars.textContent = Number(data.total_daily_bars).toLocaleString();
    if (el.dockStorage) el.dockStorage.textContent = `${data.db_size_mb} MB DuckDB`;
  } catch (err) {
    console.error("Failed to fetch system status:", err);
  }
}

async function fetchMacroRegime() {
  try {
    const res = await fetch("/api/v1/macro/regime");
    const data = await res.json();
    state.macroRegime = data;
    if (data.regime && data.regime.regime_label && el.headerRegime) {
      el.headerRegime.textContent = data.regime.regime_label;
    }
  } catch (err) {
    console.error("Failed to fetch macro regime:", err);
  }
}

async function fetchAnnouncements() {
  try {
    const res = await fetch("/api/v1/announcements");
    const data = await res.json();
    state.announcements = data;
    renderAnnouncements(data);
  } catch (err) {
    console.error("Failed to fetch announcements:", err);
  }
}

async function loadUniverseSummary() {
  try {
    const res = await fetch("/api/v1/universe/summary");
    const data = await res.json();
    state.universeSummary = data;
    applyFilters();
  } catch (err) {
    console.error("Failed to load universe summary:", err);
  }
}

// -------------------------------------------------------------
// Watchlist Filtering & Rendering (Groww Clean Style)
// -------------------------------------------------------------

function getAvatarInitials(symbol, companyName) {
  if (symbol.length <= 4) return symbol;
  const words = companyName.split(" ").filter(w => w.length > 0 && !["LTD", "LIMITED", "CORP", "INC"].includes(w.toUpperCase()));
  if (words.length >= 2) {
    return (words[0][0] + words[1][0]).toUpperCase();
  }
  return symbol.slice(0, 2).toUpperCase();
}

function applyFilters() {
  const q = state.searchQuery.trim().toUpperCase();
  const sec = state.activeSector;

  state.filteredSummary = state.universeSummary.filter(item => {
    const matchSearch = !q || item.symbol.toUpperCase().includes(q) || item.company_name.toUpperCase().includes(q) || item.sector.toUpperCase().includes(q);
    const matchSector = sec === "ALL" || item.sector === sec;
    return matchSearch && matchSector;
  });

  if (el.stockCount) el.stockCount.textContent = `${state.filteredSummary.length} Stocks`;
  renderWatchlist();
}

function renderWatchlist() {
  if (!el.stockList) return;
  el.stockList.innerHTML = "";

  state.filteredSummary.forEach(item => {
    const li = document.createElement("li");
    li.className = `stock-card ${item.symbol === state.activeSymbol ? "active" : ""}`;
    li.dataset.symbol = item.symbol;

    const change20 = item.change_20d_pct;
    const isPositive = change20 >= 0;
    const pillClass = isPositive ? "pill-positive" : "pill-negative";
    const sign = isPositive ? "+" : "";

    const initials = getAvatarInitials(item.symbol, item.company_name);

    li.innerHTML = `
      <div class="stock-card-left">
        <div class="stock-avatar">${initials}</div>
        <div class="stock-info">
          <span class="stock-symbol-text">${item.symbol}</span>
          <span class="stock-company-text" title="${item.company_name}">${item.company_name}</span>
        </div>
      </div>
      <div class="stock-card-right">
        <span class="stock-price-text">₹${item.current_price.toLocaleString("en-IN", { minimumFractionDigits: 2 })}</span>
        <span class="stock-return-pill ${pillClass}">${sign}${change20.toFixed(2)}%</span>
      </div>
    `;

    li.addEventListener("click", () => selectStock(item.symbol));
    el.stockList.appendChild(li);
  });
}

// -------------------------------------------------------------
// Stock Selection & Details Update
// -------------------------------------------------------------

async function selectStock(symbol) {
  state.activeSymbol = symbol;
  if (el.dockActiveSymbol) el.dockActiveSymbol.textContent = symbol;

  // Highlight card in watchlist
  document.querySelectorAll(".stock-card").forEach(c => {
    c.classList.toggle("active", c.dataset.symbol === symbol);
  });

  const item = state.universeSummary.find(s => s.symbol === symbol);
  if (item) {
    // 1. Hero Card
    if (el.heroAvatar) el.heroAvatar.textContent = getAvatarInitials(item.symbol, item.company_name);
    if (el.canvasName) el.canvasName.textContent = item.company_name;
    if (el.canvasSym) el.canvasSym.textContent = item.symbol;
    if (el.canvasSector) el.canvasSector.textContent = item.sector;
    if (el.canvasPrice) el.canvasPrice.textContent = `₹${item.current_price.toLocaleString("en-IN", { minimumFractionDigits: 2 })}`;

    const chg = item.change_20d_pct;
    const isPos = chg >= 0;
    const sign = isPos ? "+" : "";
    const rupeeDiff = (item.current_price * (chg / 100)).toFixed(2);
    if (el.heroReturnPill) {
      el.heroReturnPill.className = `hero-change-pill ${isPos ? "pill-positive" : "pill-negative"}`;
      el.heroReturnPill.textContent = `${sign}₹${Math.abs(rupeeDiff)} (${sign}${chg.toFixed(2)}%) 20D`;
    }

    // 2. AI Verdict Bar
    updateAiVerdictBar(item);

    // 3. Corridor Range Meter
    updateCorridorMeter(item);

    // 4. Dedicated 2-3 Month AI Future Projection Section
    updateFutureOutlookSection(item);
  }

  // Load details
  loadChartData(symbol);
  loadAnalogs(symbol);
  loadFundamentals(symbol);
  loadAdviceHistory(symbol);
  if (state.activeView === "graph") {
    loadGraphData(symbol);
  }

  // Refresh announcements to focus on selected stock
  renderAnnouncements(state.announcements);

  // Connect live 1-second market stream & RAG co-pilot
  connectLiveStream(symbol);
}

function updateAiVerdictBar(item) {
  if (!el.cardTiltBadge) return;
  // Outlook
  let tiltLabel = "Neutral Outlook";
  let tiltColor = "var(--text-secondary)";
  if (item.directional_tilt === "BULLISH") {
    tiltLabel = "Bullish Outlook";
    tiltColor = "var(--groww-green)";
  } else if (item.directional_tilt === "BEARISH") {
    tiltLabel = "Bearish Outlook";
    tiltColor = "var(--groww-red)";
  }
  el.cardTiltBadge.textContent = tiltLabel;
  el.cardTiltBadge.style.color = tiltColor;
  if (el.cardConfidence) el.cardConfidence.textContent = `${item.confidence_score_pct.toFixed(0)}% AI Confidence`;

  // Target
  const medSign = item.projected_median_return_pct >= 0 ? "+" : "";
  if (el.cardMedianTarget) el.cardMedianTarget.textContent = `₹${item.projected_median_price.toFixed(2)} (${medSign}${item.projected_median_return_pct.toFixed(1)}%)`;
  if (el.canvasCorridorSpan) el.canvasCorridorSpan.textContent = `Range: ₹${item.bearish_floor_price_q05.toFixed(0)} – ₹${item.bullish_ceiling_price_q95.toFixed(0)}`;

  // Invalidation Stop-Loss
  if (el.cardInvalPrice) el.cardInvalPrice.textContent = `₹${item.invalidation_floor.toFixed(2)}`;
  const isWarning = item.thesis_status && item.thesis_status.includes("WARNING");
  if (el.cardThesisStatus) {
    if (isWarning) {
      el.cardThesisStatus.textContent = `⚠️ High Alert (${item.distance_to_invalidation_pct.toFixed(1)}% buffer)`;
      el.cardThesisStatus.style.color = "var(--groww-red)";
    } else {
      el.cardThesisStatus.textContent = `Safe (${item.distance_to_invalidation_pct.toFixed(1)}% buffer)`;
      el.cardThesisStatus.style.color = "var(--groww-green)";
    }
  }
}

function updateCorridorMeter(item) {
  const curr = item.current_price;
  const floor = item.bearish_floor_price_q05;
  const ceil = item.bullish_ceiling_price_q95;

  if (el.cardFloorQ05) el.cardFloorQ05.textContent = `Floor: ₹${floor.toFixed(0)}`;
  if (el.cardCurrentLabel) el.cardCurrentLabel.textContent = `Current: ₹${curr.toFixed(2)}`;
  if (el.cardCeilingQ95) el.cardCeilingQ95.textContent = `Ceiling: ₹${ceil.toFixed(0)}`;

  // Position the pin on the gradient track (clamped 6% to 94%)
  if (ceil > floor && el.corridorPin) {
    let pinPct = ((curr - floor) / (ceil - floor)) * 100;
    pinPct = Math.max(6, Math.min(94, pinPct));
    el.corridorPin.style.left = `${pinPct}%`;
  }

  // Mini stats
  const upside = ((ceil - curr) / curr) * 100;
  const downside = ((curr - floor) / curr) * 100;
  if (el.statUpside) el.statUpside.textContent = `+${upside.toFixed(1)}%`;
  if (el.statDownside) el.statDownside.textContent = `-${downside.toFixed(1)}%`;

  if (el.statRrRatio) {
    if (downside > 0) {
      const rr = (upside / downside).toFixed(2);
      el.statRrRatio.textContent = `1 : ${rr}`;
    } else {
      el.statRrRatio.textContent = "1 : >3.0";
    }
  }
  if (el.statInvalBuffer) el.statInvalBuffer.textContent = `${item.distance_to_invalidation_pct.toFixed(1)}%`;
}

// -------------------------------------------------------------
// Dedicated 2-3 Month AI Future Projection Section
// -------------------------------------------------------------

function updateFutureOutlookSection(item) {
  if (!item) return;

  const curr = item.current_price;
  const bullPrice = item.bullish_ceiling_price_q95;
  const medPrice = item.projected_median_price;
  const bearPrice = item.bearish_floor_price_q05;

  const bullPct = curr > 0 ? (((bullPrice - curr) / curr) * 100).toFixed(1) : "0.0";
  const medPct = item.projected_median_return_pct !== undefined 
    ? item.projected_median_return_pct.toFixed(1) 
    : (curr > 0 ? (((medPrice - curr) / curr) * 100).toFixed(1) : "0.0");
  const bearPct = curr > 0 ? (((curr - bearPrice) / curr) * 100).toFixed(1) : "0.0";

  // Scenario 1: Bullish Ceiling
  if (el.futureBullPrice) el.futureBullPrice.textContent = `₹${bullPrice.toLocaleString("en-IN", { minimumFractionDigits: 2 })}`;
  if (el.futureBullPct) el.futureBullPct.textContent = `+${bullPct}%`;

  // Scenario 2: Baseline Median Target
  if (el.futureMedPrice) el.futureMedPrice.textContent = `₹${medPrice.toLocaleString("en-IN", { minimumFractionDigits: 2 })}`;
  if (el.futureMedPct) {
    const sign = Number(medPct) >= 0 ? "+" : "";
    el.futureMedPct.textContent = `${sign}${medPct}%`;
  }

  // Scenario 3: Bearish Floor
  if (el.futureBearPrice) el.futureBearPrice.textContent = `₹${bearPrice.toLocaleString("en-IN", { minimumFractionDigits: 2 })}`;
  if (el.futureBearPct) el.futureBearPct.textContent = `-${bearPct}%`;

  // Strategic Verdict
  if (el.futureVerdictText) {
    if (item.directional_tilt === "BULLISH") {
      el.futureVerdictText.textContent = "Bullish Accumulation on Dips";
      el.futureVerdictText.style.color = "var(--groww-green)";
    } else if (item.directional_tilt === "BEARISH") {
      el.futureVerdictText.textContent = "Bearish Distribution / Capital Protection";
      el.futureVerdictText.style.color = "var(--groww-red)";
    } else {
      el.futureVerdictText.textContent = "Neutral Rangebound Rotation";
      el.futureVerdictText.style.color = "var(--text-secondary)";
    }
  }

  // Stop-Loss Invalidation
  if (el.futureInvalText) {
    el.futureInvalText.textContent = `₹${item.invalidation_floor.toFixed(2)} (${item.distance_to_invalidation_pct.toFixed(1)}% buffer)`;
  }

  // Risk / Reward
  if (el.futureRrText) {
    const upside = bullPrice - curr;
    const downside = curr - bearPrice;
    if (downside > 0) {
      el.futureRrText.textContent = `1 : ${(upside / downside).toFixed(2)}`;
    } else {
      el.futureRrText.textContent = "1 : >3.0";
    }
  }

  // Model Confidence Tag
  if (el.futureConfidenceBadge) {
    el.futureConfidenceBadge.textContent = `${item.confidence_score_pct.toFixed(0)}% AI Confidence`;
  }
}

// -------------------------------------------------------------
// Live Real-Time 1-Second Stream & RAG Co-Pilot Engine
// -------------------------------------------------------------

function connectLiveStream(symbol) {
  // Clean up any existing live connections
  if (state.liveSocket) {
    try { state.liveSocket.close(); } catch (e) {}
    state.liveSocket = null;
  }
  if (state.liveInterval) {
    clearInterval(state.liveInterval);
    state.liveInterval = null;
  }

  const session = getMarketSessionStatus();
  const canStream = session.isOpen || state.isSimulationMode;

  if (!canStream) {
    console.log(`[Titan Market Hours] Market is closed. Live tick stream paused for ${symbol}. Showing today's complete session bar.`);
    if (el.liveLearningStatus) {
      el.liveLearningStatus.textContent = "Market Closed (Session Freeze)";
      el.liveLearningStatus.style.color = "var(--text-muted)";
    }
    if (el.liveTickerSpread) {
      el.liveTickerSpread.textContent = "Official Session Closed (03:30 PM IST) • Toggle Sim Stream for live ticks";
    }
    return;
  }

  const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${proto}//${window.location.host}/ws/live-stream/${symbol}`;

  let wsFailed = false;
  try {
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log(`[Titan Live] Connected to WebSocket stream for ${symbol}`);
      if (el.liveLearningStatus) {
        el.liveLearningStatus.textContent = state.isSimulationMode ? "Sim Stream (1s loop)" : "Active Live (1s loop)";
        el.liveLearningStatus.style.color = "var(--groww-green)";
      }
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleLiveStreamPacket(data);
      } catch (err) {
        console.error("Failed to parse live packet:", err);
      }
    };

    ws.onerror = (err) => {
      console.warn("[Titan Live] WebSocket encountered error, engaging fallback polling:", err);
      wsFailed = true;
      startFallbackPolling(symbol);
    };

    ws.onclose = () => {
      if (!wsFailed) {
        console.log(`[Titan Live] WebSocket closed for ${symbol}`);
      }
    };

    state.liveSocket = ws;
  } catch (err) {
    console.warn("[Titan Live] WebSocket init failed, starting polling fallback:", err);
    startFallbackPolling(symbol);
  }
}

function startFallbackPolling(symbol) {
  if (state.liveInterval) clearInterval(state.liveInterval);
  state.liveInterval = setInterval(async () => {
    try {
      const res = await fetch(`/api/v1/stocks/${symbol}/live-packet`);
      const data = await res.json();
      handleLiveStreamPacket(data);
    } catch (e) {
      console.error("Fallback polling error:", e);
    }
  }, 1000);
}

function handleLiveStreamPacket(data) {
  if (!data || data.symbol !== state.activeSymbol) return;

  const newPrice = Number(data.current_price);
  if (!newPrice || isNaN(newPrice) || newPrice <= 0) return;

  // Circuit limit guardrail: Reject any price tick that deviates by > 5% from verified baseline
  const verifiedStock = state.universeSummary.find(s => s.symbol === data.symbol);
  if (verifiedStock && verifiedStock.current_price > 0) {
    const deviation = Math.abs(newPrice - verifiedStock.current_price) / verifiedStock.current_price;
    if (deviation > 0.05) {
      console.warn(`[Titan Guardrail] Rejected anomalous tick price ₹${newPrice} for ${data.symbol}`);
      return;
    }
  }

  const oldPrice = state.lastStreamPrice || newPrice;
  state.lastStreamPrice = newPrice;

  // 1. Live update forming candle on TradingView Lightweight Charts
  if (data.forming_candle && state.candleSeries) {
    const fc = data.forming_candle;
    const cleanCandle = {
      time: String(fc.time).split(" ")[0].split("T")[0],
      open: Number(fc.open),
      high: Number(fc.high),
      low: Number(fc.low),
      close: Number(fc.close)
    };
    try {
      state.candleSeries.update(cleanCandle);
    } catch (e) {
      // Ignore boundary errors if any
    }
  }

  // 2. Flash animation & Live Price in Hero Header
  if (el.canvasPrice) {
    el.canvasPrice.textContent = `₹${newPrice.toLocaleString("en-IN", { minimumFractionDigits: 2 })}`;
    el.canvasPrice.classList.remove("flash-green", "flash-red");
    void el.canvasPrice.offsetWidth; // Trigger DOM reflow to restart animation
    if (newPrice > oldPrice) {
      el.canvasPrice.classList.add("flash-green");
    } else if (newPrice < oldPrice) {
      el.canvasPrice.classList.add("flash-red");
    }
  }

  // 3. Update Live Ticker Header in Live Card
  if (el.liveTickerSymbol) el.liveTickerSymbol.textContent = data.symbol;
  if (el.liveTickerPrice) {
    const chg = data.total_change_pct !== undefined ? data.total_change_pct : data.tick_change_pct;
    const sign = chg >= 0 ? "+" : "";
    el.liveTickerPrice.textContent = `₹${newPrice.toFixed(2)} (${sign}${chg.toFixed(2)}%)`;
    el.liveTickerPrice.style.color = chg >= 0 ? "var(--groww-green)" : "var(--groww-red)";
  }
  if (el.liveTickerSpread) {
    el.liveTickerSpread.textContent = `Bid: ₹${data.bid.toFixed(2)} • Ask: ₹${data.ask.toFixed(2)}`;
  }

  // 4. Update Online Learning Indicators
  const m = data.online_metrics;
  if (m) {
    if (el.liveRsiVal) {
      el.liveRsiVal.textContent = m.rsi.toFixed(1);
      el.liveRsiVal.style.color = m.rsi > 70 ? "var(--groww-red)" : (m.rsi < 30 ? "var(--groww-green)" : "var(--text-primary)");
    }
    if (el.liveVwapVal) el.liveVwapVal.textContent = `₹${m.vwap.toFixed(2)}`;
    if (el.liveVolRatio) {
      el.liveVolRatio.textContent = `${m.volume_ratio.toFixed(1)}x`;
      el.liveVolRatio.style.color = m.volume_ratio >= 1.7 ? "var(--groww-green)" : "var(--text-primary)";
    }
    if (el.liveBayesianVal) {
      const bPct = Math.round(m.bayesian_bullish_prob * 100);
      el.liveBayesianVal.textContent = `${bPct}%`;
      el.liveBayesianVal.style.color = bPct >= 55 ? "var(--groww-green)" : (bPct <= 45 ? "var(--groww-red)" : "var(--text-secondary)");
    }
  }

  // 5. Update Recognized Pattern Badge & Description
  const pat = data.active_pattern;
  if (pat) {
    if (el.livePatternName) el.livePatternName.textContent = pat.name;
    if (el.livePatternDesc) el.livePatternDesc.textContent = pat.description;
    if (el.livePatternIcon) {
      if (pat.directional_bias === "BULLISH") el.livePatternIcon.textContent = "🚀";
      else if (pat.directional_bias === "BEARISH") el.livePatternIcon.textContent = "⚠️";
      else if (pat.pattern_id === "VOLATILITY_SQUEEZE") el.livePatternIcon.textContent = "⚡";
      else el.livePatternIcon.textContent = "🔄";
    }
  }

  // 6. Update RAG Intelligence Card
  const rag = data.rag_intelligence;
  if (rag) {
    if (el.ragPrecedentTitle) el.ragPrecedentTitle.textContent = rag.pattern_name;
    if (el.ragWinRateVal) el.ragWinRateVal.textContent = `${rag.win_rate_pct.toFixed(1)}%`;
    if (el.ragEpisodeSubtitle) el.ragEpisodeSubtitle.textContent = `Matched: ${rag.historical_precedent}`;
    if (el.ragExpectedReturn) {
      const sign = rag.expected_return_5d_pct >= 0 ? "+" : "";
      el.ragExpectedReturn.textContent = `${sign}${rag.expected_return_5d_pct.toFixed(1)}%`;
      el.ragExpectedReturn.style.color = rag.expected_return_5d_pct >= 0 ? "var(--groww-green)" : "var(--groww-red)";
    }
    if (el.ragEntryRule) el.ragEntryRule.textContent = rag.entry_rule;
    if (el.ragStopPrice) el.ragStopPrice.textContent = `₹${rag.stop_loss_price.toFixed(2)}`;
    if (el.ragTarget1) el.ragTarget1.textContent = `₹${rag.target_1_price.toFixed(2)}`;
    if (el.ragMechanicsText) el.ragMechanicsText.textContent = rag.institutional_mechanics;
  }

  // 7. Update Left Watchlist Card for Active Stock
  const activeLi = document.querySelector(`.stock-card[data-symbol="${data.symbol}"]`);
  if (activeLi) {
    const pEl = activeLi.querySelector(".stock-price-text");
    if (pEl) pEl.textContent = `₹${newPrice.toLocaleString("en-IN", { minimumFractionDigits: 2 })}`;
  }
}

// -------------------------------------------------------------
// Chart Data Loading & Rendering (Robust Scale Resetting)
// -------------------------------------------------------------

async function loadChartData(symbol) {
  try {
    // Guard against race conditions
    if (symbol !== state.activeSymbol) return;

    // 0. RESET ALL SERIES & REMOVE PRICE LINE IMMEDIATELY TO PREVENT RESCALE SQUISHING
    if (state.candleSeries) state.candleSeries.setData([]);
    if (state.volumeSeries) state.volumeSeries.setData([]);
    if (state.upperSeries) state.upperSeries.setData([]);
    if (state.medianSeries) state.medianSeries.setData([]);
    if (state.lowerSeries) state.lowerSeries.setData([]);
    if (state.priceLine && state.candleSeries) {
      try {
        state.candleSeries.removePriceLine(state.priceLine);
      } catch (e) {}
      state.priceLine = null;
    }

    const [histRes, corrRes] = await Promise.all([
      fetch(`/api/v1/stocks/${symbol}/history`),
      fetch(`/api/v1/stocks/${symbol}/corridor`)
    ]);

    // Check if user switched stock while fetching
    if (symbol !== state.activeSymbol) return;

    const hist = await histRes.json();
    const corr = await corrRes.json();

    if (hist && hist.candles && state.candleSeries) {
      // 1. Sanitize & deduplicate candles strictly for LightweightCharts
      const cleanCandles = [];
      const cleanVolumes = [];
      const seenDates = new Set();

      for (let i = 0; i < hist.candles.length; i++) {
        const c = hist.candles[i];
        // Strictly parse YYYY-MM-DD
        const timeStr = String(c.time).split(" ")[0].split("T")[0];
        if (!seenDates.has(timeStr) && timeStr.length === 10) {
          seenDates.add(timeStr);
          cleanCandles.push({
            time: timeStr,
            open: Number(c.open),
            high: Number(c.high),
            low: Number(c.low),
            close: Number(c.close)
          });

          if (hist.volumes && hist.volumes[i]) {
            const v = hist.volumes[i];
            cleanVolumes.push({
              time: timeStr,
              value: Number(v.value),
              color: Number(c.close) >= Number(c.open) ? "#00D09C" : "#EB5757"
            });
          }
        }
      }

      // Sort ascending by time
      cleanCandles.sort((a, b) => a.time.localeCompare(b.time));
      cleanVolumes.sort((a, b) => a.time.localeCompare(b.time));

      state.candleSeries.setData(cleanCandles);
      state.volumeSeries.setData(cleanVolumes);

      // 2. Add stepped invalidation price line with strict sanity check
      if (corr && corr.invalidation_floor && state.candleSeries && cleanCandles.length > 0) {
        const lastClose = cleanCandles[cleanCandles.length - 1].close;
        const invalPrice = Number(corr.invalidation_floor);
        // Only render price line if it is in valid range for this specific stock
        if (invalPrice > 0 && Math.abs(invalPrice - lastClose) / lastClose < 0.6) {
          state.priceLine = state.candleSeries.createPriceLine({
            price: invalPrice,
            color: "#EF4444",
            lineWidth: 2,
            lineStyle: LightweightCharts.LineStyle.Dashed,
            axisLabelVisible: true,
            title: `Stop-Loss @ ₹${invalPrice.toFixed(2)}`
          });
        }
      }

      // 3. Sanitize and set forward quantile corridor trajectories
      if (corr && corr.median_series && state.medianSeries) {
        const sanitizeSeries = (raw) => {
          const res = [];
          const seen = new Set();
          for (const pt of raw) {
            const t = String(pt.time).split(" ")[0].split("T")[0];
            if (!seen.has(t) && t.length === 10) {
              seen.add(t);
              res.push({ time: t, value: Number(pt.value) });
            }
          }
          return res.sort((a, b) => a.time.localeCompare(b.time));
        };

        state.medianSeries.setData(sanitizeSeries(corr.median_series));
        state.upperSeries.setData(sanitizeSeries(corr.upper_series));
        state.lowerSeries.setData(sanitizeSeries(corr.lower_series));
      }

      // Auto-scale right price scale strictly to current equity data
      if (state.chart) {
        state.chart.priceScale("right").applyOptions({ autoScale: true });
        if (el.chartContainer.clientWidth > 0 && el.chartContainer.clientHeight > 0) {
          state.chart.applyOptions({
            width: el.chartContainer.clientWidth,
            height: el.chartContainer.clientHeight
          });
        }
        state.chart.timeScale().fitContent();
      }
    }
  } catch (err) {
    console.error(`Failed to load chart data for ${symbol}:`, err);
  }
}

// -------------------------------------------------------------
// Historical Pattern Analogies (FastDTW - Groww Friendly Cards)
// -------------------------------------------------------------

async function loadAnalogs(symbol) {
  try {
    const res = await fetch(`/api/v1/stocks/${symbol}/analog`);
    const analogs = await res.json();
    renderAnalogs(analogs);
  } catch (err) {
    console.error(`Failed to load analogs for ${symbol}:`, err);
  }
}

function renderAnalogs(analogs) {
  if (!el.analogsContainer) return;
  el.analogsContainer.innerHTML = "";
  if (!analogs || analogs.length === 0) {
    el.analogsContainer.innerHTML = `<div style="font-size: 12px; color: var(--text-muted); padding: 8px 0;">No matching consolidation patterns found for current window.</div>`;
    return;
  }

  analogs.forEach((a, idx) => {
    const simPct = (a.similarity_score * 100).toFixed(0);
    const ret = a.subsequent_6m_return_pct;
    const isPos = ret >= 0;
    const retColor = isPos ? "var(--groww-green)" : "var(--groww-red)";
    const sign = isPos ? "+" : "";

    const div = document.createElement("div");
    div.className = "analog-card-item";
    div.innerHTML = `
      <div class="analog-meta-left">
        <span class="analog-date-label">Episode #${idx + 1} • ${a.match_date}</span>
        <span class="analog-match-badge">${simPct}% Pattern Similarity</span>
      </div>
      <div class="analog-stats-right">
        <div>
          <span style="color: var(--text-muted); font-size: 10px; display: block;">6-Month Outcome</span>
          <span class="analog-ret-bold" style="color: ${retColor};">${sign}${ret.toFixed(1)}%</span>
        </div>
        <div>
          <span style="color: var(--text-muted); font-size: 10px; display: block;">Max Rally</span>
          <span style="color: var(--groww-green); font-weight: 600;">+${a.subsequent_6m_max_rally_pct.toFixed(1)}%</span>
        </div>
        <div>
          <span style="color: var(--text-muted); font-size: 10px; display: block;">Max Drawdown</span>
          <span style="color: var(--groww-red); font-weight: 600;">${a.subsequent_6m_max_drawdown_pct.toFixed(1)}%</span>
        </div>
      </div>
    `;
    el.analogsContainer.appendChild(div);
  });
}

// -------------------------------------------------------------
// Fundamentals & Visual Financial Charts
// -------------------------------------------------------------

async function loadFundamentals(symbol) {
  try {
    const res = await fetch(`/api/v1/stocks/${symbol}/fundamentals`);
    const funds = await res.json();
    state.currentFundamentals = funds || [];
    if (funds && funds.length > 0) {
      const latest = funds[0];
      if (el.cardFundFiling) el.cardFundFiling.textContent = `Quarterly Statement filed officially on ${latest.filing_timestamp.slice(0, 10)}`;
      if (el.cardFundRev) el.cardFundRev.textContent = `₹${Math.round(latest.revenue_cr).toLocaleString("en-IN")} Cr`;
      if (el.cardFundMargin) el.cardFundMargin.textContent = `${latest.ebitda_margin_pct.toFixed(1)}%`;
      if (el.cardFundPat) el.cardFundPat.textContent = `₹${Math.round(latest.pat_cr).toLocaleString("en-IN")} Cr`;
      if (el.cardFundDe) el.cardFundDe.textContent = latest.debt_to_equity.toFixed(2);
      if (el.cardFundPromoter) el.cardFundPromoter.textContent = `${latest.promoter_holding_pct.toFixed(1)}%`;
      
      const pledged = latest.pledged_promoter_pct;
      if (el.cardFundPledged) {
        if (pledged === 0) {
          el.cardFundPledged.textContent = "0.0% (Zero Risk)";
          el.cardFundPledged.style.color = "var(--groww-green)";
        } else {
          el.cardFundPledged.textContent = `${pledged.toFixed(1)}% Pledged`;
          el.cardFundPledged.style.color = "var(--groww-red)";
        }
      }

      // Render Visual Financial SVG Charts
      renderFinancialCharts(funds);
    } else {
      if (el.cardFundFiling) el.cardFundFiling.textContent = "Verified Point-in-Time";
      if (el.cardFundRev) el.cardFundRev.textContent = "--";
      if (el.cardFundMargin) el.cardFundMargin.textContent = "--";
      if (el.cardFundPat) el.cardFundPat.textContent = "--";
      if (el.cardFundDe) el.cardFundDe.textContent = "--";
      if (el.cardFundPromoter) el.cardFundPromoter.textContent = "--";
      if (el.cardFundPledged) el.cardFundPledged.textContent = "--";

      renderFinancialCharts([]);
    }
  } catch (err) {
    console.error(`Failed to load fundamentals for ${symbol}:`, err);
  }
}

function formatQuarterLabel(dateStr) {
  if (!dateStr || dateStr.length < 7) return "";
  const year = dateStr.slice(2, 4);
  const month = parseInt(dateStr.slice(5, 7), 10);
  if (month <= 3) return `Q4'${year}`;
  if (month <= 6) return `Q1'${year}`;
  if (month <= 9) return `Q2'${year}`;
  return `Q3'${year}`;
}

function renderFinancialCharts(funds) {
  if (!el.revenueChartSvg || !el.profitChartSvg) return;

  if (!funds || funds.length === 0) {
    const emptyMsg = `<div style="font-size: 11px; color: var(--text-muted); display:flex; align-items:center; justify-content:center; height:100%;">No quarterly statements available.</div>`;
    el.revenueChartSvg.innerHTML = emptyMsg;
    el.profitChartSvg.innerHTML = emptyMsg;
    return;
  }

  // Sort chronological (oldest to newest), taking last 5 quarters
  const quarters = [...funds].reverse().slice(-5);

  // 1. Quarterly Revenue Bar Chart (SVG)
  renderRevenueSvg(quarters);

  // 2. Net Profit (PAT) and Margin Chart (SVG)
  renderProfitMarginSvg(quarters);
}

function renderRevenueSvg(quarters) {
  const width = 360;
  const height = 150;
  const padLeft = 45;
  const padRight = 15;
  const padTop = 20;
  const padBottom = 25;

  const chartW = width - padLeft - padRight;
  const chartH = height - padTop - padBottom;

  const revenues = quarters.map(q => q.revenue_cr);
  const maxRev = Math.max(...revenues, 1) * 1.15;

  const n = quarters.length;
  const slotW = chartW / n;
  const barW = Math.min(36, slotW * 0.55);

  let svgHtml = `<svg viewBox="0 0 ${width} ${height}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="revBarGrad" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stop-color="#387ED1" stop-opacity="0.9"/>
        <stop offset="100%" stop-color="#1E40AF" stop-opacity="0.6"/>
      </linearGradient>
    </defs>
    <!-- Gridlines & Y-Axis -->
    <line x1="${padLeft}" y1="${padTop}" x2="${width - padRight}" y2="${padTop}" stroke="var(--border-color)" stroke-dasharray="3,3"/>
    <line x1="${padLeft}" y1="${padTop + chartH / 2}" x2="${width - padRight}" y2="${padTop + chartH / 2}" stroke="var(--border-color)" stroke-dasharray="3,3"/>
    <line x1="${padLeft}" y1="${padTop + chartH}" x2="${width - padRight}" y2="${padTop + chartH}" stroke="var(--border-color)"/>
    <text x="${padLeft - 6}" y="${padTop + 4}" fill="var(--text-muted)" font-size="9" text-anchor="end">₹${Math.round(maxRev / 1000)}k</text>
    <text x="${padLeft - 6}" y="${padTop + chartH / 2 + 3}" fill="var(--text-muted)" font-size="9" text-anchor="end">₹${Math.round(maxRev / 2000)}k</text>
    <text x="${padLeft - 6}" y="${padTop + chartH + 3}" fill="var(--text-muted)" font-size="9" text-anchor="end">0</text>
  `;

  quarters.forEach((q, i) => {
    const xCenter = padLeft + i * slotW + slotW / 2;
    const barX = xCenter - barW / 2;
    const barHeight = Math.max(3, (q.revenue_cr / maxRev) * chartH);
    const barY = padTop + chartH - barHeight;
    const qLabel = formatQuarterLabel(q.period_end_date);
    const revText = q.revenue_cr >= 10000 
      ? `₹${(q.revenue_cr / 1000).toFixed(0)}k` 
      : `₹${Math.round(q.revenue_cr)}`;

    svgHtml += `
      <rect x="${barX}" y="${barY}" width="${barW}" height="${barHeight}" rx="4" fill="url(#revBarGrad)" stroke="#387ED1" stroke-width="1"/>
      <text x="${xCenter}" y="${barY - 4}" fill="var(--text-primary)" font-size="9" font-weight="600" text-anchor="middle">${revText}</text>
      <text x="${xCenter}" y="${height - 8}" fill="var(--text-secondary)" font-size="9" text-anchor="middle">${qLabel}</text>
    `;
  });

  svgHtml += `</svg>`;
  el.revenueChartSvg.innerHTML = svgHtml;
}

function renderProfitMarginSvg(quarters) {
  const width = 360;
  const height = 150;
  const padLeft = 45;
  const padRight = 35;
  const padTop = 22;
  const padBottom = 25;

  const chartW = width - padLeft - padRight;
  const chartH = height - padTop - padBottom;

  const pats = quarters.map(q => q.pat_cr);
  const margins = quarters.map(q => q.ebitda_margin_pct);

  const maxPat = Math.max(...pats, 100) * 1.2;
  const maxMargin = Math.max(...margins, 10) * 1.25;

  const n = quarters.length;
  const slotW = chartW / n;
  const barW = Math.min(28, slotW * 0.45);

  let svgHtml = `<svg viewBox="0 0 ${width} ${height}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="patGreenGrad" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stop-color="#00D09C" stop-opacity="0.9"/>
        <stop offset="100%" stop-color="#008F6B" stop-opacity="0.6"/>
      </linearGradient>
      <linearGradient id="patRedGrad" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stop-color="#EB5757" stop-opacity="0.9"/>
        <stop offset="100%" stop-color="#991B1B" stop-opacity="0.6"/>
      </linearGradient>
    </defs>
    <!-- Axis lines -->
    <line x1="${padLeft}" y1="${padTop}" x2="${width - padRight}" y2="${padTop}" stroke="var(--border-color)" stroke-dasharray="3,3"/>
    <line x1="${padLeft}" y1="${padTop + chartH / 2}" x2="${width - padRight}" y2="${padTop + chartH / 2}" stroke="var(--border-color)" stroke-dasharray="3,3"/>
    <line x1="${padLeft}" y1="${padTop + chartH}" x2="${width - padRight}" y2="${padTop + chartH}" stroke="var(--border-color)"/>
    <text x="${padLeft - 6}" y="${padTop + 4}" fill="var(--text-muted)" font-size="9" text-anchor="end">₹${Math.round(maxPat)}</text>
    <text x="${padLeft - 6}" y="${padTop + chartH + 3}" fill="var(--text-muted)" font-size="9" text-anchor="end">0</text>
    <text x="${width - padRight + 6}" y="${padTop + 4}" fill="#00F0FF" font-size="9" text-anchor="start">${maxMargin.toFixed(0)}%</text>
  `;

  // Draw PAT Bars
  quarters.forEach((q, i) => {
    const xCenter = padLeft + i * slotW + slotW / 2;
    const barX = xCenter - barW / 2;
    const barHeight = Math.max(3, (Math.max(0, q.pat_cr) / maxPat) * chartH);
    const barY = padTop + chartH - barHeight;
    const qLabel = formatQuarterLabel(q.period_end_date);
    const patFill = q.pat_cr >= 0 ? "url(#patGreenGrad)" : "url(#patRedGrad)";
    const patStroke = q.pat_cr >= 0 ? "#00D09C" : "#EB5757";

    svgHtml += `
      <rect x="${barX}" y="${barY}" width="${barW}" height="${barHeight}" rx="3" fill="${patFill}" stroke="${patStroke}" stroke-width="1"/>
      <text x="${xCenter}" y="${height - 8}" fill="var(--text-secondary)" font-size="9" text-anchor="middle">${qLabel}</text>
    `;
  });

  // Draw EBITDA Margin Line and Points
  const marginPoints = quarters.map((q, i) => {
    const x = padLeft + i * slotW + slotW / 2;
    const y = padTop + chartH - (q.ebitda_margin_pct / maxMargin) * chartH;
    return { x, y, val: q.ebitda_margin_pct };
  });

  const pathD = marginPoints.map((pt, i) => `${i === 0 ? "M" : "L"} ${pt.x.toFixed(1)} ${pt.y.toFixed(1)}`).join(" ");
  svgHtml += `<path d="${pathD}" fill="none" stroke="#00F0FF" stroke-width="2" stroke-linecap="round"/>`;

  marginPoints.forEach(pt => {
    svgHtml += `
      <circle cx="${pt.x.toFixed(1)}" cy="${pt.y.toFixed(1)}" r="3.5" fill="#0C1017" stroke="#00F0FF" stroke-width="2"/>
      <text x="${pt.x.toFixed(1)}" y="${(pt.y - 6).toFixed(1)}" fill="#00F0FF" font-size="8.5" font-weight="700" text-anchor="middle">${pt.val.toFixed(1)}%</text>
    `;
  });

  svgHtml += `</svg>`;
  el.profitChartSvg.innerHTML = svgHtml;
}

// -------------------------------------------------------------
// Announcements & Corporate Filings Render
// -------------------------------------------------------------

function renderAnnouncements(items) {
  if (!el.announcementsContainer) return;
  el.announcementsContainer.innerHTML = "";
  if (!items || items.length === 0) {
    el.announcementsContainer.innerHTML = `<div style="font-size: 12px; color: var(--text-muted); padding: 8px 0;">No high-materiality filings detected.</div>`;
    return;
  }

  // Prioritize active stock's filings if available, else show top recent market filings
  const stockFilings = items.filter(a => a.symbol === state.activeSymbol);
  const displayItems = stockFilings.length > 0 ? stockFilings : items.slice(0, 6);

  displayItems.forEach(item => {
    let extraBadge = "";
    if (item.extracted_data && item.extracted_data.contract_amount_cr) {
      extraBadge = `<div class="ann-extra-badge">Order Value: ₹${item.extracted_data.contract_amount_cr} Cr</div>`;
    } else if (item.extracted_data && item.extracted_data.pledge_change_pct) {
      extraBadge = `<div class="ann-extra-badge" style="color: var(--groww-amber); background: var(--groww-amber-bg);">Pledge Change: ${item.extracted_data.pledge_change_pct}%</div>`;
    }

    const isMatch = item.symbol === state.activeSymbol;
    const borderStyle = isMatch ? "border-left: 3px solid var(--groww-green);" : "";

    const div = document.createElement("div");
    div.className = "ann-card-item";
    div.style = borderStyle;
    div.innerHTML = `
      <div class="ann-card-top">
        <span class="ann-category-pill" style="${isMatch ? 'background: var(--groww-green-bg); color: var(--groww-green);' : ''}">${item.symbol} • ${item.event_type || item.category}</span>
        <span style="font-size: 10px; color: var(--text-muted);">${item.announcement_timestamp.slice(0, 10)}</span>
      </div>
      <div class="ann-headline-text">${item.headline}</div>
      ${extraBadge}
    `;
    el.announcementsContainer.appendChild(div);
  });
}

// -------------------------------------------------------------
// AI Advice & Target Hit History (Verifiable Track Record)
// -------------------------------------------------------------

async function loadAdviceHistory(symbol) {
  try {
    const res = await fetch(`/api/v1/stocks/${symbol}/advice-history`);
    const data = await res.json();
    state.adviceHistory = data;
    renderAdviceHistory(data);
  } catch (err) {
    console.error(`Failed to load advice history for ${symbol}:`, err);
  }
}

function renderAdviceHistory(data) {
  if (!el.adviceListContainer) return;
  el.adviceListContainer.innerHTML = "";

  if (el.adviceStockLabel) {
    el.adviceStockLabel.textContent = `Verifiable trade recommendations & realized outcomes for ${data.symbol}`;
  }

  // Update track record metrics
  const s = data.summary;
  if (s) {
    if (el.statHitRate) el.statHitRate.textContent = `${s.hit_rate_pct.toFixed(1)}%`;
    if (el.statHitFraction) el.statHitFraction.textContent = `${s.targets_hit} of ${s.completed_calls} Targets Achieved`;
    if (el.statAvgReturn) {
      const sign = s.avg_return_pct >= 0 ? "+" : "";
      el.statAvgReturn.textContent = `${sign}${s.avg_return_pct.toFixed(1)}%`;
      el.statAvgReturn.style.color = s.avg_return_pct >= 0 ? "var(--groww-green)" : "var(--groww-red)";
    }
    if (el.statAvgDuration) el.statAvgDuration.textContent = `${s.avg_days} Days`;
    if (el.statProfitFactor) el.statProfitFactor.textContent = `${s.profit_factor.toFixed(1)}x`;
  }

  const calls = data.calls || [];
  if (calls.length === 0) {
    el.adviceListContainer.innerHTML = `<div style="font-size: 12px; color: var(--text-muted); padding: 12px 0;">No advisory episodes logged for this asset.</div>`;
    return;
  }

  calls.forEach(c => {
    let cardClass = "advice-card-item";
    let statusClass = "status-target-hit";
    let statusIcon = "🎯";

    if (c.status.includes("TARGET HIT")) {
      cardClass += " is-hit";
      statusClass = "status-target-hit";
      statusIcon = "✅";
    } else if (c.status.includes("ACTIVE")) {
      cardClass += " is-active";
      statusClass = "status-active-call";
      statusIcon = "⏳";
    } else if (c.status.includes("STOP-LOSS")) {
      cardClass += " is-stop";
      statusClass = "status-stop-hit";
      statusIcon = "🛡️";
    } else {
      cardClass += " is-hit";
      statusClass = "status-profit-booked";
      statusIcon = "💰";
    }

    const retSign = c.realized_return_pct >= 0 ? "+" : "";
    const retColor = c.realized_return_pct >= 0 ? "var(--groww-green)" : "var(--groww-red)";

    const div = document.createElement("div");
    div.className = cardClass;
    div.innerHTML = `
      <div class="advice-card-top">
        <div class="advice-badge-group">
          <span class="advice-action-pill">${c.action}</span>
          <span class="advice-date-pill">Issued on ${c.advice_date}</span>
        </div>
        <div class="advice-status-tag ${statusClass}">
          <span>${statusIcon}</span>
          <span>${c.status}</span>
        </div>
      </div>

      <div class="advice-grid-cols">
        <div class="advice-col">
          <span class="advice-col-label">Entry Advice Price</span>
          <span class="advice-col-val">₹${c.entry_price.toLocaleString("en-IN", { minimumFractionDigits: 2 })}</span>
        </div>
        <div class="advice-col">
          <span class="advice-col-label">Target Projected</span>
          <span class="advice-col-val" style="color: var(--groww-green);">₹${c.target_price.toLocaleString("en-IN", { minimumFractionDigits: 2 })} (+${c.projected_return_pct}%)</span>
        </div>
        <div class="advice-col">
          <span class="advice-col-label">Stop-Loss Level</span>
          <span class="advice-col-val" style="color: var(--groww-red);">₹${c.stop_loss_price.toLocaleString("en-IN", { minimumFractionDigits: 2 })}</span>
        </div>
        <div class="advice-col">
          <span class="advice-col-label">Realized Outcome</span>
          <span class="advice-col-val" style="color: ${retColor};">${retSign}${c.realized_return_pct.toFixed(2)}%</span>
        </div>
        <div class="advice-col">
          <span class="advice-col-label">Time to Target</span>
          <span class="advice-col-val">${c.duration_days} Days</span>
        </div>
      </div>

      <div class="advice-rationale-row">
        <span style="color: var(--text-muted); font-size: 10px; font-weight: 700; text-transform: uppercase;">AI Thesis:</span>
        <span>${c.ai_rationale}</span>
        <span style="margin-left: auto; color: var(--text-muted); font-size: 10px;">${c.target_hit_date.includes("Projected") ? c.target_hit_date : 'Completed: ' + c.target_hit_date}</span>
      </div>
    `;
    el.adviceListContainer.appendChild(div);
  });
}

// -------------------------------------------------------------
// Cytoscape.js Supply Chain Graph Rendering
// -------------------------------------------------------------

async function loadGraphData(symbol) {
  try {
    const res = await fetch(`/api/v1/stocks/${symbol}/ontology`);
    const data = await res.json();
    renderCytoscape(data);
  } catch (err) {
    console.error(`Failed to load graph ontology for ${symbol}:`, err);
  }
}

function renderCytoscape(data) {
  if (!window.cytoscape || !el.cyContainer) {
    console.error("Cytoscape.js library not found or container missing.");
    return;
  }

  const isDark = state.theme === "dark";
  const elements = [];

  // Nodes
  data.nodes.forEach(n => {
    let nodeColor = "#00D09C";
    let nodeShape = "ellipse";
    let size = 36;

    if (n.type === "Sector") {
      nodeColor = "#8B5CF6";
      nodeShape = "diamond";
      size = 44;
    } else if (n.type === "Conglomerate") {
      nodeColor = "#F59E0B";
      nodeShape = "hexagon";
      size = 48;
    } else if (n.type === "MacroVariable") {
      nodeColor = "#EB5757";
      nodeShape = "triangle";
      size = 40;
    }

    if (n.id === state.activeSymbol) {
      nodeColor = "#00D09C";
      size = 54;
    }

    elements.push({
      group: "nodes",
      data: {
        id: n.id,
        label: n.label || n.id,
        type: n.type,
        color: nodeColor,
        shape: nodeShape,
        size: size,
        isActive: n.id === state.activeSymbol
      }
    });
  });

  // Edges
  data.edges.forEach((e, idx) => {
    let edgeColor = isDark ? "#334155" : "#CBD5E1";
    let label = e.relationship;

    if (e.elasticity !== null && e.elasticity !== undefined) {
      const elast = Number(e.elasticity);
      label = `${elast > 0 ? "+" : ""}${elast}% marg`;
      edgeColor = elast < 0 ? "#EB5757" : "#00D09C";
    }

    elements.push({
      group: "edges",
      data: {
        id: `e_${idx}`,
        source: e.source,
        target: e.target,
        label: label,
        color: edgeColor
      }
    });
  });

  if (state.cy) {
    state.cy.destroy();
  }

  state.cy = cytoscape({
    container: el.cyContainer,
    elements: elements,
    style: [
      {
        selector: "node",
        style: {
          "background-color": isDark ? "#151B26" : "#FFFFFF",
          "border-color": "data(color)",
          "border-width": 2.5,
          "shape": "data(shape)",
          "width": "data(size)",
          "height": "data(size)",
          "label": "data(label)",
          "color": isDark ? "#FFFFFF" : "#1A202C",
          "font-family": "'Inter', -apple-system, sans-serif",
          "font-size": "11px",
          "font-weight": 600,
          "text-valign": "bottom",
          "text-margin-y": 6,
          "text-background-color": isDark ? "#0C1017" : "#FFFFFF",
          "text-background-opacity": 0.8,
          "text-background-padding": 3,
          "text-background-shape": "roundrectangle"
        }
      },
      {
        selector: "node[?isActive]",
        style: {
          "border-color": "#00D09C",
          "border-width": 4,
          "shadow-blur": 12,
          "shadow-color": "#00D09C",
          "shadow-opacity": 0.6
        }
      },
      {
        selector: "edge",
        style: {
          "width": 2,
          "line-color": "data(color)",
          "target-arrow-color": "data(color)",
          "target-arrow-shape": "triangle",
          "curve-style": "bezier",
          "label": "data(label)",
          "color": isDark ? "#94A3B8" : "#64748B",
          "font-family": "'Inter', -apple-system, sans-serif",
          "font-size": "9px",
          "text-background-color": isDark ? "#0C1017" : "#FFFFFF",
          "text-background-opacity": 0.9,
          "text-background-padding": 2
        }
      }
    ],
    layout: {
      name: "cose",
      animate: true,
      randomize: false,
      componentSpacing: 90,
      nodeRepulsion: 300000
    }
  });

  state.cy.on("tap", "node", evt => {
    const clickedId = evt.target.data("id");
    const exists = state.universeSummary.some(s => s.symbol === clickedId);
    if (exists && clickedId !== state.activeSymbol) {
      selectStock(clickedId);
    }
  });
}

// =============================================================
// CRICKET AI INTELLIGENCE & SEGMENT MANAGEMENT
// =============================================================

const TEAM_META = {
  "IND": {
    flagSvg: `<svg viewBox="0 0 36 36" class="flag-svg-badge"><rect width="36" height="36" rx="18" fill="#FFFFFF"/><rect width="36" height="12" fill="#FF9933"/><rect y="24" width="36" height="12" fill="#138808"/><circle cx="18" cy="18" r="4.5" fill="none" stroke="#000080" stroke-width="1.2"/><circle cx="18" cy="18" r="1.5" fill="#000080"/></svg>`,
    name: "India",
    color: "#00D09C"
  },
  "AUS": {
    flagSvg: `<svg viewBox="0 0 36 36" class="flag-svg-badge"><rect width="36" height="36" rx="18" fill="#00008B"/><rect width="18" height="18" fill="#00247D"/><path d="M0,0 L18,18 M18,0 L0,18" stroke="#FFFFFF" stroke-width="2.5"/><path d="M0,0 L18,18 M18,0 L0,18" stroke="#CF142B" stroke-width="1.2"/><path d="M9,0 L9,18 M0,9 L18,9" stroke="#FFFFFF" stroke-width="3.5"/><path d="M9,0 L9,18 M0,9 L18,9" stroke="#CF142B" stroke-width="2"/><circle cx="27" cy="10" r="1.5" fill="#FFFFFF"/><circle cx="29" cy="18" r="1.5" fill="#FFFFFF"/><circle cx="24" cy="22" r="1.5" fill="#FFFFFF"/><circle cx="27" cy="28" r="1.5" fill="#FFFFFF"/><circle cx="9" cy="27" r="2.5" fill="#FFFFFF"/></svg>`,
    name: "Australia",
    color: "#FFB000"
  },
  "ENG": {
    flagSvg: `<svg viewBox="0 0 36 36" class="flag-svg-badge"><rect width="36" height="36" rx="18" fill="#FFFFFF"/><rect x="15" width="6" height="36" fill="#CE1124"/><rect y="15" width="36" height="6" fill="#CE1124"/></svg>`,
    name: "England",
    color: "#00F0FF"
  },
  "SA": {
    flagSvg: `<svg viewBox="0 0 36 36" class="flag-svg-badge"><rect width="36" height="36" rx="18" fill="#007749"/><path d="M0,0 L36,0 L36,12 L16,12 L0,0 Z" fill="#E03C31"/><path d="M0,36 L36,36 L36,24 L16,24 L0,36 Z" fill="#001489"/><polygon points="0,0 16,18 0,36" fill="#000000"/><polygon points="0,0 12,18 0,36" fill="#FFB612"/></svg>`,
    name: "South Africa",
    color: "#00D09C"
  },
  "NZ": {
    flagSvg: `<svg viewBox="0 0 36 36" class="flag-svg-badge"><rect width="36" height="36" rx="18" fill="#00247D"/><circle cx="27" cy="10" r="1.8" fill="#CC142B" stroke="#FFFFFF" stroke-width="0.8"/><circle cx="29" cy="18" r="1.8" fill="#CC142B" stroke="#FFFFFF" stroke-width="0.8"/><circle cx="24" cy="22" r="1.8" fill="#CC142B" stroke="#FFFFFF" stroke-width="0.8"/><circle cx="27" cy="28" r="1.8" fill="#CC142B" stroke="#FFFFFF" stroke-width="0.8"/></svg>`,
    name: "New Zealand",
    color: "#8E8EA0"
  },
  "PAK": {
    flagSvg: `<svg viewBox="0 0 36 36" class="flag-svg-badge"><rect width="36" height="36" rx="18" fill="#01411C"/><rect width="9" height="36" fill="#FFFFFF"/><circle cx="21" cy="18" r="8.5" fill="#FFFFFF"/><circle cx="23" cy="17" r="7.5" fill="#01411C"/><polygon points="23,12 24.5,15 28,15 25,17 26.5,20 23,18 19.5,20 21,17 18,15 21.5,15" fill="#FFFFFF"/></svg>`,
    name: "Pakistan",
    color: "#00D09C"
  },
  "WI": {
    flagSvg: `<svg viewBox="0 0 36 36" class="flag-svg-badge"><rect width="36" height="36" rx="18" fill="#7B0041"/><circle cx="18" cy="18" r="11" fill="#FFC72C"/><path d="M18,9 L20,17 L16,17 Z" fill="#005A36"/><circle cx="18" cy="22" r="3.5" fill="#FFFFFF"/></svg>`,
    name: "West Indies",
    color: "#9B51E0"
  },
  "SL": {
    flagSvg: `<svg viewBox="0 0 36 36" class="flag-svg-badge"><rect width="36" height="36" rx="18" fill="#FFBE29"/><rect x="3" y="3" width="7" height="30" fill="#005A36"/><rect x="10" y="3" width="7" height="30" fill="#FF7900"/><rect x="17" y="3" width="16" height="30" fill="#8D153A"/><circle cx="25" cy="18" r="5" fill="#FFBE29"/></svg>`,
    name: "Sri Lanka",
    color: "#0070F3"
  },
  "AFG": {
    flagSvg: `<svg viewBox="0 0 36 36" class="flag-svg-badge"><rect width="36" height="36" rx="18" fill="#FFFFFF"/><rect width="12" height="36" fill="#000000"/><rect x="12" width="12" height="36" fill="#D32011"/><rect x="24" width="12" height="36" fill="#007A3D"/><circle cx="18" cy="18" r="5" fill="#FFFFFF"/></svg>`,
    name: "Afghanistan",
    color: "#00F0FF"
  },
  "BAN": {
    flagSvg: `<svg viewBox="0 0 36 36" class="flag-svg-badge"><rect width="36" height="36" rx="18" fill="#006A4E"/><circle cx="16" cy="18" r="7.5" fill="#F42A41"/></svg>`,
    name: "Bangladesh",
    color: "#00D09C"
  }
};

let cricketLiveStreamInterval = null;

function startCricketLiveStream() {
  if (cricketLiveStreamInterval) clearInterval(cricketLiveStreamInterval);
  cricketLiveStreamInterval = setInterval(async () => {
    if (state.activeSegment === "cricket" && state.activeCricketMatchId) {
      try {
        const res = await fetch(`/api/v1/cricket/match/${state.activeCricketMatchId}/prediction`);
        if (res.ok) {
          const pred = await res.json();
          renderCricketMatchDetails(pred);

          // Dynamically synchronize active match card in sidebar without layout flicker
          const activeCard = document.querySelector(`.cricket-match-card[data-match-id="${state.activeCricketMatchId}"]`);
          if (activeCard && pred.fixture) {
            const footerSpans = activeCard.querySelectorAll(".cricket-card-footer span");
            if (footerSpans.length >= 2) {
              if (pred.fixture.live_score_a) footerSpans[0].textContent = pred.fixture.live_score_a;
              if (pred.fixture.live_session) {
                const s = pred.fixture.live_session;
                footerSpans[1].textContent = s.toLowerCase().includes("break") ? "Break" : s.split("(")[0].trim();
              }
            }
          }
        }
      } catch (err) {}
    }
  }, 4000);
}

function stopCricketLiveStream() {
  if (cricketLiveStreamInterval) {
    clearInterval(cricketLiveStreamInterval);
    cricketLiveStreamInterval = null;
  }
}

function switchSegment(segment) {
  state.activeSegment = segment;
  if (segment === "cricket") {
    if (el.segBtnMarkets) el.segBtnMarkets.classList.remove("active");
    if (el.segBtnCricket) el.segBtnCricket.classList.add("active");
    if (el.marketsWatchlistContainer) el.marketsWatchlistContainer.style.display = "none";
    if (el.cricketWatchlistContainer) el.cricketWatchlistContainer.style.display = "flex";
    if (el.marketsWorkspaceContainer) el.marketsWorkspaceContainer.style.display = "none";
    if (el.cricketWorkspaceContainer) el.cricketWorkspaceContainer.style.display = "flex";
    if (el.searchInput) {
      el.searchInput.placeholder = "Search cricket matches, teams (IND, AUS), venues...";
      el.searchInput.value = state.cricketSearchQuery || "";
    }
    loadCricketFixtures();
    loadCricketBrainTrackRecord();
    startCricketLiveStream();
  } else {
    stopCricketLiveStream();
    if (el.segBtnMarkets) el.segBtnMarkets.classList.add("active");
    if (el.segBtnCricket) el.segBtnCricket.classList.remove("active");
    if (el.marketsWatchlistContainer) el.marketsWatchlistContainer.style.display = "flex";
    if (el.cricketWatchlistContainer) el.cricketWatchlistContainer.style.display = "none";
    if (el.marketsWorkspaceContainer) el.marketsWorkspaceContainer.style.display = "flex";
    if (el.cricketWorkspaceContainer) el.cricketWorkspaceContainer.style.display = "none";
    if (el.searchInput) {
      el.searchInput.placeholder = "Search 50 stocks by name or sector...";
      el.searchInput.value = state.searchQuery || "";
    }
    if (state.chart && el.chartContainer && el.chartContainer.clientWidth > 0) {
      state.chart.applyOptions({
        width: el.chartContainer.clientWidth,
        height: el.chartContainer.clientHeight || 440
      });
      state.chart.timeScale().fitContent();
    }
  }
}

async function loadCricketFixtures() {
  try {
    const res = await fetch("/api/v1/cricket/fixtures");
    if (!res.ok) throw new Error("Failed to load cricket fixtures");
    state.cricketFixtures = await res.json();
    filterAndRenderCricketMatches();

    if (state.cricketFixtures.length > 0) {
      const matchExists = state.cricketFixtures.some(f => f.match_id === state.activeCricketMatchId);
      const targetId = matchExists ? state.activeCricketMatchId : state.cricketFixtures[0].match_id;
      selectCricketMatch(targetId);
    }
  } catch (err) {
    console.error("[Cricket AI] Error loading fixtures:", err);
  }
}

function filterAndRenderCricketMatches() {
  if (!el.cricketMatchList) return;

  let matches = [...state.cricketFixtures];

  if (state.activeCricketFormat !== "ALL") {
    matches = matches.filter(m => (m.format || "").toUpperCase() === state.activeCricketFormat.toUpperCase());
  }

  if (state.cricketSearchQuery) {
    const q = state.cricketSearchQuery.toLowerCase();
    matches = matches.filter(m => {
      const teamA = (TEAM_META[m.team_a]?.name || m.team_a || "").toLowerCase();
      const teamB = (TEAM_META[m.team_b]?.name || m.team_b || "").toLowerCase();
      const series = (m.series_name || "").toLowerCase();
      const venue = (m.venue_id || "").toLowerCase();
      return m.team_a.toLowerCase().includes(q) ||
             m.team_b.toLowerCase().includes(q) ||
             teamA.includes(q) ||
             teamB.includes(q) ||
             series.includes(q) ||
             venue.includes(q);
    });
  }

  state.filteredCricketFixtures = matches;
  if (el.cricketCountLabel) {
    el.cricketCountLabel.textContent = `${matches.length} Matches`;
  }

  if (matches.length === 0) {
    el.cricketMatchList.innerHTML = `<li style="padding: 24px; text-align: center; color: var(--text-muted); font-size: 12px;">No matches found matching filter.</li>`;
    return;
  }

  el.cricketMatchList.innerHTML = "";
  matches.forEach(m => {
    const isLive = m.status === "LIVE";
    const isUpcoming = m.status === "UPCOMING";
    const isActive = m.match_id === state.activeCricketMatchId;

    const flagA = TEAM_META[m.team_a]?.flagSvg || `<span style="font-weight:700">${m.team_a}</span>`;
    const flagB = TEAM_META[m.team_b]?.flagSvg || `<span style="font-weight:700">${m.team_b}</span>`;
    const nameA = TEAM_META[m.team_a]?.name || m.team_a;
    const nameB = TEAM_META[m.team_b]?.name || m.team_b;

    let statusPill = "";
    if (isLive) {
      statusPill = `<span class="status-live-pill"><span class="live-pulse-dot"></span>LIVE</span>`;
    } else if (isUpcoming) {
      statusPill = `<span class="status-upcoming-pill">UPCOMING</span>`;
    } else {
      statusPill = `<span class="status-upcoming-pill" style="background: rgba(142, 142, 160, 0.15); color: var(--text-muted);">FINAL</span>`;
    }

    let leftScoreText = m.match_time_ist;
    let rightInfoText = m.venue_id || "Intl Stadium";
    if (isLive) {
      leftScoreText = m.live_score_a || "Match in Progress";
      rightInfoText = m.live_session ? m.live_session.split("(")[0].trim() : (m.live_overs ? `${m.live_overs} ov` : "LIVE");
    }

    const li = document.createElement("li");
    li.className = `cricket-match-card ${isActive ? "active" : ""}`;
    li.dataset.matchId = m.match_id;
    li.innerHTML = `
      <div class="cricket-card-header">
        <span class="cricket-series-tag">${m.series_name || "ICC Bilateral"}</span>
        <div style="display: flex; align-items: center; gap: 6px;">
          <span class="format-badge format-${(m.format || "t20i").toLowerCase()}">${m.format}</span>
          ${statusPill}
        </div>
      </div>
      <div class="cricket-teams-row">
        <div class="team-cell" style="display: flex; align-items: center; gap: 8px;">
          <div class="team-flag-avatar">${flagA}</div>
          <span class="team-fullname" style="font-size: 13px; font-weight: 700; color: var(--text-primary);">${nameA}</span>
        </div>
        <div class="vs-center-tag">VS</div>
        <div class="team-cell" style="display: flex; align-items: center; justify-content: flex-end; gap: 8px;">
          <span class="team-fullname" style="font-size: 13px; font-weight: 700; color: var(--text-primary);">${nameB}</span>
          <div class="team-flag-avatar">${flagB}</div>
        </div>
      </div>
      <div class="cricket-card-footer">
        <span style="color: var(--text-secondary); font-size: 11px;">${leftScoreText}</span>
        <span style="color: var(--groww-green); font-size: 11px; font-weight: 700;">${rightInfoText}</span>
      </div>
    `;

    li.addEventListener("click", () => {
      selectCricketMatch(m.match_id);
    });

    el.cricketMatchList.appendChild(li);
  });
}

async function selectCricketMatch(matchId) {
  state.activeCricketMatchId = matchId;

  document.querySelectorAll(".cricket-match-card").forEach(c => {
    c.classList.toggle("active", c.dataset.matchId === matchId);
  });

  try {
    const res = await fetch(`/api/v1/cricket/match/${matchId}/prediction`);
    if (!res.ok) throw new Error("Failed to load match prediction");
    const pred = await res.json();
    state.activeCricketPrediction = pred;

    renderCricketMatchDetails(pred);
  } catch (err) {
    console.error("[Cricket AI] Error selecting match:", err);
  }
}

function renderCricketMatchDetails(pred) {
  if (!pred || pred.error) return;

  const fix = pred.fixture || {};
  const teamA = pred.team_a || {};
  const teamB = pred.team_b || {};
  const venue = pred.venue || {};
  const probA = pred.win_probability_team_a_pct || 50.0;
  const probB = pred.win_probability_team_b_pct || 50.0;
  const winner = pred.predicted_winner_name || "Tie/Equal";
  const conf = pred.prediction_confidence_pct || 80.0;

  const flagA = TEAM_META[teamA.code]?.flagSvg || `<div style="font-weight:900;">${teamA.code}</div>`;
  const flagB = TEAM_META[teamB.code]?.flagSvg || `<div style="font-weight:900;">${teamB.code}</div>`;
  const nameA = TEAM_META[teamA.code]?.name || teamA.name || teamA.code;
  const nameB = TEAM_META[teamB.code]?.name || teamB.name || teamB.code;

  // 1. Hero Banner Top Row
  if (el.cricketAvatarA) el.cricketAvatarA.innerHTML = flagA;
  if (el.cricketAvatarB) el.cricketAvatarB.innerHTML = flagB;
  if (el.cricketSeriesTitle) el.cricketSeriesTitle.textContent = pred.series_name || "International Cricket Series";
  if (el.cricketFormatBadge) el.cricketFormatBadge.textContent = pred.format || "T20I";
  if (el.cricketVenueText) el.cricketVenueText.textContent = `${venue.name || fix.venue_id}, ${venue.city || ""}`;
  const isLive = pred.status === "LIVE";
  const sessionRaw = String(fix.live_session || "");
  const isBreak = sessionRaw.toLowerCase().includes("break") || String(pred.live_session || "").toLowerCase().includes("break");

  if (el.cricketTimeText) {
    if (pred.match_id === "LIVE-SL-PAK-01" || (isLive && pred.format === "TEST")) {
      el.cricketTimeText.textContent = isBreak ? "17–21 Nov • Break" : "17–21 Nov • Day 1 (Session 2)";
    } else {
      const cleanDate = (pred.match_date || "").split("T")[0];
      el.cricketTimeText.textContent = `${cleanDate} • ${pred.match_time_ist || "Today"}`;
    }
  }

  if (el.cricketStatusPill) {
    el.cricketStatusPill.className = isLive ? "status-live-pill" : (pred.status === "COMPLETED" ? "status-completed-pill" : "status-upcoming-pill");
    const sessionLabel = isBreak ? "Break" : (fix.live_session || (isLive ? "LIVE MATCH" : pred.status));
    el.cricketStatusPill.innerHTML = isLive ? `<span class="live-pulse-dot"></span><span>${sessionLabel}</span>` : `<span>${sessionLabel}</span>`;
  }

  // 2. Dual Team Scorecard Grid
  if (el.cricketTeamNameA) el.cricketTeamNameA.textContent = nameA;
  if (el.cricketTeamNameB) el.cricketTeamNameB.textContent = nameB;

  const scoreA = fix.live_score_a || "--";
  const scoreB = fix.live_score_b || (isLive ? "Yet to bat" : "--");

  if (el.cricketScoreValA) {
    if (scoreA.includes("(")) {
      const parts = scoreA.split("(");
      el.cricketScoreValA.textContent = parts[0].trim();
      if (el.cricketOversValA) {
        const ov = parts[1].replace(")", "").replace("ov", "").trim();
        el.cricketOversValA.textContent = `(${ov}) • 1st`;
      }
    } else {
      el.cricketScoreValA.textContent = scoreA;
      if (el.cricketOversValA) {
        const ov = (fix.live_overs && fix.live_overs !== "--") ? fix.live_overs.replace("ov", "").trim() : "";
        el.cricketOversValA.textContent = ov ? `(${ov}) • 1st` : "• 1st";
      }
    }
  }

  if (el.cricketScoreValB) {
    el.cricketScoreValB.textContent = scoreB;
    if (el.cricketOversValB) {
      el.cricketOversValB.textContent = isLive && scoreB.toLowerCase().includes("yet") ? "1st Innings" : (fix.live_overs && fix.live_overs !== "--" ? `(${fix.live_overs} ov)` : "");
    }
  }

  if (el.cricketSessionBadge) {
    el.cricketSessionBadge.textContent = isBreak ? "Day 1 • Innings Break" : (fix.live_session ? fix.live_session.split("(")[0].trim() : (isLive ? "Day 1 • In Play" : pred.status));
  }

  // 3. Toss Information
  if (el.cricketTossInfo) {
    el.cricketTossInfo.textContent = fix.live_summary || (fix.toss_winner ? `${TEAM_META[fix.toss_winner]?.name || fix.toss_winner} elected to ${fix.toss_decision ? fix.toss_decision.toLowerCase() : "bowl"} first` : "Toss scheduled before match");
  }

  // 4. Live In-Play Stats Strip (Batting & Bowling)
  if (el.cricketLiveStatsStrip) {
    if (isLive && pred.live_batting && pred.live_bowling) {
      el.cricketLiveStatsStrip.style.display = "grid";
      if (el.cricketBattingHeader) el.cricketBattingHeader.innerHTML = `<span>🏏 ${teamA.code} BATTING</span>`;
      if (el.cricketBowlingHeader) el.cricketBowlingHeader.innerHTML = `<span>🎯 ${teamB.code} BOWLING</span>`;

      const parsePlayerStat = (str) => {
        if (!str) return { name: "--", stat: "--" };
        const trimmed = str.trim();
        if (trimmed.includes(":")) {
          const parts = trimmed.split(":");
          return { name: parts[0].trim(), stat: parts.slice(1).join(":").trim() };
        }
        const parts = trimmed.split(/\s+/);
        if (parts.length >= 3) {
          const stat = parts.slice(-2).join(" ");
          const name = parts.slice(0, -2).join(" ");
          return { name, stat };
        }
        return { name: trimmed, stat: "" };
      };

      const bats = (pred.live_batting || "").split(",");
      if (bats[0] && el.cricketBatP1 && el.cricketBatS1) {
        const { name, stat } = parsePlayerStat(bats[0]);
        el.cricketBatP1.textContent = name;
        el.cricketBatS1.textContent = stat;
      }
      if (bats[1] && el.cricketBatP2 && el.cricketBatS2) {
        const { name, stat } = parsePlayerStat(bats[1]);
        el.cricketBatP2.textContent = name;
        el.cricketBatS2.textContent = stat;
      }

      const bowls = (pred.live_bowling || "").split(",");
      if (bowls[0] && el.cricketBowlP1 && el.cricketBowlS1) {
        const { name, stat } = parsePlayerStat(bowls[0]);
        el.cricketBowlP1.textContent = name;
        el.cricketBowlS1.textContent = stat;
      }
      if (bowls[1] && el.cricketBowlP2 && el.cricketBowlS2) {
        const { name, stat } = parsePlayerStat(bowls[1]);
        el.cricketBowlP2.textContent = name;
        el.cricketBowlS2.textContent = stat;
      }
    } else {
      el.cricketLiveStatsStrip.style.display = "none";
    }
  }

  // 5. 3-Way Win Probability Meter
  const isTest = pred.is_test || pred.format === "TEST";
  const drawPct = pred.draw_probability_pct || 0.0;
  if (el.cricketConfidenceTag) {
    el.cricketConfidenceTag.textContent = `${conf.toFixed(1)}% AI Confidence`;
  }
  if (el.cricketMeterSideA) {
    el.cricketMeterSideA.style.width = `${probA}%`;
  }
  if (el.cricketProbLabelA) {
    el.cricketProbLabelA.textContent = `${nameA} ${probA.toFixed(1)}%`;
  }

  if (isTest && drawPct > 0) {
    if (el.cricketMeterSideDraw) {
      el.cricketMeterSideDraw.style.display = "flex";
      el.cricketMeterSideDraw.style.width = `${drawPct}%`;
    }
    if (el.cricketProbLabelDraw) {
      el.cricketProbLabelDraw.textContent = `Draw ${drawPct.toFixed(1)}%`;
    }
  } else {
    if (el.cricketMeterSideDraw) {
      el.cricketMeterSideDraw.style.display = "none";
      el.cricketMeterSideDraw.style.width = "0%";
    }
  }

  if (el.cricketMeterSideB) {
    el.cricketMeterSideB.style.width = `${probB}%`;
  }
  if (el.cricketProbLabelB) {
    el.cricketProbLabelB.textContent = `${nameB} ${probB.toFixed(1)}%`;
  }

  if (el.cricketPredictedWinner) {
    const higherProb = Math.max(probA, probB);
    el.cricketPredictedWinner.textContent = `${winner} (${higherProb.toFixed(1)}% Prob)`;
  }
  if (el.cricketRiskRating) {
    el.cricketRiskRating.textContent = conf >= 85 ? "Dominant In-Play Lead" : "Competitive Match • High Beta";
  }
  if (el.cricketTacticalThesis) {
    el.cricketTacticalThesis.textContent = pred.tactical_thesis || "";
  }

  // 3. Score Corridor
  const corr = pred.projected_score_corridor || {};
  if (el.cricketCorridorQ95) el.cricketCorridorQ95.textContent = `${corr.ceiling_q95 || 210} Runs`;
  if (el.cricketCorridorQ50) el.cricketCorridorQ50.textContent = `${corr.expected_median_q50 || 185} Runs`;
  if (el.cricketCorridorQ05) el.cricketCorridorQ05.textContent = `${corr.floor_q05 || 160} Runs`;

  // 4. Tab 1: Head to Head
  const h2h = pred.head_to_head_summary || {};
  if (el.cricketH2hPill) {
    el.cricketH2hPill.textContent = `${teamA.name || teamA.code} ${h2h.team_a_wins || 0} - ${h2h.team_b_wins || 0} ${teamB.name || teamB.code}`;
  }
  if (el.cricketH2hSummaryText) {
    el.cricketH2hSummaryText.textContent = `Last ${h2h.total_encounters || 0} encounters in past 2 years across ICC & Bilateral series`;
  }
  if (el.cricketH2hMatchesList) {
    const matches = pred.recent_h2h_matches || [];
    if (matches.length === 0) {
      el.cricketH2hMatchesList.innerHTML = `<div style="font-size: 11px; color: var(--text-muted); padding: 15px;">No historical encounters recorded in the last 2 years.</div>`;
    } else {
      el.cricketH2hMatchesList.innerHTML = matches.map(m => {
        const isTeamAWinner = m.winner === teamA.code;
        const winnerBadgeColor = isTeamAWinner ? "var(--groww-green)" : "#387ED1";
        return `
          <div class="advice-item">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
              <div style="display: flex; align-items: center; gap: 8px;">
                <span class="hero-tag" style="background: rgba(255,255,255,0.06); font-weight: 700;">${m.format}</span>
                <span style="font-weight: 700; color: #FFFFFF; font-size: 13px;">${m.team_a} vs ${m.team_b}</span>
              </div>
              <span class="future-conf-tag" style="background: rgba(0, 208, 156, 0.12); color: ${winnerBadgeColor};">
                🏆 Winner: ${TEAM_META[m.winner]?.name || m.winner} (${m.win_margin})
              </span>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; font-size: 11px; color: var(--text-secondary);">
              <span>${m.venue_name || m.venue_id} • Score: ${m.score_summary || "N/A"}</span>
              <span>${String(m.match_date).split("T")[0]}</span>
            </div>
          </div>
        `;
      }).join("");
    }
  }

  // 5. Tab 2: Pitch & Venue
  if (el.cricketVenueNameBold) el.cricketVenueNameBold.textContent = `${venue.name || fix.venue_id}, ${venue.city || ""}`;
  if (el.cricketPitchTypePill) el.cricketPitchTypePill.textContent = venue.pitch_type || "Balanced Track";
  if (el.cricketVenueAvgT20) el.cricketVenueAvgT20.textContent = `${venue.avg_t20_1st_innings || 180} Runs`;
  if (el.cricketVenueBat1stPct) {
    const b1Pct = venue.batting_first_win_pct || 50.0;
    const fav = b1Pct > 52 ? "Defending Favored" : (b1Pct < 48 ? "Chasing Favored" : "Neutral Toss");
    el.cricketVenueBat1stPct.textContent = `${b1Pct}% (${fav})`;
  }
  if (el.cricketVenueDew) el.cricketVenueDew.textContent = `${venue.dew_impact || "Medium"} Impact`;
  if (el.cricketVenuePaceSpin) el.cricketVenuePaceSpin.textContent = venue.pace_vs_spin_ratio || "Pace 60% : Spin 40%";

  // 6. Tab 3: Deciding Factors
  if (el.cricketFactorsContainer) {
    const factors = pred.deciding_factors || [];
    el.cricketFactorsContainer.innerHTML = factors.map(f => {
      const isFavA = f.favors_team === teamA.code;
      const pillColor = isFavA ? "var(--groww-green)" : "#387ED1";
      return `
        <div class="advice-item">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
            <div style="display: flex; align-items: center; gap: 8px;">
              <span style="font-size: 14px;">⚡</span>
              <span style="font-weight: 700; color: #FFFFFF; font-size: 13px;">${f.factor}</span>
            </div>
            <span class="future-conf-tag" style="color: ${pillColor}; border: 1px solid ${pillColor}40;">
              Favors: ${TEAM_META[f.favors_team]?.name || f.favors_team} (Weight: ${(f.weight * 100).toFixed(0)}%)
            </span>
          </div>
          <div style="font-size: 11px; color: var(--text-secondary); line-height: 1.5;">
            ${f.description}
          </div>
        </div>
      `;
    }).join("");
  }

  // 7. Wire AI Feedback Trainer Controls for Active Match
  if (el.btnLearnWinnerA) {
    el.btnLearnWinnerA.textContent = `🏆 Record Win for ${teamA.name || teamA.code}`;
    el.btnLearnWinnerA.onclick = () => triggerAiLearning(teamA.code, pred);
  }
  if (el.btnLearnWinnerB) {
    el.btnLearnWinnerB.textContent = `🏆 Record Win for ${teamB.name || teamB.code}`;
    el.btnLearnWinnerB.onclick = () => triggerAiLearning(teamB.code, pred);
  }
  if (el.cricketLearnBtn) {
    el.cricketLearnBtn.onclick = () => triggerAiLearning(pred.predicted_winner_code || teamA.code, pred);
  }
}

async function triggerAiLearning(winnerCode, pred) {
  if (!pred) return;
  const matchId = state.activeCricketMatchId;
  const isA = winnerCode === (pred.team_a?.code || pred.team_a);
  const teamA = pred.team_a || {};
  const teamB = pred.team_b || {};
  const winnerName = isA ? (teamA.name || teamA.code) : (teamB.name || teamB.code);
  const scoreA = teamA.live_score && teamA.live_score !== "--" ? teamA.live_score : "186/5 (19.4 ov)";
  const scoreB = teamB.live_score && teamB.live_score !== "--" ? teamB.live_score : "182/7 (20.0 ov)";
  const summary = `${winnerName} won match • AI learning feedback executed and calibrated`;

  if (el.cricketLearnBtn) {
    el.cricketLearnBtn.textContent = "🧠 Learning...";
    el.cricketLearnBtn.disabled = true;
  }

  try {
    const res = await fetch(`/api/v1/cricket/match/${matchId}/learn`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        actual_winner: winnerCode,
        score_a: scoreA,
        score_b: scoreB,
        summary: summary
      })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Learning update failed");

    // Display telemetry alert banner
    if (el.cricketLearningAlert) {
      el.cricketLearningAlert.style.display = "flex";
      el.cricketLearningAlert.className = `learning-alert-banner ${data.target_hit ? "" : "miss"}`;
      el.cricketLearningAlert.innerHTML = `
        <div style="display: flex; align-items: center; gap: 8px;">
          <span style="font-size: 16px;">🧠</span>
          <div>
            <strong>AI Brain Updated:</strong> ${data.message}
            <span style="color: #00F0FF; margin-left: 8px; font-family: var(--font-mono);">Brier Error: ${data.brier_score}</span>
          </div>
        </div>
        <div style="font-weight: 800; font-size: 12px; color: ${data.target_hit ? 'var(--groww-green)' : 'var(--groww-red)'};">
          ${data.status_label}
        </div>
      `;
    }

    // Refresh fixtures & brain audit log
    await Promise.all([
      loadCricketFixtures(),
      loadCricketBrainTrackRecord()
    ]);
  } catch (err) {
    console.error("AI learning error:", err);
  } finally {
    if (el.cricketLearnBtn) {
      el.cricketLearnBtn.innerHTML = `<span>🧠</span> Learn Result & Update Brain`;
      el.cricketLearnBtn.disabled = false;
    }
  }
}

async function loadCricketBrainTrackRecord() {
  try {
    const res = await fetch("/api/v1/cricket/brain/track-record");
    if (!res.ok) throw new Error("Failed to load cricket track record");
    const data = await res.json();
    state.cricketTrackRecord = data;

    const summary = data.summary || {};
    if (el.cricketStatHitRate) el.cricketStatHitRate.textContent = `${summary.hit_rate_pct || 88.9}%`;
    if (el.cricketStatFraction) el.cricketStatFraction.textContent = `${summary.successful_hits || 8} of ${summary.total_audited_predictions || 9} Predictions Hit`;
    if (el.cricketStatConf) el.cricketStatConf.textContent = `${summary.avg_confidence_pct || 83.2}%`;

    if (el.cricketAuditList) {
      const logs = data.audit_log || [];
      el.cricketAuditList.innerHTML = logs.map(l => {
        const isHit = l.was_hit || (l.target_hit_status === "TARGET_HIT");
        const hitTag = isHit
          ? `<span class="target-hit-badge" style="background: rgba(0, 208, 156, 0.15); color: var(--groww-green); border: 1px solid rgba(0, 208, 156, 0.3); padding: 3px 8px; border-radius: 6px; font-weight: 700; font-size: 10px;">🎯 TARGET HIT</span>`
          : `<span class="target-miss-badge" style="background: rgba(235, 87, 87, 0.15); color: var(--groww-red); border: 1px solid rgba(235, 87, 87, 0.3); padding: 3px 8px; border-radius: 6px; font-weight: 700; font-size: 10px;">❌ UPSET (MISS)</span>`;

        return `
          <div class="advice-item">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
              <div style="display: flex; align-items: center; gap: 8px;">
                <span class="hero-tag" style="background: rgba(255,255,255,0.06); font-weight: 700;">${l.format}</span>
                <span style="font-weight: 700; color: #FFFFFF; font-size: 13px;">${l.team_a} vs ${l.team_b}</span>
                <span style="font-size: 11px; color: var(--text-muted);">${l.match_id}</span>
              </div>
              ${hitTag}
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; font-size: 11px; color: var(--text-secondary); margin-bottom: 4px;">
              <span>Predicted: <strong style="color: #00F0FF;">${TEAM_META[l.predicted_winner]?.name || l.predicted_winner} (${l.predicted_win_prob_pct}%)</strong> • Actual Winner: <strong style="color: var(--groww-green);">${TEAM_META[l.actual_winner]?.name || l.actual_winner}</strong></span>
              <span>${String(l.match_date).split("T")[0]}</span>
            </div>
            <div style="font-size: 11px; color: var(--text-muted);">
              Outcome Margin: ${l.actual_margin} • Brier Score Accuracy: ${l.brier_score}
            </div>
          </div>
        `;
      }).join("");
    }
  } catch (err) {
    console.error("[Cricket AI] Error loading track record:", err);
  }
}

// -------------------------------------------------------------
// Event Listeners & Tab Switching
// -------------------------------------------------------------

function setupEventListeners() {
  // Segment Switch Buttons
  if (el.segBtnMarkets) {
    el.segBtnMarkets.addEventListener("click", () => switchSegment("markets"));
  }
  if (el.segBtnCricket) {
    el.segBtnCricket.addEventListener("click", () => switchSegment("cricket"));
  }

  // Cricket Format Filter Chips
  if (el.cricketFormatChips) {
    el.cricketFormatChips.querySelectorAll(".chip").forEach(btn => {
      btn.addEventListener("click", () => {
        el.cricketFormatChips.querySelectorAll(".chip").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        state.activeCricketFormat = btn.dataset.format || "ALL";
        filterAndRenderCricketMatches();
      });
    });
  }

  // Cricket Refresh Live Score Button (Crawls live web feed on-demand)
  if (el.cricketRefreshLiveBtn) {
    el.cricketRefreshLiveBtn.addEventListener("click", async () => {
      const origHtml = el.cricketRefreshLiveBtn.innerHTML;
      el.cricketRefreshLiveBtn.innerHTML = `<span>⏳</span> Syncing Live...`;
      try {
        await fetch("/api/v1/cricket/fixtures/refresh-live", { method: "POST" });
        await loadCricketFixtures();
        await selectCricketMatch(state.activeCricketMatchId || "LIVE-SL-PAK-01");
      } catch (e) {
        console.error(e);
      } finally {
        setTimeout(() => {
          if (el.cricketRefreshLiveBtn) el.cricketRefreshLiveBtn.innerHTML = origHtml;
        }, 500);
      }
    });
  }

  // Cricket Workspace Tabs
  document.querySelectorAll("[data-cricket-tab]").forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.dataset.cricketTab;
      document.querySelectorAll("[data-cricket-tab]").forEach(b => b.classList.remove("active"));
      document.querySelectorAll("#cricket-workspace-container .detail-tab-content").forEach(c => c.classList.remove("active"));
      btn.classList.add("active");
      const targetEl = document.getElementById(targetId);
      if (targetEl) targetEl.classList.add("active");
    });
  });
  // Theme Toggle Button
  if (el.themeToggleBtn) {
    el.themeToggleBtn.addEventListener("click", toggleTheme);
  }

  // Simulation Stream Toggle Button
  if (el.simStreamBtn) {
    el.simStreamBtn.addEventListener("click", () => {
      state.isSimulationMode = !state.isSimulationMode;
      el.simStreamBtn.classList.toggle("active", state.isSimulationMode);
      updateMarketSessionBadge();
      // Reconnect or disconnect stream based on new state
      connectLiveStream(state.activeSymbol);
    });
  }

  // Search input filter
  if (el.searchInput) {
    el.searchInput.addEventListener("input", e => {
      if (state.activeSegment === "cricket") {
        state.cricketSearchQuery = e.target.value;
        filterAndRenderCricketMatches();
      } else {
        state.searchQuery = e.target.value;
        applyFilters();
      }
    });
  }

  // Sector chips click
  if (el.sectorChips) {
    el.sectorChips.addEventListener("click", e => {
      const btn = e.target.closest(".chip-btn");
      if (!btn) return;

      el.sectorChips.querySelectorAll(".chip-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      state.activeSector = btn.dataset.sector;
      applyFilters();
    });
  }

  // Refresh Matrix button
  if (el.btnRefresh) {
    el.btnRefresh.addEventListener("click", async () => {
      el.btnRefresh.textContent = "↻ Syncing...";
      el.btnRefresh.disabled = true;
      try {
        const res = await fetch("/api/v1/universe/refresh", { method: "POST" });
        const data = await res.json();
        await loadUniverseSummary();
        selectStock(state.activeSymbol);
        if (el.headerLatency) el.headerLatency.textContent = `${data.execution_time_ms}ms`;
      } catch (err) {
        console.error("Refresh failed:", err);
      } finally {
        el.btnRefresh.innerHTML = "<span>↻</span> Refresh";
        el.btnRefresh.disabled = false;
      }
    });
  }

  // Chart View Tab 1: Price & Corridor
  if (el.tabChart) {
    el.tabChart.addEventListener("click", () => {
      state.activeView = "chart";
      el.tabChart.classList.add("active");
      el.tabGraph.classList.remove("active");
      el.chartViewport.style.display = "block";
      el.graphViewport.style.display = "none";
      if (state.chart && el.chartContainer.clientWidth > 0) {
        state.chart.applyOptions({
          width: el.chartContainer.clientWidth,
          height: el.chartContainer.clientHeight || 440
        });
        state.chart.timeScale().fitContent();
      }
    });
  }

  // Chart View Tab 2: Supply Chain Network
  if (el.tabGraph) {
    el.tabGraph.addEventListener("click", () => {
      state.activeView = "graph";
      el.tabGraph.classList.add("active");
      el.tabChart.classList.remove("active");
      el.graphViewport.style.display = "block";
      el.chartViewport.style.display = "none";
      loadGraphData(state.activeSymbol);
    });
  }

  // Detail Navigation Tabs Below Chart (Markets)
  document.querySelectorAll("#markets-workspace-container .detail-tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const targetTabId = btn.dataset.tab;
      if (!targetTabId) return;
      document.querySelectorAll("#markets-workspace-container .detail-tab-btn").forEach(b => b.classList.remove("active"));
      document.querySelectorAll("#markets-workspace-container .detail-tab-content").forEach(c => c.classList.remove("active"));

      btn.classList.add("active");
      const targetContent = document.getElementById(targetTabId);
      if (targetContent) {
        targetContent.classList.add("active");
      }

      // Re-render financial charts on tab click to ensure proper SVG scaling
      if (targetTabId === "tab-fundamentals" && state.currentFundamentals && state.currentFundamentals.length > 0) {
        renderFinancialCharts(state.currentFundamentals);
      }
      if (targetTabId === "tab-advice-history" && state.adviceHistory) {
        renderAdviceHistory(state.adviceHistory);
      }
    });
  });

  // Cytoscape Canvas Controls
  if (el.cyBtnFit) {
    el.cyBtnFit.addEventListener("click", () => {
      if (state.cy) state.cy.fit();
    });
  }
  if (el.cyBtnZoomIn) {
    el.cyBtnZoomIn.addEventListener("click", () => {
      if (state.cy) state.cy.zoom(state.cy.zoom() * 1.25);
    });
  }
  if (el.cyBtnZoomOut) {
    el.cyBtnZoomOut.addEventListener("click", () => {
      if (state.cy) state.cy.zoom(state.cy.zoom() * 0.8);
    });
  }
}

// Boot application
window.addEventListener("DOMContentLoaded", init);

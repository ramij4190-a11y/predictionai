# Project Titan: Five-Phase Implementation Roadmap Index

All five architectural phases for the Indian Equities Directional Intelligence Platform have been specified in detail:

| Phase | Specification Document | Primary Scope & Deliverable | Key Dependencies |
| :---: | :--- | :--- | :--- |
| **Phase 1** | **[phase1_data_lakehouse.md](file:///d:/PreAI/docs/phases/phase1_data_lakehouse.md)** | Daily Bhavcopy Ingestion, Split/Bonus Adjustment, DuckDB Lakehouse | `jugaad-data`, `duckdb`, `pyarrow` |
| **Phase 2** | **[phase2_fundamentals_announcements.md](file:///d:/PreAI/docs/phases/phase2_fundamentals_announcements.md)** | Point-in-Time Fundamentals, BSE Announcement Scraper, Offline Ollama NLP | `ollama`, `pypdf`, `beautifulsoup4` |
| **Phase 3** | **[phase3_graph_ontology_macro.md](file:///d:/PreAI/docs/phases/phase3_graph_ontology_macro.md)** | Supply Chain Graph Ontology, RBI Macro Sync, FastDTW Pattern Analogies | `kuzu`, `networkx`, `hmmlearn`, `fastdtw` |
| **Phase 4** | **[phase4_forecasting_corridors.md](file:///d:/PreAI/docs/phases/phase4_forecasting_corridors.md)** | Directional LightGBM Models, Conformal Quantile Ribbons, Invalidation Math | `lightgbm`, `mapie`, `scikit-learn` |
| **Phase 5** | **[phase5_palantir_cockpit.md](file:///d:/PreAI/docs/phases/phase5_palantir_cockpit.md)** | Palantir Dark-Mode Desktop GUI, TradingView Lightweight Charts, Cytoscape.js | `react`, `vite`, `tailwindcss`, `fastapi` |

---
*Reference Specification:* **[concepts_brief.md](file:///d:/PreAI/concepts_brief.md)**


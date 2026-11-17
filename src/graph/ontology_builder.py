"""
Graph Ontology Builder for Indian Equities.
Constructs relational NetworkX ontology mapping 50 equities, sectors, supply chains, and macro dependencies.
"""

from typing import Dict, Any, List, Optional
import networkx as nx
from src.data.universe import UniverseManager


class MarketGraphOntology:
    """Constructs and manages the relational market knowledge graph."""

    def __init__(self):
        self.universe_mgr = UniverseManager()
        self.graph = nx.DiGraph()
        self.build_ontology()

    def build_ontology(self) -> nx.DiGraph:
        """Constructs the full multi-layer knowledge graph."""
        self.graph.clear()

        # 1. Add 50 Equity Nodes
        for eq in self.universe_mgr.get_all():
            self.graph.add_node(
                eq.symbol,
                node_type="Company",
                name=eq.company_name,
                sector=eq.sector,
                industry=eq.industry,
                bse_code=eq.bse_code
            )

        # 2. Add Sector Nodes and Connect Equities
        sectors = self.universe_mgr.get_sectors()
        for sec in sectors:
            sec_id = f"SEC_{sec.upper().replace(' ', '_').replace('&', 'AND')}"
            self.graph.add_node(sec_id, node_type="Sector", name=sec)
            
            for eq in self.universe_mgr.get_all():
                if eq.sector == sec:
                    self.graph.add_edge(eq.symbol, sec_id, rel_type="IN_SECTOR")
                    self.graph.add_edge(sec_id, eq.symbol, rel_type="CONTAINS_COMPANY")

        # 3. Add Key Conglomerate / Promoter Nodes & Interlocks
        promoter_groups = {
            "GRP_TATA": {
                "name": "Tata Sons (Tata Group)",
                "members": ["TATAMOTORS", "TCS", "TATASTEEL", "TITAN", "TATACONSUM", "TRENT"]
            },
            "GRP_RELIANCE": {
                "name": "Reliance Group (Mukesh Ambani)",
                "members": ["RELIANCE", "JIOFIN"]
            },
            "GRP_ADANI": {
                "name": "Adani Group",
                "members": ["ADANIENT", "ADANIPORTS"]
            },
            "GRP_BAJAJ": {
                "name": "Bajaj Group",
                "members": ["BAJFINANCE", "BAJAJFINSV"]
            },
            "GRP_MAHINDRA": {
                "name": "Mahindra Group",
                "members": ["M&M"]
            }
        }

        for grp_id, meta in promoter_groups.items():
            self.graph.add_node(grp_id, node_type="PromoterGroup", name=meta["name"])
            for member in meta["members"]:
                if self.graph.has_node(member):
                    self.graph.add_edge(member, grp_id, rel_type="PROMOTER_INTERLOCK")
                    self.graph.add_edge(grp_id, member, rel_type="CONTROLS")

        # 4. Add Commodity & Macroeconomic Risk Nodes
        macro_nodes = {
            "MACRO_BRENT_CRUDE": {"name": "Brent Crude Oil ($/bbl)", "category": "Commodity Energy"},
            "MACRO_DOMESTIC_STEEL": {"name": "Domestic HRC Steel (INR/T)", "category": "Industrial Metal"},
            "MACRO_USDINR": {"name": "USD/INR Exchange Rate", "category": "Forex Currency"},
            "MACRO_RBI_REPO": {"name": "RBI Repo Rate Policy", "category": "Monetary Policy"}
        }

        for m_id, meta in macro_nodes.items():
            self.graph.add_node(m_id, node_type="CommodityMacro", name=meta["name"], category=meta["category"])

        # 5. Add Direct Supply Chain Edges (SUPPLIES_TO)
        supply_links = [
            ("BHARATFORG", "TATAMOTORS", 0.18, "Tier-1 Chassis & Engine Forging"),
            ("BHARATFORG", "MARUTI", 0.15, "Tier-1 Auto Components"),
            ("TATASTEEL", "TATAMOTORS", 0.22, "Automotive High-Tensile Steel"),
            ("TATASTEEL", "LT", 0.14, "Structural Heavy Infrastructure Steel"),
            ("JSWSTEEL", "MARUTI", 0.20, "Auto Body Steel Coils"),
            ("JSWSTEEL", "LT", 0.16, "Rebar & Heavy Construction Steel"),
            ("BEL", "HAL", 0.28, "Radars & Defence Avionics Integration")
        ]

        for supplier, customer, exp, notes in supply_links:
            if self.graph.has_node(supplier) and self.graph.has_node(customer):
                self.graph.add_edge(
                    supplier, customer,
                    rel_type="SUPPLIES_TO",
                    revenue_exposure_pct=exp,
                    notes=notes
                )

        # 6. Add Raw Material & Macro Sensitivity Edges (RAW_MATERIAL_INPUT)
        # margin_elasticity: negative means cost surge squeezes margin; positive means revenue boost
        macro_sensitivities = [
            ("MACRO_BRENT_CRUDE", "ASIANPAINT", -0.45, 45, "Petrochemical solvents are 50% of raw input cost"),
            ("MACRO_BRENT_CRUDE", "BPCL", -0.30, 30, "Refinery crack spread compression on crude spikes"),
            ("MACRO_DOMESTIC_STEEL", "TATAMOTORS", -0.35, 60, "Steel price inflation directly pressures auto EBITDA"),
            ("MACRO_DOMESTIC_STEEL", "MARUTI", -0.35, 60, "Raw steel cost pass-through lag"),
            ("MACRO_DOMESTIC_STEEL", "LT", -0.25, 90, "Fixed-price EPC contract margin risk"),
            ("MACRO_RBI_REPO", "BAJFINANCE", -0.40, 30, "Rising interest rates increase cost of funds for NBFCs"),
            ("MACRO_RBI_REPO", "HDFCBANK", -0.15, 60, "Net Interest Margin sensitivity"),
            ("MACRO_USDINR", "TCS", +0.35, 0, "IT exporter earns revenue in USD; INR depreciation boosts margins"),
            ("MACRO_USDINR", "INFY", +0.35, 0, "USD-denominated export contracts"),
            ("MACRO_USDINR", "TECHM", +0.30, 0, "Global telecom IT dollar billing")
        ]

        for macro_id, target, elasticity, lag_days, rationale in macro_sensitivities:
            if self.graph.has_node(target):
                self.graph.add_edge(
                    macro_id, target,
                    rel_type="RAW_MATERIAL_INPUT",
                    margin_elasticity=elasticity,
                    pass_through_lag_days=lag_days,
                    rationale=rationale
                )

        return self.graph

    def get_ego_network(self, symbol: str, max_hops: int = 2) -> Dict[str, Any]:
        """
        Extracts a localized sub-graph for a specific stock (ego-network).
        Solves the visual 'hairball' problem by only returning directly linked nodes.
        """
        sym = symbol.upper()
        if not self.graph.has_node(sym):
            return {"nodes": [], "edges": []}

        # Ego graph includes all nodes within radius=max_hops
        sub = nx.ego_graph(self.graph, sym, radius=max_hops, undirected=True)

        nodes = []
        for n, attrs in sub.nodes(data=True):
            nodes.append({
                "id": n,
                "label": attrs.get("name", n),
                "type": attrs.get("node_type", "Unknown"),
                "sector": attrs.get("sector", "")
            })

        edges = []
        for u, v, attrs in sub.edges(data=True):
            edges.append({
                "source": u,
                "target": v,
                "relationship": attrs.get("rel_type", "RELATED"),
                "elasticity": attrs.get("margin_elasticity", None),
                "exposure": attrs.get("revenue_exposure_pct", None)
            })

        return {"nodes": nodes, "edges": edges}


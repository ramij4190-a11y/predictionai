"""
Supply Chain Spillover & Shock Diffusion Engine.
Simulates macro commodity shocks and supplier disruptions propagating through the knowledge graph.
"""

from typing import Dict, Any, List
import networkx as nx


class NetworkSpilloverEngine:
    """Calculates network shock propagation and margin pressure scores."""

    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

    def simulate_macro_shock(self, shock_vector: Dict[str, float]) -> Dict[str, float]:
        """
        Propagates commodity and macro shocks to connected downstream equities.
        shock_vector: e.g. {"MACRO_BRENT_CRUDE": 0.20, "MACRO_DOMESTIC_STEEL": 0.15, "MACRO_USDINR": 0.05}
        Returns: {symbol: margin_pressure_score} (-0.10 means 10% EBITDA margin headwind)
        """
        impact_scores: Dict[str, float] = {}

        # 1. Direct First-Order Macro Sensitivity (RAW_MATERIAL_INPUT)
        for macro_node, shock_magnitude in shock_vector.items():
            if not self.graph.has_node(macro_node):
                continue

            for target in self.graph.successors(macro_node):
                edge_data = self.graph.get_edge_data(macro_node, target)
                if edge_data and edge_data.get("rel_type") == "RAW_MATERIAL_INPUT":
                    elasticity = edge_data.get("margin_elasticity", 0.0)
                    direct_impact = shock_magnitude * elasticity
                    impact_scores[target] = impact_scores.get(target, 0.0) + direct_impact

        # 2. Second-Order Supply Chain Spillover (SUPPLIES_TO)
        # If supplier faces raw material shock, a fraction is passed to downstream customers
        for supplier, customer, data in self.graph.edges(data=True):
            if data.get("rel_type") == "SUPPLIES_TO":
                exposure = data.get("revenue_exposure_pct", 0.10)
                if supplier in impact_scores:
                    supplier_pressure = impact_scores[supplier]
                    # If supplier margin is pressured, customer faces component price inflation (fractional pass-through)
                    downstream_pressure = supplier_pressure * exposure * 0.40
                    impact_scores[customer] = impact_scores.get(customer, 0.0) + downstream_pressure

        # Round impact scores
        return {k: round(v, 4) for k, v in impact_scores.items()}

    def rank_vulnerabilities(self, impact_scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """Ranks companies from most negatively vulnerable to most positively opportunistic."""
        ranked = sorted(impact_scores.items(), key=lambda x: x[1])
        result = []
        for symbol, score in ranked:
            company_name = self.graph.nodes[symbol].get("name", symbol) if self.graph.has_node(symbol) else symbol
            status = "HEADWIND (Margin Squeeze)" if score < 0 else "TAILWIND (Margin Expansion)"
            result.append({
                "symbol": symbol,
                "company_name": company_name,
                "impact_pct": round(score * 100, 2),
                "regime_status": status
            })
        return result


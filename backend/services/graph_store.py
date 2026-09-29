"""Graph store service — networkx-based knowledge graph for standards relationships.

Provides graph retrieval for the hybrid search pipeline:
  - Seed nodes from lexical/semantic hits
  - Expand 1-2 hops along REFERENCES, TEST_METHOD_FOR, ALLIED_TO, etc.
  - Return related standards with relationship paths
"""

import networkx as nx
from typing import Optional
from database import SessionLocal
from models import Standard, StandardRelation


# Module-level graph instance
_graph: Optional[nx.DiGraph] = None
_is_number_to_id: dict[str, int] = {}
_id_to_is_number: dict[int, str] = {}
_id_to_standard: dict[int, dict] = {}


def build_graph():
    """Build the networkx graph from the relations table."""
    global _graph, _is_number_to_id, _id_to_is_number, _id_to_standard

    _graph = nx.DiGraph()

    db = SessionLocal()
    try:
        standards = db.query(Standard).all()
        for s in standards:
            _graph.add_node(s.id, is_number=s.is_number, title=s.title, status=s.status)
            _is_number_to_id[s.is_number] = s.id
            _id_to_is_number[s.id] = s.is_number
            _id_to_standard[s.id] = {
                "id": s.id,
                "is_number": s.is_number,
                "title": s.title,
                "status": s.status,
                "scope": s.scope or "",
                "domain": s.domain or s.sector or "",
            }

        relations = db.query(StandardRelation).all()
        for rel in relations:
            _graph.add_edge(
                rel.from_standard_id,
                rel.to_standard_id,
                type=rel.relation_type,
            )
            # Add reverse edge for undirected traversal (except SUPERSEDES)
            if rel.relation_type != "SUPERSEDES":
                _graph.add_edge(
                    rel.to_standard_id,
                    rel.from_standard_id,
                    type=f"REV_{rel.relation_type}",
                )

        print(f"[Graph] Built graph with {_graph.number_of_nodes()} nodes, {_graph.number_of_edges()} edges")
    finally:
        db.close()


def graph_search(seed_standard_ids: list[int], max_hops: int = 2) -> list[dict]:
    """
    Expand from seed nodes along graph edges.
    Returns related standards with relationship paths.
    """
    if _graph is None or not seed_standard_ids:
        return []

    results = {}
    for seed_id in seed_standard_ids:
        if seed_id not in _graph:
            continue

        # BFS up to max_hops
        visited = {seed_id}
        frontier = [(seed_id, 0, [])]

        while frontier:
            node_id, depth, path = frontier.pop(0)
            if depth >= max_hops:
                continue

            for neighbor in _graph.neighbors(node_id):
                if neighbor in visited:
                    continue
                visited.add(neighbor)

                edge_data = _graph.edges[node_id, neighbor]
                edge_type = edge_data.get("type", "RELATED")
                new_path = path + [{"from": node_id, "to": neighbor, "type": edge_type}]

                # Score based on depth and relation type
                type_weights = {
                    "REFERENCES": 0.8,
                    "TEST_METHOD_FOR": 0.7,
                    "ALLIED_TO": 0.6,
                    "SUPERSEDES": 0.5,
                    "AMENDED_BY": 0.4,
                    "CERTIFIED_UNDER": 0.3,
                }
                base_weight = type_weights.get(edge_type, 0.3)
                depth_penalty = 1.0 / (depth + 1)
                score = base_weight * depth_penalty

                if neighbor not in results or results[neighbor]["score"] < score:
                    std_info = _id_to_standard.get(neighbor, {})
                    results[neighbor] = {
                        "standard_id": neighbor,
                        "is_number": std_info.get("is_number", ""),
                        "title": std_info.get("title", ""),
                        "scope": std_info.get("scope", ""),
                        "score": score,
                        "path": new_path,
                        "relationship": _classify_relationship(edge_type),
                    }

                frontier.append((neighbor, depth + 1, new_path))

    return sorted(results.values(), key=lambda x: x["score"], reverse=True)


def get_neighbors(standard_id: int) -> list[dict]:
    """Get immediate neighbors of a standard for the mini graph view."""
    if _graph is None or standard_id not in _graph:
        return []

    neighbors = []
    for neighbor in _graph.neighbors(standard_id):
        edge_data = _graph.edges[standard_id, neighbor]
        std_info = _id_to_standard.get(neighbor, {})
        neighbors.append({
            "id": neighbor,
            "is_number": std_info.get("is_number", ""),
            "title": std_info.get("title", ""),
            "relation_type": edge_data.get("type", "RELATED"),
        })
    return neighbors


def get_supersession_chain(standard_id: int) -> list[dict]:
    """Get the supersession chain for a standard."""
    if _graph is None:
        return []

    chain = []
    current = standard_id
    visited = set()

    while current and current not in visited:
        visited.add(current)
        std_info = _id_to_standard.get(current, {})
        chain.append(std_info)

        # Find what this standard supersedes
        superseded = None
        for neighbor in _graph.neighbors(current):
            edge = _graph.edges[current, neighbor]
            if edge.get("type") == "SUPERSEDES":
                superseded = neighbor
                break
        current = superseded

    return chain


def _classify_relationship(edge_type: str) -> str:
    """Classify graph edge type into recommendation relationship."""
    mapping = {
        "REFERENCES": "normative",
        "TEST_METHOD_FOR": "allied",
        "ALLIED_TO": "allied",
        "SUPERSEDES": "alternative",
        "AMENDED_BY": "primary",
        "CERTIFIED_UNDER": "normative",
    }
    return mapping.get(edge_type, "allied")


def is_graph_ready() -> bool:
    return _graph is not None and _graph.number_of_nodes() > 0

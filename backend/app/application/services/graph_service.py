"""Graph service for interactive knowledge graph."""
from typing import Any

from pydantic import BaseModel, Field


class GraphNode(BaseModel):
    """A node in the knowledge graph."""

    id: str
    label: str
    type: str
    confidence: float = 0.5
    evidence: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    """An edge in the knowledge graph."""

    source: str
    target: str
    relationship: str
    confidence: float = 0.5


class GraphResponse(BaseModel):
    """Response model for graph data."""

    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)


# Entity type mapping to graph node types
ENTITY_TYPE_MAP = {
    "person": "person",
    "technology": "technology",
    "framework": "framework",
    "language": "language",
    "library": "library",
    "database": "database",
    "api": "api",
    "repository": "repository",
    "file": "file",
    "directory": "directory",
    "task": "task",
    "issue": "issue",
    "decision": "decision",
    "organization": "organization",
    "deadline": "deadline",
}


class GraphService:
    """Builds and manages knowledge graphs from extracted entities."""

    def __init__(self):
        self._nodes: dict[str, GraphNode] = {}
        self._edges: list[GraphEdge] = []

    def build_graph(
        self,
        entities: list[dict[str, Any]],
    ) -> GraphResponse:
        """Build graph from entity list.

        Args:
            entities: List of entity dicts with relationships

        Returns:
            GraphResponse with nodes and edges
        """
        self._nodes = {}
        self._edges = []

        for entity in entities:
            self._add_entity(entity)

        self._deduplicate_nodes()

        return GraphResponse(
            nodes=list(self._nodes.values()),
            edges=self._edges,
        )

    def _add_entity(self, entity: dict[str, Any]) -> None:
        """Add entity to graph."""
        entity_id = entity.get("id", entity.get("name", ""))
        if not entity_id:
            return

        entity_type = entity.get("entity_type", "unknown")
        graph_type = ENTITY_TYPE_MAP.get(entity_type, entity_type)

        if entity_id not in self._nodes:
            self._nodes[entity_id] = GraphNode(
                id=entity_id,
                label=entity.get("name", entity_id),
                type=graph_type,
                confidence=entity.get("confidence", 0.5),
                evidence=entity.get("evidence", []),
                metadata=entity.get("metadata", {}),
            )

        # Process relationships
        for rel in entity.get("relationships", []):
            target = rel.get("related_to", "")
            if target:
                self._edges.append(
                    GraphEdge(
                        source=entity_id,
                        target=target,
                        relationship=rel.get("relationship_type", "related_to"),
                        confidence=entity.get("confidence", 0.5),
                    ),
                )

    def _deduplicate_nodes(self) -> None:
        """Merge duplicate nodes by label similarity."""
        # Simple deduplication: if labels are similar, merge
        to_remove = set()
        for id1, node1 in self._nodes.items():
            for id2, node2 in self._nodes.items():
                if id1 != id2 and self._labels_match(node1.label, node2.label):
                    # Merge into node1
                    node1.evidence.extend(node2.evidence)
                    node1.confidence = max(node1.confidence, node2.confidence)
                    to_remove.add(id2)

        for id2 in to_remove:
            del self._nodes[id2]

    def _labels_match(self, label1: str, label2: str) -> bool:
        """Check if two labels refer to the same entity."""
        # Normalize for comparison
        norm1 = label1.lower().strip("@")
        norm2 = label2.lower().strip("@")

        if norm1 == norm2:
            return True
        if norm1 in norm2 or norm2 in norm1:
            return True
        return False

    def filter_graph(
        self,
        graph: GraphResponse,
        entity_types: list[str] | None = None,
        confidence_threshold: float = 0.0,
        search: str | None = None,
    ) -> GraphResponse:
        """Filter graph by type, confidence, and search.

        Args:
            graph: Original graph
            entity_types: List of entity types to include
            confidence_threshold: Minimum confidence
            search: Search query for node labels

        Returns:
            Filtered graph
        """
        filtered_nodes = []
        filtered_edges = []

        for node in graph.nodes:
            if entity_types and node.type not in entity_types:
                continue
            if node.confidence < confidence_threshold:
                continue
            if search and search.lower() not in node.label.lower():
                continue
            filtered_nodes.append(node)

        # Keep only edges between filtered nodes
        node_ids = {n.id for n in filtered_nodes}
        for edge in graph.edges:
            if edge.source in node_ids and edge.target in node_ids:
                filtered_edges.append(edge)

        return GraphResponse(nodes=filtered_nodes, edges=filtered_edges)
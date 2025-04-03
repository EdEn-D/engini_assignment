from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class DiagramRequest(BaseModel):
    """Request model for diagram generation"""
    description: str = Field(..., description="Natural language description of the diagram to generate")

# Schemas for diagram generation
class Node(BaseModel):
    id: str = Field(..., description="Unique identifier for the node")
    type: str = Field(..., description="Type of node (e.g., EC2, Lambda, RDS)")
    label: Optional[str] = Field(None, description="Display name for the node")

class Edge(BaseModel):
    source: str = Field(..., description="Source node id")
    target: str = Field(..., description="Target node id")

class Cluster(BaseModel):
    id: str = Field(..., description="Unique identifier for the cluster")
    label: str = Field(..., description="Display name for the cluster")
    nodes: List[str] = Field(..., description="List of node ids that belong to this cluster")

class DiagramSchema(BaseModel):
    name: str = Field(..., description="Name of the diagram")
    nodes: List[Node] = Field(default_factory=list, description="List of nodes in the diagram")
    edges: List[Edge] = Field(default_factory=list, description="List of edges connecting nodes")
    clusters: Optional[List[Cluster]] = Field(default_factory=list, description="Optional list of node clusters/groups")

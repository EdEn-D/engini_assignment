from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

# Schemas for diagram generation
class DiagramRequest(BaseModel):
    """Request model for diagram generation"""
    description: str = Field(..., description="Natural language description of the diagram to generate")

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

# Schemas for assistant endpoint
class AssistantRequest(BaseModel):
    """Request model for the assistant endpoint"""
    message: str = Field(..., 
        description="User message for the assistant")
    context: Optional[List[Dict[str, Any]]] = Field(None, 
        description="Previous conversation context as a list of message exchanges")
    
class AssistantResponse(BaseModel):
    """Response model for the assistant endpoint"""
    message: str = Field(..., 
        description="Assistant's response message")
    invoke_diagram_generation: Optional[str] = Field(None,
        description="When this is set, the assistant will invoke diagram generation tool with this diagram description")
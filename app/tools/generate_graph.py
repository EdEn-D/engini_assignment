from typing import Dict, Any, Optional
import os
import asyncio
from diagrams import Diagram, Cluster

# Import all node types at import time
from diagrams.aws.compute import EC2, Lambda
from diagrams.aws.database import RDS, ElastiCache, Dynamodb
from diagrams.aws.storage import S3
from diagrams.aws.network import ELB, ALB, VPC, APIGateway
from diagrams.aws.management import Cloudwatch
from diagrams.aws.security import WAF
from diagrams.aws.integration import SQS, SNS
from diagrams.programming.framework import Fastapi

# Create a mapping of string names to actual classes
NODE_CLASSES = {
    "ec2": EC2,
    "lambda": Lambda,
    "rds": RDS,
    "elasticache": ElastiCache,
    "dynamodb": Dynamodb,
    "s3": S3,
    "elb": ELB,
    "alb": ALB,
    "vpc": VPC,
    "cloudwatch": Cloudwatch,
    "waf": WAF,
    "apigateway": APIGateway,
    "sqs": SQS,
    "sns": SNS,
    "fastapi": Fastapi,
}


async def parse_diagram_schema(
    schema: Dict[str, Any], output_dir: Optional[str] = None
) -> str:
    """Parse a schema and create a diagram with nodes and edges asynchronously.

    Args:
        schema: Dictionary containing diagram definition
        output_dir: Directory to save the diagram (creates temp dir if None)

    Returns:
        str: Path to the generated diagram file
    """

    # Extract diagram attributes
    diagram_name = schema.get("name", "Architecture Diagram")
    diagram_attrs = schema.get("attributes", {})

    # Default diagram attributes
    attrs = {
        "show": True,
        "direction": "LR",
        "outformat": "png",
        "filename": os.path.join(output_dir, diagram_name.replace(" ", "_").lower()),
    }
    attrs.update(diagram_attrs)

    # Dictionary to store node objects by ID
    node_objects = {}

    # Dictionary to store cluster objects by ID
    cluster_objects = {}

    def get_node_class(node_type: str):
        """Get the appropriate node class based on node type."""
        node_type_lower = node_type.lower()
        if node_type_lower in NODE_CLASSES:
            return NODE_CLASSES[node_type_lower]
        else:
            available_types = ", ".join(NODE_CLASSES.keys())
            raise ValueError(
                f"Unsupported node type: {node_type}. Available types: {available_types}"
            )

    # Prepare the expected output path
    output_path = f"{attrs['filename']}.{attrs['outformat']}"

    # Define the diagram creation function
    def create_diagram():
        # Create the diagram
        with Diagram(diagram_name, **attrs):
            # Process clusters first to establish hierarchy
            for cluster_def in schema.get("clusters", []):
                cluster_id = cluster_def["id"]
                cluster_label = cluster_def.get("label", cluster_id)
                cluster_objects[cluster_id] = Cluster(cluster_label)

            # Map nodes to their clusters
            node_to_cluster = {}
            for cluster_def in schema.get("clusters", []):
                cluster_id = cluster_def["id"]
                for node_id in cluster_def.get("nodes", []):
                    node_to_cluster[node_id] = cluster_id

            # Create all nodes
            for node in schema.get("nodes", []):
                node_id = node["id"]
                node_type = node["type"]
                node_label = node.get("label", node_id)

                # Get the node class
                NodeClass = get_node_class(node_type)

                # Check if this node belongs to a cluster
                if node_id in node_to_cluster:
                    cluster_id = node_to_cluster[node_id]
                    with cluster_objects[cluster_id]:
                        node_objects[node_id] = NodeClass(node_label)
                else:
                    # Create node without a cluster
                    node_objects[node_id] = NodeClass(node_label)

            # Create all edges
            for edge_def in schema.get("edges", []):
                source_id = edge_def["source"]
                target_id = edge_def["target"]

                if source_id not in node_objects or target_id not in node_objects:
                    print(
                        f"Warning: Edge refers to undefined node: {source_id} -> {target_id}"
                    )
                    continue

                source = node_objects[source_id]
                target = node_objects[target_id]

                source >> target

        return output_path

    try:
        # Run CPU-bound operation in a thread pool to avoid blocking the event loop
        result = await asyncio.to_thread(create_diagram)
        return result

    except Exception as e:
        # If diagram creation fails, clean up any partially created file
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
                print(f"Removed incomplete diagram file: {output_path}")
            except OSError:
                print(f"Failed to remove incomplete diagram file: {output_path}")
        # Re-raise the original exception
        raise

import pytest
import os
from unittest.mock import patch, MagicMock
from app.tools.generate_graph import DiagramGenerator, parse_diagram_schema


class TestDiagramGenerator:
    """Tests for the DiagramGenerator class"""

    def test_init(self):
        """Test initialization of DiagramGenerator"""
        # Execute
        generator = DiagramGenerator()

        # Assert
        assert generator.graph is not None
        assert generator.node_renderers is not None

    def test_add_node(self):
        """Test adding node to the graph"""
        # Setup
        generator = DiagramGenerator()
        node_data = {"id": "test_node", "type": "EC2", "label": "Test Node"}

        # Execute
        node = generator.add_node(node_data)

        # Assert
        assert node is not None
        assert generator.graph.has_node(node)

    def test_add_invalid_node_type(self):
        """Test adding node with invalid type"""
        # Setup
        generator = DiagramGenerator()
        node_data = {"id": "test_node", "type": "INVALID", "label": "Test Node"}

        # Execute & Assert
        with pytest.raises(ValueError) as excinfo:
            generator.add_node(node_data)

        assert "Unsupported node type" in str(excinfo.value)

    def test_add_edge(self):
        """Test adding edge between nodes"""
        # Setup
        generator = DiagramGenerator()
        node1 = generator.add_node({"id": "node1", "type": "EC2", "label": "Node 1"})
        node2 = generator.add_node({"id": "node2", "type": "RDS", "label": "Node 2"})

        # Execute
        edge = generator.add_edge({"source": "node1", "target": "node2"})

        # Assert
        assert edge is not None
        assert generator.graph.has_edge(node1, node2)

    def test_add_edge_missing_node(self):
        """Test adding edge with missing node"""
        # Setup
        generator = DiagramGenerator()
        generator.add_node({"id": "node1", "type": "EC2", "label": "Node 1"})

        # Execute & Assert
        with pytest.raises(KeyError) as excinfo:
            generator.add_edge({"source": "node1", "target": "missing_node"})

        assert "missing_node" in str(excinfo.value)

    def test_add_cluster(self):
        """Test adding a cluster"""
        # Setup
        generator = DiagramGenerator()
        generator.add_node({"id": "node1", "type": "EC2", "label": "Node 1"})
        generator.add_node({"id": "node2", "type": "EC2", "label": "Node 2"})
        cluster_data = {
            "id": "cluster1",
            "label": "Test Cluster",
            "nodes": ["node1", "node2"],
        }

        # Execute
        cluster = generator.add_cluster(cluster_data)

        # Assert
        assert cluster is not None
        assert len(cluster.nodes) == 2

    def test_add_cluster_with_missing_node(self):
        """Test adding a cluster with a missing node"""
        # Setup
        generator = DiagramGenerator()
        generator.add_node({"id": "node1", "type": "EC2", "label": "Node 1"})
        cluster_data = {
            "id": "cluster1",
            "label": "Test Cluster",
            "nodes": ["node1", "missing_node"],
        }

        # Execute & Assert
        with pytest.raises(KeyError) as excinfo:
            generator.add_cluster(cluster_data)

        assert "missing_node" in str(excinfo.value)

    @patch("app.tools.generate_graph.DiagramGenerator.render")
    def test_generate(self, mock_render):
        """Test the generate method"""
        # Setup
        mock_render.return_value = "test_output.png"
        generator = DiagramGenerator()

        diagram_data = {
            "name": "Test Diagram",
            "nodes": [
                {"id": "node1", "type": "EC2", "label": "Node 1"},
                {"id": "node2", "type": "RDS", "label": "Node 2"},
            ],
            "edges": [{"source": "node1", "target": "node2"}],
        }

        # Execute
        output_path = generator.generate(diagram_data, "test_dir")

        # Assert
        assert output_path == "test_output.png"
        mock_render.assert_called_once_with("test_dir", "Test Diagram")


@patch("app.tools.generate_graph.DiagramGenerator")
async def test_parse_diagram_schema(mock_diagram_generator):
    """Test parse_diagram_schema function"""
    # Setup
    mock_instance = MagicMock()
    mock_diagram_generator.return_value = mock_instance
    mock_instance.generate.return_value = "test_output.png"

    diagram_schema = {"name": "Test Diagram", "nodes": [{"id": "node1", "type": "EC2"}]}

    # Execute
    result = await parse_diagram_schema(diagram_schema, "test_dir")

    # Assert
    assert result == "test_output.png"
    mock_instance.generate.assert_called_once_with(diagram_schema, "test_dir")

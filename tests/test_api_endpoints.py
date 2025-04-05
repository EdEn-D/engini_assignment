import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import os
import json
from app.main import app
from app.api.v1.router import router, diagram_agent, assistant_agent
from app.agents.digram_generating_agent import DiagramGenerationError
from app.schemas.diagram import DiagramRequest, AssistantRequest


# Create test client
client = TestClient(app)


class TestAPIEndpoints:
    """Tests for the API endpoints"""

    @patch("app.api.v1.router.diagram_agent.generate_diagram_structure")
    @patch("app.api.v1.router.parse_diagram_schema")
    async def test_generate_diagram_success(
        self, mock_parse_schema, mock_generate_structure
    ):
        """Test successful diagram generation endpoint"""
        # Setup mocks
        mock_generate_structure.return_value = {
            "nodes": [{"id": "node1", "type": "EC2"}]
        }
        mock_parse_schema.return_value = "test_diagram.png"

        # Execute
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/generate-diagram",
                json={"description": "Create an EC2 instance"},
            )

        # Assert
        assert response.status_code == 200
        mock_generate_structure.assert_called_once_with("Create an EC2 instance")
        mock_parse_schema.assert_called_once()

    @patch("app.api.v1.router.diagram_agent.generate_diagram_structure")
    async def test_generate_diagram_empty_description(self, mock_generate_structure):
        """Test diagram generation with empty description"""
        # Setup mock
        mock_generate_structure.side_effect = ValueError("Description cannot be empty")

        # Execute
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/generate-diagram",
                json={"description": ""},
            )

        # Assert
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()

    @patch("app.api.v1.router.diagram_agent.generate_diagram_structure")
    async def test_generate_diagram_unsupported_node(self, mock_generate_structure):
        """Test diagram generation with unsupported node type"""
        # Setup mock
        mock_generate_structure.side_effect = ValueError(
            "Unsupported node type: InvalidNode"
        )

        # Execute
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/generate-diagram",
                json={"description": "Create an invalid diagram"},
            )

        # Assert
        assert response.status_code == 400
        assert "unsupported components" in response.json()["detail"].lower()

    @patch("app.api.v1.router.diagram_agent.generate_diagram_structure")
    async def test_generate_diagram_server_error(self, mock_generate_structure):
        """Test diagram generation with server error"""
        # Setup mock
        mock_generate_structure.side_effect = Exception("Internal server error")

        # Execute
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/generate-diagram",
                json={"description": "Create a diagram"},
            )

        # Assert
        assert response.status_code == 500
        assert "error generating diagram" in response.json()["detail"].lower()

    @patch("app.api.v1.router.assistant_agent.invoke_assistant")
    async def test_assistant_success(self, mock_invoke_assistant):
        """Test successful assistant endpoint"""
        # Setup mock
        mock_invoke_assistant.return_value = {
            "message": "I'll help you create a diagram.",
            "invoke_diagram_generation": None,
        }

        # Execute
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/assistant",
                json={"message": "Can you help me create a diagram?"},
            )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == "I'll help you create a diagram."
        mock_invoke_assistant.assert_called_once()

    @patch("app.api.v1.router.assistant_agent.invoke_assistant")
    async def test_assistant_empty_message(self, mock_invoke_assistant):
        """Test assistant with empty message"""
        # Execute
        with TestClient(app) as client:
            response = client.post("/api/v1/assistant", json={"message": ""})

        # Assert
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()
        mock_invoke_assistant.assert_not_called()

    @patch("app.api.v1.router.assistant_agent.invoke_assistant")
    async def test_assistant_diagram_generation_error(self, mock_invoke_assistant):
        """Test assistant with diagram generation error"""
        # Setup mock
        mock_invoke_assistant.side_effect = DiagramGenerationError(
            "Failed to generate diagram"
        )

        # Execute
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/assistant", json={"message": "Create a diagram for me"}
            )

        # Assert
        assert response.status_code == 400
        assert "unable to generate diagram" in response.json()["message"].lower()

    @patch("app.api.v1.router.assistant_agent.invoke_assistant")
    async def test_assistant_server_error(self, mock_invoke_assistant):
        """Test assistant with server error"""
        # Setup mock
        mock_invoke_assistant.side_effect = Exception("Internal server error")

        # Execute
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/assistant", json={"message": "Help me with a diagram"}
            )

        # Assert
        assert response.status_code == 500
        assert "unexpected error" in response.json()["message"].lower()

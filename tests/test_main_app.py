import pytest
from fastapi.testclient import TestClient
import os
import shutil
from unittest.mock import patch, MagicMock
from app.main import app, lifespan


class TestMainApp:
    """Tests for the main FastAPI application"""

    def test_root_endpoint(self):
        """Test the root endpoint returns correct information"""
        with TestClient(app) as client:
            response = client.get("/")

            # Assert response is successful
            assert response.status_code == 200

            # Assert response contains expected data
            data = response.json()
            assert "message" in data
            assert "Welcome to the Diagram Generator API" in data["message"]
            assert "docs" in data
            assert "version" in data
            assert "status" in data
            assert data["status"] == "operational"

    def test_health_endpoint(self):
        """Test the health check endpoint"""
        with TestClient(app) as client:
            response = client.get("/health")

            # Assert response is successful
            assert response.status_code == 200

            # Assert response contains expected data
            data = response.json()
            assert "status" in data
            assert data["status"] == "healthy"
            assert "timestamp" in data
            assert "services" in data
            assert "api" in data["services"]

    @patch("app.main.os.makedirs")
    @patch("app.main.shutil.rmtree")
    @patch("app.main.os.path.exists")
    async def test_lifespan(self, mock_exists, mock_rmtree, mock_makedirs):
        """Test application lifespan creates and removes temp directory"""
        # Setup mocks
        mock_exists.return_value = True
        mock_app = MagicMock()

        # Execute lifespan context manager
        async with lifespan(mock_app):
            # Assert temp directory was created
            mock_makedirs.assert_called_once()

        # Assert temp directory was removed after context exit
        mock_exists.assert_called_once()
        mock_rmtree.assert_called_once()

    @patch("app.main.os.makedirs")
    async def test_lifespan_makedirs_error(self, mock_makedirs):
        """Test lifespan handles error during directory creation"""
        # Setup mock to raise exception
        mock_makedirs.side_effect = PermissionError("Permission denied")
        mock_app = MagicMock()

        # Execute & Assert
        with pytest.raises(PermissionError):
            async with lifespan(mock_app):
                pass

        # Verify makedirs was called
        mock_makedirs.assert_called_once()

    @patch("app.main.os.makedirs")
    @patch("app.main.shutil.rmtree")
    @patch("app.main.os.path.exists")
    async def test_lifespan_rmtree_error(self, mock_exists, mock_rmtree, mock_makedirs):
        """Test lifespan handles error during directory cleanup"""
        # Setup mocks
        mock_exists.return_value = True
        mock_rmtree.side_effect = PermissionError("Permission denied")
        mock_app = MagicMock()

        # Execute
        # Should not raise exception even if cleanup fails
        async with lifespan(mock_app):
            pass

        # Verify calls were made
        mock_makedirs.assert_called_once()
        mock_exists.assert_called_once()
        mock_rmtree.assert_called_once()

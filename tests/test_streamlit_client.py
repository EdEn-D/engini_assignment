import pytest
from unittest.mock import patch, MagicMock
import json
import base64
import io
import requests
from streamlit.client import generate_response, generate_diagram, process_messages


class TestStreamlitClient:
    """Tests for the Streamlit client functions"""

    def test_process_messages(self):
        """Test processing messages for API serialization"""
        # Setup test messages
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
            {
                "role": "user",
                "content": {"image": "image_data", "text": "Image caption"},
            },
        ]

        # Execute
        processed = process_messages(messages)

        # Assert
        assert len(processed) == 3
        assert processed[0] == {"role": "user", "content": "Hello"}
        assert processed[1] == {"role": "assistant", "content": "Hi there"}
        assert (
            processed[2]["content"] == "[Generated Image]"
        )  # Image content is converted to placeholder

    @patch("streamlit.client.requests.post")
    def test_generate_diagram_success(self, mock_post):
        """Test successful diagram generation"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"image_data"
        mock_post.return_value = mock_response

        # Execute
        result = generate_diagram({"description": "test diagram"})

        # Assert
        assert result == base64.b64encode(b"image_data").decode("utf-8")
        mock_post.assert_called_once()

    @patch("streamlit.client.requests.post")
    def test_generate_diagram_error(self, mock_post):
        """Test diagram generation with error response"""
        # Setup mock error response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Invalid diagram data"
        mock_post.return_value = mock_response

        # Execute
        result = generate_diagram({"description": "invalid diagram"})

        # Assert
        assert result is None
        mock_post.assert_called_once()

    @patch("streamlit.client.requests.post")
    def test_generate_diagram_exception(self, mock_post):
        """Test diagram generation with exception"""
        # Setup mock to raise exception
        mock_post.side_effect = requests.RequestException("Connection error")

        # Execute
        result = generate_diagram({"description": "test diagram"})

        # Assert
        assert result is None
        mock_post.assert_called_once()

    @patch("streamlit.client.requests.post")
    def test_generate_response_success(self, mock_post):
        """Test successful response generation"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": "Here's a response",
            "invoke_diagram_generation": None,
        }
        mock_post.return_value = mock_response

        # Setup message list
        messages = [{"role": "user", "content": "Hello"}]

        # Execute
        result = generate_response(messages)

        # Assert
        assert result["type"] == "text"
        assert result["message"] == "Here's a response"
        mock_post.assert_called_once()

    @patch("streamlit.client.requests.post")
    @patch("streamlit.client.generate_diagram")
    def test_generate_response_with_diagram(self, mock_generate_diagram, mock_post):
        """Test response generation with diagram"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": "Here's a diagram",
            "invoke_diagram_generation": {"description": "test diagram"},
        }
        mock_post.return_value = mock_response

        # Setup diagram generation mock
        mock_generate_diagram.return_value = "base64_encoded_image"

        # Setup message list
        messages = [{"role": "user", "content": "Create a diagram"}]

        # Execute
        result = generate_response(messages)

        # Assert
        assert result["type"] == "diagram"
        assert result["message"] == "Here's a diagram"
        assert result["image"] == "base64_encoded_image"
        mock_post.assert_called_once()
        mock_generate_diagram.assert_called_once_with({"description": "test diagram"})

    @patch("streamlit.client.requests.post")
    def test_generate_response_error(self, mock_post):
        """Test response generation with error"""
        # Setup mock error response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Server error"
        mock_post.return_value = mock_response

        # Setup message list
        messages = [{"role": "user", "content": "Hello"}]

        # Execute
        result = generate_response(messages)

        # Assert
        assert result["type"] == "text"
        assert "error" in result["message"].lower()
        mock_post.assert_called_once()

    @patch("streamlit.client.requests.post")
    def test_generate_response_timeout(self, mock_post):
        """Test response generation with timeout"""
        # Setup mock to raise timeout
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")

        # Setup message list
        messages = [{"role": "user", "content": "Hello"}]

        # Execute
        result = generate_response(messages)

        # Assert
        assert result["type"] == "text"
        assert "too long to respond" in result["message"].lower()
        mock_post.assert_called_once()

    @patch("streamlit.client.requests.post")
    def test_generate_response_connection_error(self, mock_post):
        """Test response generation with connection error"""
        # Setup mock to raise connection error
        mock_post.side_effect = requests.exceptions.ConnectionError(
            "Connection refused"
        )

        # Setup message list
        messages = [{"role": "user", "content": "Hello"}]

        # Execute
        result = generate_response(messages)

        # Assert
        assert result["type"] == "text"
        assert "unable to connect" in result["message"].lower()
        mock_post.assert_called_once()

import pytest
from unittest.mock import patch, MagicMock
import json
from app.agents.digram_generating_agent import (
    DiagramGeneratingAgent,
    DiagramGenerationError,
)


class TestDiagramGeneratingAgent:
    """Tests for the DiagramGeneratingAgent class"""

    @patch("app.agents.digram_generating_agent.ChatOpenAI")
    def test_init(self, mock_chat_openai):
        """Test agent initialization"""
        # Setup
        mock_instance = MagicMock()
        mock_chat_openai.return_value = mock_instance

        # Execute
        agent = DiagramGeneratingAgent(model="test-model")

        # Assert
        mock_chat_openai.assert_called_once_with(model="test-model", temperature=0.0)
        assert agent.llm == mock_instance

    @pytest.mark.parametrize(
        "response_content,expected",
        [
            # Test case 1: Valid JSON
            (
                '{"name": "Test", "nodes": [{"id": "node1", "type": "EC2"}]}',
                {"name": "Test", "nodes": [{"id": "node1", "type": "EC2"}]},
            ),
            # Test case 2: JSON in markdown
            (
                '```json\n{"name": "Test", "nodes": [{"id": "node1", "type": "EC2"}]}\n```',
                {"name": "Test", "nodes": [{"id": "node1", "type": "EC2"}]},
            ),
            # Test case 3: Dictionary in text
            (
                'Here is the diagram:\n{"name": "Test", "nodes": [{"id": "node1", "type": "EC2"}]}',
                {"name": "Test", "nodes": [{"id": "node1", "type": "EC2"}]},
            ),
        ],
    )
    def test_parse_llm_response_success(self, response_content, expected):
        """Test successful parsing of LLM responses in different formats"""
        # Setup
        agent = DiagramGeneratingAgent()
        mock_response = MagicMock()
        mock_response.content = response_content

        # Execute
        result = agent._parse_llm_response(mock_response)

        # Assert
        assert result == expected

    def test_parse_llm_response_failure(self):
        """Test parsing failure with invalid response"""
        # Setup
        agent = DiagramGeneratingAgent()
        mock_response = MagicMock()
        mock_response.content = "Not a valid JSON or dictionary format"

        # Execute & Assert
        with pytest.raises(DiagramGenerationError) as excinfo:
            agent._parse_llm_response(mock_response)

        assert "Could not parse the diagram structure" in str(excinfo.value)

    @pytest.mark.parametrize(
        "structure,expected_valid",
        [
            # Valid structure
            (
                {
                    "nodes": [
                        {"id": "node1", "type": "EC2"},
                        {"id": "node2", "type": "RDS"},
                    ],
                    "edges": [{"source": "node1", "target": "node2"}],
                },
                True,
            ),
            # Missing nodes
            ({"edges": [{"source": "node1", "target": "node2"}]}, False),
            # Nodes not a list
            ({"nodes": "not a list"}, False),
            # Node missing id
            ({"nodes": [{"type": "EC2"}]}, False),
            # Node missing type
            ({"nodes": [{"id": "node1"}]}, False),
            # Invalid edge source
            (
                {
                    "nodes": [{"id": "node1", "type": "EC2"}],
                    "edges": [{"target": "node2"}],
                },
                False,
            ),
        ],
    )
    def test_validate_diagram_structure(self, structure, expected_valid):
        """Test validation of diagram structures"""
        # Setup
        agent = DiagramGeneratingAgent()

        # Execute & Assert
        if expected_valid:
            # Should not raise exception
            agent._validate_diagram_structure(structure)
        else:
            with pytest.raises(ValueError):
                agent._validate_diagram_structure(structure)

    @patch(
        "app.agents.digram_generating_agent.DiagramGeneratingAgent._parse_llm_response"
    )
    @patch("app.agents.digram_generating_agent.ChatPromptTemplate.from_messages")
    @patch("app.agents.digram_generating_agent.ChatOpenAI")
    async def test_generate_diagram_structure(self, mock_chat, mock_prompt, mock_parse):
        """Test the diagram structure generation workflow"""
        # Setup mock responses
        mock_llm = MagicMock()
        mock_chat.return_value = mock_llm

        mock_chain = MagicMock()
        # Configure the mocked chain's ainvoke to return a result
        mock_result = {"nodes": [{"id": "test", "type": "EC2"}]}
        mock_chain.ainvoke.return_value = mock_result

        # Patch the agent's chain attribute
        with patch.object(DiagramGeneratingAgent, "chain", mock_chain):
            agent = DiagramGeneratingAgent()

            # Execute
            result = await agent.generate_diagram_structure(
                "Create a diagram with an EC2 instance"
            )

            # Assert
            mock_chain.ainvoke.assert_called_once_with(
                "Create a diagram with an EC2 instance"
            )
            assert result == mock_result

    @pytest.mark.asyncio
    async def test_generate_diagram_structure_empty_description(self):
        """Test handling of empty description"""
        # Setup
        agent = DiagramGeneratingAgent()

        # Execute & Assert
        with pytest.raises(ValueError) as excinfo:
            await agent.generate_diagram_structure("")

        assert "Description cannot be empty" in str(excinfo.value)

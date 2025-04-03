from typing import Dict, Any
import logging
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from openai import OpenAIError

from app.schemas.diagram import DiagramSchema
from .prompts import diagram_generation_system_prompt

load_dotenv(find_dotenv())

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DiagramGenerationError(Exception):
    """Custom exception for diagram generation errors"""

    pass


class DiagramGeneratingAgent:
    """
    Agent responsible for generating diagrams based on text input using an LLM.
    """

    def __init__(self):
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.client = llm.with_structured_output(DiagramSchema)

    def generate_diagram_structure(self, diagram_description: str) -> Dict[str, Any]:
        """
        Generate a diagram based on a natural language description.

        Args:
            diagram_description (str): Natural language description of the diagram to generate.

        Returns:
            Dict[str, Any]: Dictionary containing the generated diagram data.

        Raises:
            DiagramGenerationError: If diagram generation fails
        """
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", diagram_generation_system_prompt),
                ("human", "{input}"),
            ]
        )

        chain = {"input": RunnablePassthrough()} | prompt | self.client

        try:
            logger.info("Attempting diagram generation")
            response = chain.invoke(diagram_description)
            diagram_dict = response.model_dump()
            logger.info("Diagram generation successful")
            return diagram_dict
        
        except OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise DiagramGenerationError(
                f"Failed to generate diagram due to API error: {str(e)}"
            ) from e
        except Exception as e:
            logger.error(f"Unexpected error during diagram generation: {str(e)}")
            raise DiagramGenerationError(
                f"Unexpected error during diagram generation: {str(e)}"
            ) from e

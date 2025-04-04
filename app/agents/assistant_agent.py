from typing import Dict, Any
import logging
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from openai import OpenAIError

from app.schemas.diagram import AssistantRequest, AssistantResponse
from .prompts import assistant_system_prompt

load_dotenv(find_dotenv())

logger = logging.getLogger(__name__)


class AssistantError(Exception):
    """Custom exception for assistant processing errors"""

    pass


class AssistantAgent:
    """
    Chat agent responsible for helping users create diagrams.
    """

    def __init__(self):
        llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
        self.client = llm.with_structured_output(AssistantResponse)

    async def invoke_assistant(self, messages: AssistantRequest) -> Dict[str, Any]:
        chat_history = messages.context or []

        # Format messages in the structure expected by the OpenAI API
        formatted_messages = [{"role": "system", "content": assistant_system_prompt}]

        # Add chat history
        if chat_history:
            for message in chat_history:
                formatted_messages.append(message)

        # Add the current user message
        formatted_messages.append({"role": "user", "content": messages.message})

        try:
            logger.info("Invoking assistant")
            response = await self.client.ainvoke(formatted_messages)
            response_dict = response.model_dump()
            # turn to str
            response_str = str(response_dict)
            logger.info("Assistant response generated successfully")
            return response_str

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise AssistantError(
                f"Failed to generate assistant response due to API error: {str(e)}"
            ) from e
        except Exception as e:
            logger.error(f"Unexpected error during assistant processing: {str(e)}")
            raise AssistantError(
                f"Unexpected error during assistant processing: {str(e)}"
            ) from e

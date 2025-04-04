import os
import requests
import logging
import sys
from dotenv import load_dotenv
import json
from io import BytesIO
import ast
import base64

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s: %(name)s > %(filename)s > %(funcName)s:%(lineno)d ~ %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# API configuration from environment variables
API_DOMAIN = os.getenv("API_DOMAIN", "localhost")
API_PORT = os.getenv("API_PORT", "8000")

# Construct the API base URL with hard-coded HTTP protocol
API_BASE_URL = f"http://{API_DOMAIN}:{API_PORT}"
API_ASSISTANT_ENDPOINT = f"{API_BASE_URL}/api/v1/assistant"
API_DIAGRAM_ENDPOINT = f"{API_BASE_URL}/api/v1/generate-diagram"

logger.info(f"API Base URL constructed as: {API_BASE_URL}")


def process_messages(message_list):
    """
    Process messages to ensure they're JSON serializable

    Args:
        message_list (list): The conversation history

    Returns:
        list: Processed messages that are JSON serializable
    """
    processed_messages = []

    for msg in message_list:
        processed_msg = {"role": msg["role"]}

        # Check if content contains image data and convert to text representation
        if isinstance(msg["content"], dict) and "image" in msg["content"]:
            # Create a text representation that mentions there was an image
            processed_msg["content"] = "[Generated Image]"
        else:
            # Text messages are already serializable
            processed_msg["content"] = msg["content"]

        processed_messages.append(processed_msg)

    return processed_messages


def generate_diagram(diagram_data):
    """
    Generate a diagram by calling the generate-diagram API endpoint.

    Args:
        diagram_data: The description to pass to the diagram generation endpoint

    Returns:
        BytesIO: The generated image as BytesIO object or None if error occurs
    """
    logger.info("Calling diagram generation endpoint")
    try:
        headers = {"accept": "*/*", "Content-Type": "application/json"}

        # Create the payload with the description
        payload = {"description": diagram_data}

        # Make the API request to the diagram endpoint
        logger.info(f"Sending request to diagram API at: {API_DIAGRAM_ENDPOINT}")
        response = requests.post(API_DIAGRAM_ENDPOINT, json=payload, headers=headers)

        if response.status_code == 200:
            # Convert the response content (image) to BytesIO
            image_bytes = BytesIO(response.content)
            return image_bytes
        else:
            error_msg = f"API request to Diagram API failed with status code {response.status_code}: {response.text}"
            logger.error(error_msg)
            return None
    except Exception as e:
        logger.error(f"Error generating diagram: {str(e)}", exc_info=True)
        return None


def generate_response(message_list):
    """
    Send user message to the API and return the generated response.

    Args:
        message_list (list): The conversation history

    Returns:
        dict: Contains the response message and possibly an image (as BytesIO)
    """
    logger.info("Generating response from assistant API...")
    try:
        headers = {"accept": "*/*", "Content-Type": "application/json"}

        # Process messages to ensure JSON serializable content
        processed_messages = process_messages(message_list)

        # Prepare the payload with processed messages
        payload = {
            "message": processed_messages[-1]["content"],
            "context": processed_messages[:-1],
        }

        # Make the API request
        logger.info(f"Sending request to API at: {API_ASSISTANT_ENDPOINT}")
        response = requests.post(API_ASSISTANT_ENDPOINT, json=payload, headers=headers)

        # Check for successful response
        if response.status_code == 200:
            result = response.json()
            # logger.info(f"Response JSON: {result}")

            # Parse the response
            if isinstance(result, str):
                parsed_result = ast.literal_eval(result)
            else:
                parsed_result = result

            message = parsed_result.get(
                "message", "Sorry, I couldn't generate a response."
            )
            invoke_diagram = parsed_result.get("invoke_diagram_generation")

            # Check if diagram generation is needed
            if invoke_diagram is not None:
                # Call diagram generation function
                diagram_image = generate_diagram(invoke_diagram)
                # Return both the message and image (if diagram generation was successful)
                if diagram_image:
                    return {
                        "type": "diagram",
                        "message": message,
                        "image": diagram_image,
                    }
                else:
                    return {
                        "type": "text",
                        "message": message + "\n(Note: Diagram generation failed)",
                    }
            else:
                # Return just the message
                return {"type": "text", "message": message}
        else:
            error_msg = f"API request to Assistant API failed with status code {response.status_code}: {response.text}"
            logger.error(error_msg)
            return {
                "type": "text",
                "message": f"Error: Unable to get a response from the server (Status code: {response.status_code})",
            }

    except Exception as e:
        logger.error(f"Error communicating with API: {str(e)}", exc_info=True)
        error_msg = "Sorry, there was an error communicating with the server."
        return {"type": "text", "message": error_msg}

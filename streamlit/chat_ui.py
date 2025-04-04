import streamlit as st
from dotenv import load_dotenv
import os
import shelve
import argparse
import sys
from pathlib import Path
import logging
from client import generate_response
import base64
from io import BytesIO

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Argument parser to handle command-line arguments
parser = argparse.ArgumentParser(description="Streamlit Chatbot Interface")
parser.add_argument(
    "--title",
    type=str,
    default="Streamlit Chatbot Interface",
    help="Set the title of the app",
)

args = parser.parse_args()


# Use the title argument to set the title of the Streamlit app
st.title(args.title)

logger.info("Streamlit app has started")

USER_AVATAR = "👤"
BOT_AVATAR = "🤖"

# Initialize messages in session state if not present
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        # Check if the message is an image or text
        if message.get("content_type") == "image":
            # Handle the image content - first display the text message
            st.markdown(message["content"]["message"])

            # Then display the image without a caption
            if isinstance(message["content"]["image"], BytesIO):
                st.image(message["content"]["image"])
            elif isinstance(message["content"]["image"], str) and message["content"][
                "image"
            ].startswith("data:image"):
                st.image(message["content"]["image"])
        else:
            st.markdown(message["content"])

# Main chat interface
if prompt := st.chat_input("How can I help?"):
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        # Create a list of messages to pass to generate_response
        message_list = []
        for msg in st.session_state.messages:
            message_list.append({"role": msg["role"], "content": msg["content"]})

        # Pass the message list to generate_response
        response = generate_response(message_list)

        # Handle different response types
        if response["type"] == "diagram":
            # For responses with both text and image, show message as text first
            st.markdown(response["message"])
            # Then display the image without a caption
            st.image(response["image"])
            content_type = "image"

            # Store both the image and message
            full_response = {"image": response["image"], "message": response["message"]}
        else:
            # For text-only responses, display the text directly
            st.markdown(response["message"])
            content_type = "text"
            full_response = response["message"]

    # Add assistant response to session state with appropriate content type
    st.session_state.messages.append(
        {"role": "assistant", "content": full_response, "content_type": content_type}
    )

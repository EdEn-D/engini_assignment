FROM python:3.12-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir ".[frontend]"

# Copy application code
COPY ./streamlit ./streamlit

# Expose port
EXPOSE 8501

# Run the Streamlit application using python -m to ensure proper module resolution
CMD ["streamlit", "run", "streamlit/chat_ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
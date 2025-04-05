FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Run the Streamlit application using python -m to ensure proper module resolution
CMD ["streamlit", "run", "streamlit/chat_ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    graphviz \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy toml file and install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir ".[backend]"

# Copy application code
COPY ./app ./app

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "app.main"]
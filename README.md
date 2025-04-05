# AWS Architecture Diagram Generator

A specialized tool for creating AWS architecture diagrams through natural language descriptions, powered by GPT models and Python Diagrams library.

## Features

- Chat interface for describing AWS architecture
- AI-powered assistant to help refine diagram descriptions
- Automatic diagram generation from descriptions
- Support for common AWS components

## Prerequisites

- Python 3.10 or higher
- [GraphViz](https://graphviz.org/download/) installed on your system
- OpenAI API key

## Setup Instructions

### Environment Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd engini_assignment
   ```

2. Create and activate a virtual environment:

   **Using UV (recommended)**:
   ```
   pip install uv
   uv venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/macOS
   ```

   **Using traditional venv**:
   ```
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/macOS
   ```

3. Install dependencies:

   **Using UV**:
   ```
   uv pip install -r requirements.txt
   ```

   **Using pip**:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Copy the `example.env` file to `.env`
   - Add your OpenAI API key

### Running Locally

1. Start the backend server:
   ```
   python -m app.main
   ```

2. In a separate terminal, start the Streamlit frontend:
   ```
   streamlit run streamlit/chat_ui.py
   ```

3. Access the application at http://localhost:8501

### Running with Docker

1. Make sure Docker and Docker Compose are installed on your system.

2. Build and start the containers:
   ```
   docker-compose up -d
   ```

3. Access the application at http://localhost:8501

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `API_HOST`: Host for the backend server (default: 0.0.0.0)
- `API_PORT`: Port for the backend server (default: 8000)
- `TEMP_DIR`: Directory for temporary files (default: temp)

## System Architecture

- **Frontend**: Streamlit-based chat interface
- **Backend**: FastAPI server with LLM-powered assistant agents
- **Diagram Generation**: Python Diagrams library for creating AWS architecture diagrams

## Available AWS Components

- EC2: Elastic Compute Cloud virtual servers
- Lambda: Serverless compute service
- RDS: Relational Database Service
- ElastiCache: In-memory caching service
- DynamoDB: NoSQL database service
- S3: Simple Storage Service for object storage
- ELB: Elastic Load Balancer (Classic)
- ALB: Application Load Balancer
- VPC: Virtual Private Cloud
- CloudWatch: Monitoring service
- WAF: Web Application Firewall
- APIGateway: API management service
- SQS: Simple Queue Service
- SNS: Simple Notification Service

## Example Usage

### Input (Natural Language Description)
```
Create a web application architecture with an Application Load Balancer distributing traffic to 3 EC2 instances. 
Include an RDS database for persistent storage and an ElastiCache cluster for session management. 
All components should be inside a VPC with proper security groups.
```

### Output
The system will generate an AWS architecture diagram visualizing:
- VPC containing all resources
- Application Load Balancer in a public subnet
- 3 EC2 instances in a private application subnet
- RDS database in a private database subnet
- ElastiCache cluster in the private application subnet
- Appropriate security groups and connections between components

The diagram will be rendered as a PNG image that can be downloaded or shared.

### Advanced Example
```
Design a serverless microservices architecture for an e-commerce platform.
Use API Gateway as the entry point that routes to different Lambda functions for user management, 
product catalog, and order processing. Store product data in DynamoDB, user profiles in another 
DynamoDB table, and order history in S3. Use SQS for order queue and SNS for notifications. 
Implement CloudWatch for monitoring and WAF for security.
```

## License

[MIT License](LICENSE)
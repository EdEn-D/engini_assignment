import logging
import os
import uvicorn
import shutil
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import AsyncIterator
from dotenv import load_dotenv
from app.api.v1.router import router as api_router

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s: %(name)s > %(filename)s > %(funcName)s:%(lineno)d ~ %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Configuration
TEMP_DIR = os.getenv("TEMP_DIR", "temp")

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup code
    logger.info("Starting up server...")
    try:
        os.makedirs(TEMP_DIR, exist_ok=True)
        logger.info(f"Created/verified temporary directory: {TEMP_DIR}")
    except Exception as e:
        logger.error(f"Failed to create temp directory: {str(e)}", exc_info=True)
        raise
    
    yield  # Application runs here
    
    # Shutdown code
    logger.info(f"Server shutting down. Cleaning up temporary directory: {TEMP_DIR}")
    try:
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
            logger.info(f"Successfully removed temporary directory: {TEMP_DIR}")
    except Exception as e:
        logger.error(f"Error cleaning up temporary directory: {str(e)}", exc_info=True)


# Create FastAPI app
app = FastAPI(
    title="Diagram Generator API",
    description="Generate diagrams from natural language descriptions using LLM-powered agents",
    version="0.1.0",
    lifespan=lifespan,
)

# Setup development CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api/v1")


# Root endpoint
@app.get("/")
async def root():
    return JSONResponse(
        status_code=200,
        content={
            "message": "Welcome to the Diagram Generator API",
            "docs": "/docs",
        },
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    return JSONResponse(
        status_code=200,
        content={"status": "healthy"},
    )




if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=True,
    )

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import logging
import os
from app.schemas.diagram import DiagramRequest
from app.agents.digram_generating_agent import DiagramGeneratingAgent
from app.tools.generate_graph import parse_diagram_schema

logger = logging.getLogger(__name__)

router = APIRouter(tags=["diagram-generation"])
diagram_agent = DiagramGeneratingAgent()


@router.post(
    "/generate-diagram",
    summary="Generate a diagram from natural language",
    response_class=FileResponse,
)
async def generate_diagram(request: DiagramRequest):
    """
    Generate a diagram based on a natural language description.

    Returns the diagram image file.
    """
    # Input validation
    if not request.description or not request.description.strip():
        logger.warning("Empty diagram description received")
        raise HTTPException(
            status_code=400, detail="Diagram description cannot be empty"
        )

    logger.info(f"Received diagram generation request: {request.description}")

    try:
        # Generate diagram structure
        diagram_dict = await diagram_agent.generate_diagram_structure(request.description)
        logger.info(f"Generated diagram structure: {diagram_dict}")

        # Generate the actual diagram image
        diagram_path = await parse_diagram_schema(diagram_dict, os.getenv("TEMP_DIR"))
        logger.info(f"Generated diagram at: {diagram_path}")

        # Return the image file
        return FileResponse(
            path=diagram_path,
            media_type="image/png",
            filename=os.path.basename(diagram_path),
        )

    except ValueError as ve:
        # Check if this is an unsupported node type error
        error_msg = str(ve)
        if "Unsupported node type:" in error_msg or "Available types:" in error_msg:
            logger.warning(f"Unsupported node type error: {error_msg}")
            raise HTTPException(
                status_code=400,
                detail=f"Diagram contains unsupported components: {error_msg}",
            )
        else:
            # Other value errors are likely bad input
            logger.warning(f"Invalid input error: {error_msg}")
            raise HTTPException(status_code=400, detail=f"Invalid input: {error_msg}")
    except KeyError as ke:
        # Missing required keys in the diagram structure
        logger.warning(f"Missing key in diagram structure: {str(ke)}")
        raise HTTPException(
            status_code=400,
            detail=f"Missing required element in diagram definition: {str(ke)}",
        )
    except Exception as e:
        # Catch-all for any other exceptions
        logger.error(f"Error generating diagram: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error generating diagram: {str(e)}"
        )

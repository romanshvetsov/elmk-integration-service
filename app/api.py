from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
import structlog
import httpx

from .models import MedicalBookRequest, ExternalAPIResponse, HealthResponse
from .auth import get_current_user
from .external_api import external_api_client
from .config import settings

logger = structlog.get_logger()

router = APIRouter()


@router.get("/healthz", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy")


@router.post("/api/v1/medical-book/validate", response_model=ExternalAPIResponse)
async def validate_medical_book(
    request: MedicalBookRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Validate medical book information.
    
    This endpoint validates the provided ELMK number and SNILS,
    then queries the external registry for medical book information.
    
    Args:
        request: Medical book validation request
        current_user: Authenticated user (from Basic Auth)
        
    Returns:
        ExternalAPIResponse: Medical book information from registry
        
    Raises:
        HTTPException: If validation fails or external API error
    """
    logger.info(
        "Medical book validation request",
        elmk_number=request.elmk_number,
        snils=request.snils,
        user=current_user
    )
    
    try:
        # Get medical book information from external API
        result = await external_api_client.get_medical_book_info(
            elmk_number=request.elmk_number,
            snils=request.snils
        )
        
        logger.info(
            "Medical book validation successful",
            elmk_number=request.elmk_number,
            user=current_user
        )
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions from external API
        raise
    except httpx.HTTPStatusError as e:
        logger.error(
            "External API HTTP error",
            error=str(e),
            status_code=e.response.status_code,
            elmk_number=request.elmk_number,
            user=current_user
        )
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medical book not found in registry"
            )
        elif e.response.status_code >= 500:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"External API error: {e.response.status_code}"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"External API error: {e.response.status_code}"
            )
    except httpx.TimeoutException as e:
        logger.error(
            "External API timeout",
            error=str(e),
            elmk_number=request.elmk_number,
            user=current_user
        )
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="External API timeout"
        )
    except httpx.ConnectError as e:
        logger.error(
            "External API connection error",
            error=str(e),
            elmk_number=request.elmk_number,
            user=current_user
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="External API unavailable"
        )
    except Exception as e:
        logger.error(
            "Unexpected error during medical book validation",
            error=str(e),
            elmk_number=request.elmk_number,
            user=current_user
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during validation"
        )


@router.get("/metrics")
async def get_metrics():
    """Get application metrics (placeholder for Prometheus metrics)."""
    # In a real implementation, this would return Prometheus metrics
    return {
        "status": "metrics endpoint",
        "note": "Prometheus metrics would be implemented here"
    }
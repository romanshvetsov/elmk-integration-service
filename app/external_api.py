import httpx
import structlog
from typing import Optional
from fastapi import HTTPException, status

from .config import settings
from .models import ExternalAPIResponse

logger = structlog.get_logger()


class ExternalAPIClient:
    """Client for external medical book registry API."""
    
    def __init__(self):
        self.base_url = settings.external_api_url
        self.timeout = settings.external_api_timeout
    
    async def get_medical_book_info(
        self, elmk_number: str, snils: str
    ) -> ExternalAPIResponse:
        """
        Get medical book information from external API.
        
        Args:
            elmk_number: Medical book number (12 digits)
            snils: SNILS number (11 digits)
            
        Returns:
            ExternalAPIResponse: Medical book information
            
        Raises:
            HTTPException: If external API request fails
        """
        params = {
            "elmk_number": elmk_number,
            "snils": snils
        }
        
        logger.info(
            "Requesting external API",
            elmk_number=elmk_number,
            snils=snils,
            url=self.base_url
        )
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.base_url, params=params)
                
                logger.info(
                    "External API response received",
                    status_code=response.status_code,
                    elmk_number=elmk_number
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return ExternalAPIResponse(**data)
                elif response.status_code == 404:
                    logger.warning(
                        "Medical book not found",
                        elmk_number=elmk_number,
                        snils=snils
                    )
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Medical book not found in registry"
                    )
                else:
                    logger.error(
                        "External API error",
                        status_code=response.status_code,
                        response_text=response.text[:200],
                        elmk_number=elmk_number
                    )
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"External API error: {response.status_code}"
                    )
                    
        except httpx.TimeoutException:
            logger.error(
                "External API timeout",
                timeout=self.timeout,
                elmk_number=elmk_number
            )
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="External API timeout"
            )
        except httpx.ConnectError as e:
            logger.error(
                "External API connection error",
                error=str(e),
                elmk_number=elmk_number
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="External API unavailable"
            )
        except Exception as e:
            logger.error(
                "Unexpected error during external API call",
                error=str(e),
                elmk_number=elmk_number
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )


# Global client instance
external_api_client = ExternalAPIClient()
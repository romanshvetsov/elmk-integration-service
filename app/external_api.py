import httpx
import structlog
import ssl
import requests
import urllib3
import subprocess
import json
from typing import Optional
from fastapi import HTTPException, status

from .config import settings
from .models import ExternalAPIResponse

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
            # Format ELMK number with dashes (convert 860102797025 to 86-01-027970-25)
            formatted_elmk = f"{elmk_number[:2]}-{elmk_number[2:4]}-{elmk_number[4:10]}-{elmk_number[10:]}"
            
            # Use curl with SSL verification disabled
            url = f"{self.base_url}?elmk_number={formatted_elmk}&snils={snils}"
            result = subprocess.run(
                ["curl", "-k", "-s", url],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            logger.info(
                "External API response received",
                return_code=result.returncode,
                elmk_number=elmk_number
            )
            
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    return ExternalAPIResponse(**data)
                except json.JSONDecodeError:
                    logger.error(
                        "Invalid JSON response",
                        response_text=result.stdout[:200],
                        elmk_number=elmk_number
                    )
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="Invalid response from external API"
                    )
            else:
                logger.error(
                    "External API error",
                    return_code=result.returncode,
                    error_text=result.stderr[:200],
                    elmk_number=elmk_number
                )
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"External API error: {result.returncode}"
                )
                    
        except subprocess.TimeoutExpired:
            logger.error(
                "External API timeout",
                timeout=self.timeout,
                elmk_number=elmk_number
            )
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="External API timeout"
            )
        except FileNotFoundError:
            logger.error(
                "curl not found in system",
                elmk_number=elmk_number
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="External API unavailable - curl not found"
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
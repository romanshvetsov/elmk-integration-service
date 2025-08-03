from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime, timezone
import re


class MedicalBookRequest(BaseModel):
    """Request model for medical book validation."""
    
    elmk_number: str = Field(..., description="Уникальный идентификатор электронной личной медицинской книжки")
    snils: str = Field(..., description="Номер СНИЛС")
    
    @field_validator('elmk_number')
    @classmethod
    def validate_elmk_number(cls, v):
        if not re.match(r'^\d{12}$', v):
            raise ValueError('ELMK number must be exactly 12 digits')
        return v
    
    @field_validator('snils')
    @classmethod
    def validate_snils(cls, v):
        if not re.match(r'^\d{11}$', v):
            raise ValueError('SNILS must be exactly 11 digits')
        return v


class ExternalAPIResponse(BaseModel):
    """Response model from external API."""
    
    elmk_status_name: str
    elmk_number: str
    first_name: str
    last_name: str
    middle_name: str
    snils: str
    work_type: List[str]
    decision_dt: str
    med_opinions_dt: str
    certification_dt: str
    recertification_dt: str
    fbuz_short_name: str
    created_fullname: str


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str
    detail: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "1.0.0"
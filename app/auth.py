from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
import secrets
from typing import Optional
import structlog

from .config import settings

logger = structlog.get_logger()
security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def authenticate_user(credentials: HTTPBasicCredentials) -> bool:
    """Authenticate user with Basic Auth."""
    is_username_correct = secrets.compare_digest(
        credentials.username, settings.basic_auth_username
    )
    is_password_correct = secrets.compare_digest(
        credentials.password, settings.basic_auth_password
    )
    
    if not (is_username_correct and is_password_correct):
        logger.warning(
            "Authentication failed",
            username=credentials.username,
            client_ip="unknown"  # Would be extracted from request in real implementation
        )
        return False
    
    logger.info(
        "Authentication successful",
        username=credentials.username,
        client_ip="unknown"
    )
    return True


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """Dependency for getting current authenticated user."""
    if not authenticate_user(credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
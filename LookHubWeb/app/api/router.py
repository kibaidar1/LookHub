from fastapi import APIRouter, HTTPException, status, Form
from jose import jwt
from datetime import datetime, timedelta, UTC
from app.config import API_KEY, SECRET_KEY, ALGORITHM

from app.api.routers.looks import router as looks_router
from app.api.routers.clothes import router as clothes_router

# Main API router that includes all sub-routers
router = APIRouter(prefix="/api", tags=["API"])

# Include sub-routers for different resources
router.include_router(looks_router)
router.include_router(clothes_router)


@router.post("/token")
async def get_api_token(api_key: str = Form(...)):
    """Returns a JWT token for API access by api_key.
    
    Args:
        api_key (str): API key for service access
    
    Returns:
        dict: Dictionary with access_token and token_type
    
    Raises:
        HTTPException: 401 if the key is invalid
    """
    if api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    expire = datetime.now(UTC) + timedelta(minutes=60)
    to_encode = {"sub": "api_client", "exp": expire}
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

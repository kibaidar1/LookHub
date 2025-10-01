from fastapi import HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.config import SECRET_KEY, ALGORITHM

bearer_scheme = HTTPBearer()


def verify_api_token(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    """Checks JWT token from Authorization header for API.
    
    Args:
        credentials (HTTPAuthorizationCredentials): Bearer token from header
    
    Raises:
        HTTPException: 401 if token is missing or invalid
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("sub") != "api_client":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


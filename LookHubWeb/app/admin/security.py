from fastapi import Request, HTTPException, status
from jose import jwt, JWTError
from app.config import SECRET_KEY, ADMIN_USERNAME, ALGORITHM


async def verify_admin_token(request: Request):
    """Check the presence and validity of the JWT token in the 'admin_token' httpOnly cookie.
    Args:
        request (Request): FastAPI request object
    Raises:
        HTTPException: 401 if token is missing or invalid, 403 if not an admin user
    """
    token = request.cookies.get("admin_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("sub") != ADMIN_USERNAME:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not an admin user")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

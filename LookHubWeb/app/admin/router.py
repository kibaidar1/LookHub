from datetime import datetime, timedelta, UTC
from hmac import compare_digest

import httpx
from fastapi import APIRouter, Request, Depends, Form, Security, Response
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from starlette.templating import Jinja2Templates
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.admin.security import verify_admin_token
from app.config import (SECRET_KEY, ADMIN_USERNAME, ALGORITHM, ADMIN_PASSWORD, ACCESS_TOKEN_EXPIRE_MINUTES, API_KEY, FLOWER_URL)

from app.admin.utils import _proxy_request, _filter_headers, _rewrite_flower_html

# Initialize Jinja2 templates for admin pages
templates = Jinja2Templates(directory="app/admin/templates")

# Router for admin panel endpoints
router = APIRouter(prefix="/admin", tags=["Admin"])

bearer_scheme = HTTPBearer()


def verify_api_token(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    """
    Checks JWT token from Authorization header for API.
    Args:
        credentials (HTTPAuthorizationCredentials): Bearer token from header
    Raises:
        HTTPException: 401 if token is missing or invalid
    """
    token = credentials.credentials
    # ...дальнейшая проверка токена...


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Render the admin login page.
    
    Args:
        request (Request): FastAPI request object
    
    Returns:
        HTMLResponse: Rendered login page
    """
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def admin_login(username: str = Form(...), password: str = Form(...)):
    """Admin login endpoint. Sets JWT token in 'admin_token' httpOnly cookie and returns API token for JS usage.
    
    Args:
        username (str): Admin username
        password (str): Admin password
    
    Returns:
        JSONResponse: Success message, sets cookie, and returns API token if credentials are correct
    
    Raises:
        HTTPException: 401 if credentials are incorrect
    """
    if compare_digest(username, ADMIN_USERNAME) and compare_digest(password, ADMIN_PASSWORD):
        expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        admin_token = jwt.encode({"sub": ADMIN_USERNAME, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
        api_token = jwt.encode({"sub": "api_client", "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
        response = JSONResponse({"message": "Login successful", "api_token": api_token})
        response.set_cookie(
            key="admin_token",
            value=admin_token,
            httponly=True,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax",
            secure=False  # Set True in production
        )
        return response
    return templates.TemplateResponse(
        "login.html", {"request": {}, "error": "Invalid username or password"}, status_code=401
    )


@router.get("/logout")
async def admin_logout():
    """Logout admin: remove cookie and redirect to login page."""
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie("admin_token", path="/")
    return response


@router.get("/", response_class=HTMLResponse, dependencies=[Depends(verify_admin_token)])
async def admin_home(request: Request):
    """Render the admin panel home page.
    
    Args:
        request (Request): FastAPI request object
        
    Returns:
        HTMLResponse: Rendered admin panel home page
    """
    return templates.TemplateResponse("base.html", {"request": request})


@router.get("/clothes", response_class=HTMLResponse, dependencies=[Depends(verify_admin_token)])
async def clothes_list(request: Request):
    """Render the clothes list page.

    Args:
        request (Request): FastAPI request object

    Returns:
        HTMLResponse: Rendered clothes list page
    """
    return templates.TemplateResponse("clothes.html", {"request": request})


@router.get("/clothes/{clothes_id}", response_class=HTMLResponse, dependencies=[Depends(verify_admin_token)])
async def clothes_detail(request: Request, clothes_id: str):
    """Render the clothes detail page.

    Args:
        request (Request): FastAPI request object
        clothes_id (str): ID of the clothes item to display

    Returns:
        HTMLResponse: Rendered clothes detail page
    """
    return templates.TemplateResponse(
        "clothes_detail.html", {"request": request, "clothes_id": clothes_id}
    )


@router.get("/looks", response_class=HTMLResponse, dependencies=[Depends(verify_admin_token)])
async def looks_list(request: Request):
    """Render the looks list page.
    
    Args:
        request (Request): FastAPI request object
        
    Returns:
        HTMLResponse: Rendered looks list page
    """
    return templates.TemplateResponse("looks.html", {"request": request})


@router.get("/looks/{look_id}", response_class=HTMLResponse, dependencies=[Depends(verify_admin_token)])
async def look_detail(request: Request, look_id: str):
    """Render the look detail page.
    
    Args:
        request (Request): FastAPI request object
        look_id (str): ID of the look to display
        
    Returns:
        HTMLResponse: Rendered look detail page
    """
    return templates.TemplateResponse(
        "look_detail.html", {"request": request, "look_id": look_id}
    )


@router.api_route("/flower/", methods=["GET", "POST"], dependencies=[Depends(verify_admin_token)])
async def flower_root(request: Request):
    return await _proxy_request(request, FLOWER_URL)


@router.api_route("/flower/{path:path}", methods=["GET", "POST"], dependencies=[Depends(verify_admin_token)])
async def flower_proxy(path: str, request: Request):
    target = f"{FLOWER_URL}/{path}" if path else FLOWER_URL
    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.request(
            method=request.method,
            url=target,
            content=await request.body(),
            headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
            params=dict(request.query_params),
            timeout=None,
        )

        headers = _filter_headers(dict(resp.headers))
        content_type = resp.headers.get("content-type", "")

        if content_type.startswith("application/json"):
            return JSONResponse(content=resp.json(), status_code=resp.status_code, headers=headers)
        elif content_type.startswith("text/html"):
            text = (await resp.aread()).decode(resp.encoding or "utf-8")
            text = _rewrite_flower_html(text)
            return HTMLResponse(content=text, status_code=resp.status_code, headers=headers)
        else:
            body = await resp.aread()
            return Response(content=body, status_code=resp.status_code, headers=headers)

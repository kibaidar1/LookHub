from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Router for frontend pages
router = APIRouter(prefix="", tags=["Frontend"])

# Initialize Jinja2 templates for frontend pages
templates = Jinja2Templates(directory="app/frontend/templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main page of the application.
    
    This endpoint serves the landing page where users can browse looks and clothes.
    
    Args:
        request (Request): FastAPI request object
        
    Returns:
        HTMLResponse: Rendered main page
    """
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/looks/{look_id}", response_class=HTMLResponse)
async def look_detail(request: Request, look_id: int):
    """Render the look detail page.
    
    This endpoint serves a detailed view of a specific look, showing all its
    components and associated clothes.
    
    Args:
        request (Request): FastAPI request object
        look_id (int): ID of the look to display
        
    Returns:
        HTMLResponse: Rendered look detail page
    """
    return templates.TemplateResponse(
        "look-detail.html", {"request": request, "look_id": look_id}
    )

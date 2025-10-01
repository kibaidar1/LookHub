from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api.exception_handlers import init_exception_handlers
from app.api.router import router as api_router
from app.frontend.router import router as frontend_router
from app.admin.router import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events.
    
    This context manager handles application startup and shutdown events.
    Currently configured for future Redis cache integration.
    
    Args:
        app (FastAPI): The FastAPI application instance
        
    Yields:
        None: Application is ready to handle requests
    """
    # redis = aioredis.from_url("redis://localhost")
    # FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield


# Initialize FastAPI application
app = FastAPI(lifespan=lifespan, title="LookHub main app")

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register application routers
app.include_router(api_router)  # API endpoints
app.include_router(frontend_router)  # Frontend endpoints
app.include_router(admin_router)  # Admin endpoints

# Register exception handlers
init_exception_handlers(app)

# Mount static file directories
app.mount(
    "/admin/static", StaticFiles(directory="app/admin/static"), name="admin_static"
)
app.mount(
    "/frontend/static",
    StaticFiles(directory="app/frontend/static"),
    name="frontend_static",
)
app.mount("/images", StaticFiles(directory="app/static/images"), name="images")


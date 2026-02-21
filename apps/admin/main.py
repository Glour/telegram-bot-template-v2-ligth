"""Admin Panel application with FastAPI and SQLAdmin."""
import uvicorn
from fastapi import FastAPI
from sqladmin import Admin
from starlette.middleware.cors import CORSMiddleware

from apps.admin.admin_panel.views.user_admin import UserAdmin
from apps.admin.api.routes import stats, users
from config.settings.base import get_settings
from infrastructure.database.core.session import get_engine

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=f"{settings.app_name} - Admin Panel",
    version=settings.app_version,
    docs_url="/api/docs" if settings.admin.enable_swagger else None,
    redoc_url="/api/redoc" if settings.admin.enable_swagger else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.admin.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create SQLAdmin
admin = Admin(
    app,
    get_engine(),
    title=f"{settings.app_name} Admin",
)

# Register admin views
admin.add_view(UserAdmin)

# Include API routers
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(stats.router, prefix="/api", tags=["stats"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "admin_panel": "/admin",
        "api_docs": "/api/docs" if settings.admin.enable_swagger else None,
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


def start_admin():
    """Start admin panel server."""
    uvicorn.run(
        "apps.admin.main:app",
        host=settings.admin.host,
        port=settings.admin.port,
        reload=settings.admin.reload,
        log_level="info",
    )


if __name__ == "__main__":
    start_admin()

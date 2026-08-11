# Asyncio
import asyncio
from contextlib import asynccontextmanager

# FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Sentry
import sentry_sdk

# Application
from core.settings import settings  # Settings
from routers import auth, oauth, host, group, page, widget, tag, user  # Routers

# Andromeda
from andromeda.worker import start_andromeda_worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("here")
    andromeda_task = asyncio.create_task(start_andromeda_worker(poll_interval=10))

    yield

    andromeda_task.cancel()
    await asyncio.gather(andromeda_task, return_exceptions=True)


# Init Sentry
sentry_sdk.init(
    dsn=settings.sentry_dsn,
    send_default_pii=True,
)

# FastAPI Application
app = FastAPI(
    title="OpenHubble Metrics - BackEnd",
    version="2.0.0",
    summary="BackEnd service of OpenHubble Metrics.",
    openapi_tags=[
        {"name": "Authentication", "description": "Authentication endpoints"},
        {"name": "OAuthentication", "description": "OAuthentication endpoints"},
        {"name": "User", "description": "User endpoints"},
        {"name": "Tag", "description": "Tag endpoints"},
        {"name": "Group", "description": "Group endpoints"},
        {"name": "Host", "description": "Host endpoints"},
        {"name": "Page", "description": "Page endpoints"},
        {"name": "Widget", "description": "Widget endpoints"},
    ],
    servers=[
        {
            "url": "https://api.metrics.openhubble.com",
            "description": "Metrics Production Server",
        },
        {
            "url": "http://127.0.0.1:8000",
            "description": "Development",
        },
    ],
    lifespan=lifespan if settings.app_mode == "production" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=[
        "https://metrics.openhubble.com",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-API-KEY"],
)


# Routers
app.include_router(auth.router, prefix="/api")  # Authentication
app.include_router(oauth.router, prefix="/api")  # OAuthentication
app.include_router(host.router, prefix="/api")  # Group
app.include_router(group.router, prefix="/api")  # Group
app.include_router(tag.router, prefix="/api")  # Tag
app.include_router(page.router, prefix="/api")  # Page
app.include_router(user.router, prefix="/api")  # User
app.include_router(widget.router, prefix="/api")  # Widget

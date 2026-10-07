from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_v1_router
from app.services.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Executed on application startup
    start_scheduler()
    yield
    # Executed during graceful shutdown
    stop_scheduler()


app = FastAPI(
    title="Real Transfer Cost API",
    description="API for calculating the real cost and hidden markup of international money transfers",
    version="0.1.0",
    lifespan=lifespan,
)

# Allow cross-origin requests from the local Vite development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 router prefix
app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "Real Transfer Cost API is running!"
    }

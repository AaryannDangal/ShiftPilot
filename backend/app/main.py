"""Main FastAPI application entrypoint."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers.auth import router as auth_router
from app.routers.employees import router as employees_router
from app.routers.scheduling import router as scheduling_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version="1.0.0")

origins = [o.strip() for o in settings.backend_cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(employees_router)
app.include_router(scheduling_router)


@app.get("/")
def root():
    return {"service": settings.app_name, "status": "running"}

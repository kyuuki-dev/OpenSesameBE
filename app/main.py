from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import devices, scenes, import_yaml

app = FastAPI()

# Allow CORS from GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific GitHub Pages URL in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(devices.router, prefix="/devices")
app.include_router(scenes.router, prefix="/scenes")
app.include_router(import_yaml.router, prefix="/import")

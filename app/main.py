
from fastapi import FastAPI
from app.routers import devices, scenes, import_yaml
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(devices.router)
app.include_router(scenes.router)
app.include_router(import_yaml.router)

@app.get("/")
def root():
    return {"status": "API running"}

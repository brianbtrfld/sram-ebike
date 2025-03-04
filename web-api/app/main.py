from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import api, web

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:*", "tauri://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(web.router)
app.include_router(api.router)
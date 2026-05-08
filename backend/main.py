from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from api import (
    auth_routes, 
    admin_routes, 
    crop_routes, 
    fertilizer_routes, 
    irrigation_routes, 
    location_routes, 
    weather_routes,
    chat_routes
)
from utils.model_loader import load_models

app = FastAPI(title="Smart Soil AI API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print("Backend starting up...")
    load_models()

# Include Routers
app.include_router(auth_routes.router)
app.include_router(admin_routes.router)
app.include_router(crop_routes.router)
app.include_router(fertilizer_routes.router)
app.include_router(irrigation_routes.router)
app.include_router(location_routes.router)
app.include_router(weather_routes.router)
app.include_router(chat_routes.router)

@app.get("/")
def read_root():
    return {"message": "Smart Soil AI API is running"}

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    # Note: Use string "main:app" for reload support, or the object app directly
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

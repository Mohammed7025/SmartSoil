from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.model_loader import load_models
from api import crop_routes, fertilizer_routes, irrigation_routes, weather_routes, location_routes, chat_routes, auth_routes, admin_routes
import uvicorn

app = FastAPI(title="Smart Soil AI API", version="1.0.0")

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Startup Event
@app.on_event("startup")
async def startup_event():
    load_models()
    # Initialize DB (Sync call is fine for startup)
    from api.auth_routes import init_db
    init_db()

# Include Routers
app.include_router(crop_routes.router)
app.include_router(fertilizer_routes.router)
app.include_router(irrigation_routes.router)
app.include_router(weather_routes.router)
app.include_router(location_routes.router)
app.include_router(chat_routes.router)
app.include_router(auth_routes.router)
app.include_router(admin_routes.router)

@app.get("/")
def read_root():
    return {"message": "Smart Soil AI API is running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

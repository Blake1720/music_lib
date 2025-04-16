from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

from app.services.spotify_import_service import SpotifyImportService
from app.services.recommendation_service import RecommendationService

app = FastAPI(
    title="Music Recommendation API",
    description="API for song recommendations based on user preferences",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize services
spotify_service = None
recommendation_service = None

@app.on_event("startup")
async def startup_event():
    """Initialize services when the application starts"""
    global spotify_service, recommendation_service
    try:
        spotify_service = SpotifyImportService(temp_dir="temp_audio")
        recommendation_service = RecommendationService()
        
        # Import and include routers after services are initialized
        from app.routes import database_route, recommendations, spotify_import
        
        # Make services available to the routers
        spotify_import.spotify_service = spotify_service
        recommendations.recommendation_service = recommendation_service
        
        # Include routers
        app.include_router(recommendations.router, prefix="/api/v1", tags=["recommendations"])
        app.include_router(database_route.router, prefix="/database", tags=["database"])
        app.include_router(spotify_import.router, prefix="/api/v1/spotify", tags=["spotify"])
    except Exception as e:
        print(f"Error initializing services: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources when the application shuts down"""
    if spotify_service:
        spotify_service.cleanup()

@app.get("/")
async def root():
    return {"message": "Welcome to the Music Recommendation API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
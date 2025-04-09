from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

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

@app.get("/")
async def root():
    return {"message": "Welcome to the Music Recommendation API"}

# Import and include routers
from routes import database_route
#app.include_router(recommendations.router, prefix="/api/v1", tags=["recommendations"])
app.include_router(database_route.router, prefix="/api/v1/database", tags=["database"]) 
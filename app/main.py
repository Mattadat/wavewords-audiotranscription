from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import transcription

app = FastAPI()

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(transcription.router)

# You can add additional route includes or other configurations here if needed.

@app.get("/")
async def root():
    return {"message": "Welcome to the Audio Transcription Service"}
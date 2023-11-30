from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class AudioFile(BaseModel):
    id: str = Field(..., description="Unique identifier for the audio file")
    user_id: str = Field(..., description="Identifier for the user who uploaded the file")
    filename: str = Field(..., description="Name of the audio file")
    size: int = Field(..., description="Size of the audio file in bytes")
    upload_time: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of when the file was uploaded")
    status: str = Field(..., description="Current status of the audio file (e.g., 'pending', 'processed')")
    duration: float = Field(..., description="Duration of the audio file in seconds")
    file_format: str = Field(..., description="Format of the audio file (e.g., 'mp3', 'wav')")

    class Config:
        schema_extra = {
            "example": {
                "id": "12345",
                "user_id": "user123",
                "filename": "sample_audio.wav",
                "size": 2048000,
                "upload_time": "2023-11-30T12:00:00",
                "status": "pending",
                "duration": 360.0,
                "file_format": "wav"
            }
        }
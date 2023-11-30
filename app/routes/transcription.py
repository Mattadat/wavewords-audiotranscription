from fastapi import APIRouter, UploadFile, File, HTTPException, Path
from ..services.transcription_service import TranscriptionService
from ..services.dynamodb_service import DynamoDBService
import os
import shutil
import boto3
import uuid

router = APIRouter()
transcription_service = TranscriptionService()
dynamodb_service = DynamoDBService()

UPLOAD_DIR = "/tmp/uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/transcribe")
async def transcribe_audio_file(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, 'wb+') as buffer:
            shutil.copyfileobj(file.file, buffer)

        transcription = transcription_service.transcribe_audio(file_path)
        os.remove(file_path)

        if transcription is None or transcription == "":
            raise HTTPException(status_code=500, detail="Transcription failed.")

        transcription_id = str(uuid.uuid4())
        # Save transcription to DynamoDB
        dynamodb_service.save_transcription(transcription_id, transcription, file.filename)

        return {"transcription_id": transcription_id, "transcription": transcription}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transcriptions")
async def list_transcriptions():
    return dynamodb_service.list_transcriptions()

@router.get("/transcriptions/{transcription_id}")
async def get_transcription(transcription_id: str = Path(..., description="The ID of the transcription to retrieve")):
    transcription = dynamodb_service.get_transcription(transcription_id)
    if transcription is None:
        raise HTTPException(status_code=404, detail="Transcription not found")
    return transcription

@router.delete("/transcriptions/{transcription_id}")
async def delete_transcription(transcription_id: str = Path(..., description="The ID of the transcription to delete")):
    success = dynamodb_service.delete_transcription(transcription_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transcription not found")
    return {"message": "Transcription deleted successfully"}

# Endpoint to download the transcription as a text file
@router.get("/transcriptions/download/{transcription_id}")
async def download_transcription(transcription_id: str = Path(..., description="The ID of the transcription to download")):
    transcription_data = dynamodb_service.get_transcription(transcription_id)
    if transcription_data is None:
        raise HTTPException(status_code=404, detail="Transcription not found")

    filename = f"{transcription_data['original_filename']}.txt"
    content = transcription_data['transcription']
    return Response(content=content, media_type="text/plain", headers={"Content-Disposition": f"attachment;filename={filename}"})
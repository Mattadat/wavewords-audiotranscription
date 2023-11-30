import os
from whispercpp import Whisper
from typing import Optional
from .dynamodb_service import DynamoDBService

class TranscriptionService:
    def __init__(self, model_size: str = "tiny", cache_dir: str = ".cache"):
        self.model_size = model_size
        self.cache_dir = cache_dir
        self.model = self.load_model()
        self.dynamodb_service = DynamoDBService()

    def load_model(self) -> Optional[Whisper]:
        os.environ["WHISPER_CACHE_DIR"] = self.cache_dir
        try:
            return Whisper(model=self.model_size)
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
            return None

    def transcribe_audio(self, file_path: str, transcription_id: str, original_filename: str) -> bool:
        if not self.model:
            return False

        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False

        try:
            # Update status to in_progress
            self.dynamodb_service.update_transcription_status(transcription_id, 'in_progress')

            result = self.model.transcribe(file_path)
            transcribed_text = self.model.extract_text(result)

            # Save transcription text and update status to completed
            self.dynamodb_service.update_transcription_text(transcription_id, transcribed_text)
            self.dynamodb_service.update_transcription_status(transcription_id, 'completed')
            return True
        except Exception as e:
            print(f"Error during transcription: {e}")
            # Update status to failed in case of error
            self.dynamodb_service.update_transcription_status(transcription_id, 'failed')
            return False
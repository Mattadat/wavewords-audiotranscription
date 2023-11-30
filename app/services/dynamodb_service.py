
Certainly, to store the text of the transcription along with its status, you need to update the DynamoDB service to handle this additional data. The save_transcription method can be adjusted to initialize the record with an empty transcription field, and a new method can be added to update the transcription text once it's available.

Here's how the DynamoDBService in dynamodb_service.py can be modified to include these functionalities:

python
Copy code
import boto3
from botocore.exceptions import ClientError
from typing import Optional, Dict, List

class DynamoDBService:
    def __init__(self, table_name: str = "Transcriptions"):
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    def save_transcription(self, transcription_id: str, original_filename: str) -> bool:
        try:
            self.table.put_item(
                Item={
                    'TranscriptionId': transcription_id,
                    'OriginalFilename': original_filename,
                    'Status': 'pending',  # Initial status
                    'TranscriptionText': ''  # Empty text initially
                }
            )
            return True
        except ClientError as e:
            print(f"Failed to save transcription: {e}")
            return False

    def update_transcription_status(self, transcription_id: str, status: str) -> bool:
        try:
            self.table.update_item(
                Key={'TranscriptionId': transcription_id},
                UpdateExpression='SET #status = :status',
                ExpressionAttributeNames={'#status': 'Status'},
                ExpressionAttributeValues={':status': status}
            )
            return True
        except ClientError as e:
            print(f"Failed to update transcription status: {e}")
            return False

    def update_transcription_text(self, transcription_id: str, text: str) -> bool:
        try:
            self.table.update_item(
                Key={'TranscriptionId': transcription_id},
                UpdateExpression='SET #text = :text',
                ExpressionAttributeNames={'#text': 'TranscriptionText'},
                ExpressionAttributeValues={':text': text}
            )
            return True
        except ClientError as e:
            print(f"Failed to update transcription text: {e}")
            return False

    def get_transcription(self, transcription_id: str) -> Optional[Dict]:
        try:
            response = self.table.get_item(
                Key={'TranscriptionId': transcription_id}
            )
            return response.get('Item')
        except ClientError as e:
            print(f"Failed to retrieve transcription: {e}")
            return None

    def list_transcriptions(self) -> List[Dict]:
        try:
            response = self.table.scan()
            return response.get('Items', [])
        except ClientError as e:
            print(f"Failed to list transcriptions: {e}")
            return []

    def delete_transcription(self, transcription_id: str) -> bool:
        try:
            self.table.delete_item(
                Key={'TranscriptionId': transcription_id}
            )
            return True
        except ClientError as e:
            print(f"Failed to delete transcription: {e}")
            return False
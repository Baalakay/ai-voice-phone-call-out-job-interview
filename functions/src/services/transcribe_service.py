"""
AWS Transcribe Service for Audio Transcription
"""
import boto3
import json
import time
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlparse
import requests
import tempfile
import os

logger = logging.getLogger(__name__)

class TranscribeService:
    """Service for transcribing audio recordings using AWS Transcribe."""
    
    def __init__(self):
        self.transcribe_client = boto3.client('transcribe')
        self.s3_client = boto3.client('s3')
        self.bucket_name = os.environ.get('S3_BUCKET_NAME', 'innovativesol-gravywork-assets-dev')
    
    def transcribe_recording(self, recording_url: str, assessment_id: str, question_key: str) -> Dict[str, Any]:
        """
        Transcribe a Twilio recording using AWS Transcribe.
        
        Args:
            recording_url: Twilio recording URL
            assessment_id: Assessment identifier
            question_key: Question identifier
            
        Returns:
            Dict with transcription result
        """
        try:
            # Step 1: Download recording from Twilio and upload to S3
            s3_key = self._upload_recording_to_s3(recording_url, assessment_id, question_key)
            if not s3_key:
                return {'success': False, 'error': 'Failed to upload recording to S3'}
            
            # Step 2: Start transcription job
            job_name = f"assessment-{assessment_id}-{question_key}-{int(time.time())}"
            transcription_result = self._start_transcription_job(job_name, s3_key)
            
            if not transcription_result['success']:
                return transcription_result
            
            # Step 3: Wait for completion and get results
            transcript = self._wait_for_transcription(job_name)
            
            if transcript:
                return {
                    'success': True,
                    'transcript': transcript,
                    'job_name': job_name,
                    's3_key': s3_key
                }
            else:
                return {'success': False, 'error': 'Transcription job failed or timed out'}
                
        except Exception as e:
            logger.error(f"Transcription error for {assessment_id}/{question_key}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _upload_recording_to_s3(self, recording_url: str, assessment_id: str, question_key: str) -> Optional[str]:
        """Download recording from Twilio and upload to S3."""
        try:
            # Download recording from Twilio
            response = requests.get(recording_url, stream=True)
            response.raise_for_status()
            
            # Create S3 key for the recording
            s3_key = f"assessments/{assessment_id}/recordings/{question_key}.mp3"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=response.content,
                ContentType='audio/mpeg'
            )
            
            logger.info(f"Uploaded recording to S3: s3://{self.bucket_name}/{s3_key}")
            return s3_key
            
        except Exception as e:
            logger.error(f"Failed to upload recording to S3: {str(e)}")
            return None
    
    def _start_transcription_job(self, job_name: str, s3_key: str) -> Dict[str, Any]:
        """Start AWS Transcribe job."""
        try:
            media_uri = f"s3://{self.bucket_name}/{s3_key}"
            
            # Start transcription job
            response = self.transcribe_client.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': media_uri},
                MediaFormat='mp3',
                LanguageCode='en-US',
                Settings={
                    'ShowSpeakerLabels': False,
                    'MaxSpeakerLabels': 1,
                    'ShowAlternatives': False
                },
                OutputBucketName=self.bucket_name,
                OutputKey=f"assessments/transcripts/{job_name}.json"
            )
            
            logger.info(f"Started transcription job: {job_name}")
            return {'success': True, 'job_name': job_name}
            
        except Exception as e:
            logger.error(f"Failed to start transcription job: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _wait_for_transcription(self, job_name: str, max_wait_seconds: int = 300) -> Optional[str]:
        """Wait for transcription job to complete and return transcript."""
        start_time = time.time()
        
        while time.time() - start_time < max_wait_seconds:
            try:
                response = self.transcribe_client.get_transcription_job(
                    TranscriptionJobName=job_name
                )
                
                status = response['TranscriptionJob']['TranscriptionJobStatus']
                
                if status == 'COMPLETED':
                    # Get transcript from S3
                    transcript_uri = response['TranscriptionJob']['Transcript']['TranscriptFileUri']
                    return self._extract_transcript_from_s3(transcript_uri)
                    
                elif status == 'FAILED':
                    logger.error(f"Transcription job failed: {job_name}")
                    return None
                    
                # Job still in progress, wait
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Error checking transcription job status: {str(e)}")
                return None
        
        logger.error(f"Transcription job timed out: {job_name}")
        return None
    
    def _extract_transcript_from_s3(self, transcript_uri: str) -> Optional[str]:
        """Extract transcript text from S3 JSON file."""
        try:
            # Parse S3 URI
            parsed_uri = urlparse(transcript_uri)
            bucket = parsed_uri.netloc
            key = parsed_uri.path.lstrip('/')
            
            # Get transcript JSON from S3
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            transcript_data = json.loads(response['Body'].read())
            
            # Extract transcript text
            transcript = transcript_data['results']['transcripts'][0]['transcript']
            return transcript.strip()
            
        except Exception as e:
            logger.error(f"Failed to extract transcript from S3: {str(e)}")
            return None
    
    def batch_transcribe_assessment(self, assessment_id: str, skill_type: str, responses: Dict[str, Any]) -> Dict[str, str]:
        """
        Transcribe all recordings for an assessment.
        
        Args:
            assessment_id: Assessment identifier
            skill_type: Role type (bartender, banquet_server, host)
            responses: Dict of question responses with recording URLs
            
        Returns:
            Dict mapping question keys to transcripts
        """
        transcripts = {}
        
        for question_key, response in responses.items():
            if 'recording_url' in response:
                logger.info(f"Transcribing {question_key} for assessment {assessment_id}")
                
                result = self.transcribe_recording(
                    response['recording_url'], 
                    assessment_id, 
                    question_key
                )
                
                if result['success']:
                    transcripts[question_key] = result['transcript']
                    logger.info(f"Successfully transcribed {question_key}: {result['transcript'][:100]}...")
                else:
                    logger.error(f"Failed to transcribe {question_key}: {result['error']}")
                    transcripts[question_key] = "[TRANSCRIPTION_FAILED]"
        
        return transcripts
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service configuration info."""
        return {
            'service': 'AWS Transcribe',
            'bucket': self.bucket_name,
            'language': 'en-US',
            'format': 'mp3'
        }


def create_transcribe_service() -> TranscribeService:
    """Factory function to create TranscribeService instance."""
    return TranscribeService()

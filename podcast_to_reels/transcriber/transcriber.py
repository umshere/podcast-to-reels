"""
Transcriber module for converting audio to text using OpenAI Whisper API.
"""

import os
import json
import logging
from pathlib import Path
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def transcribe_audio(audio_path, output_dir="output", filename="transcript.json"):
    """
    Transcribe audio file using OpenAI Whisper API.
    
    Args:
        audio_path (str): Path to the audio file
        output_dir (str): Directory to save the transcript
        filename (str): Name of the output transcript file
        
    Returns:
        str: Path to the transcript file
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    
    # Get API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable not set")
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    # Initialize OpenAI client
    client = openai.OpenAI(api_key=api_key)
    
    logger.info(f"Transcribing audio file: {audio_path}")
    
    try:
        # Check if file exists and is accessible
        if not os.path.isfile(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Check file size to ensure it's within Whisper API limits (25MB)
        file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
        if file_size_mb > 25:
            logger.error(f"Audio file size ({file_size_mb:.2f} MB) exceeds Whisper API limit of 25 MB")
            raise ValueError(f"Audio file size ({file_size_mb:.2f} MB) exceeds Whisper API limit of 25 MB")
        
        # Open the audio file
        with open(audio_path, "rb") as audio_file:
            # Call the Whisper API
            logger.info("Sending audio to OpenAI Whisper API")
            response = client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["segment"]
            )
        
        # Process the response
        if hasattr(response, 'to_dict'):
            transcript_data = response.to_dict()
        else:
            transcript_data = response
        
        # Save the transcript to a JSON file
        with open(output_path, "w") as f:
            json.dump(transcript_data, f, indent=2)
        
        logger.info(f"Transcription saved to {output_path}")
        return output_path
        
    except openai.APIError as e:
        logger.error(f"OpenAI API error: {e}")
        raise RuntimeError(f"OpenAI API error: {e}")
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        raise

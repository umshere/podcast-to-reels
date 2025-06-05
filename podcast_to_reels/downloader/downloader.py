"""
Downloader module for extracting audio from YouTube videos.
"""

import os
import subprocess
import logging
from pathlib import Path
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_audio(url, duration=60, start_time=0, output_dir="output", filename="audio.mp3"):
    """
    Download audio from a YouTube URL and optionally trim it to a specified duration.
    
    Args:
        url (str): YouTube URL to download from
        duration (int): Maximum duration in seconds (default: 60)
        start_time (int): Starting point in seconds (default: 0)
        output_dir (str): Directory to save the audio file
        filename (str): Name of the output audio file
        
    Returns:
        str: Path to the downloaded audio file
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    
    logger.info(f"Downloading audio from {url}")
    
    try:
        # First, get video duration using yt-dlp
        duration_cmd = [
            "yt-dlp", 
            "--skip-download", 
            "--print", "duration", 
            url
        ]
        video_duration = int(subprocess.check_output(duration_cmd, text=True).strip())
        logger.info(f"Video duration: {video_duration} seconds")
        
        # Determine if we need to trim based on duration or start time
        needs_trimming = video_duration > duration or start_time > 0
        
        if needs_trimming:
            # Download to a temporary file first
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_file.close()
            temp_path = temp_file.name
            
            # Download audio using yt-dlp
            download_cmd = [
                "yt-dlp",
                "-x",  # Extract audio
                "--audio-format", "mp3",
                "--audio-quality", "0",  # Best quality
                "-o", temp_path,
                url
            ]
            subprocess.run(download_cmd, check=True)
            
            # Trim the audio using ffmpeg
            logger.info(f"Trimming audio: start at {start_time}s for {duration} seconds")
            trim_cmd = [
                "ffmpeg",
                "-i", temp_path,
                "-ss", str(start_time),
                "-t", str(duration),
                "-c:a", "libmp3lame",
                "-q:a", "0",  # Best quality
                "-y",  # Overwrite output file
                output_path
            ]
            subprocess.run(trim_cmd, check=True)
            
            # Clean up temporary file
            os.unlink(temp_path)
        else:
            # Download directly to output path
            download_cmd = [
                "yt-dlp",
                "-x",  # Extract audio
                "--audio-format", "mp3",
                "--audio-quality", "0",  # Best quality
                "-o", output_path,
                url
            ]
            subprocess.run(download_cmd, check=True)
        
        logger.info(f"Audio downloaded and saved to {output_path}")
        return output_path
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error downloading audio: {e}")
        raise RuntimeError(f"Failed to download audio from {url}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

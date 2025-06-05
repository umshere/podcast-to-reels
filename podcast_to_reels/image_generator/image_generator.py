"""
Image Generator module for creating images from text prompts using Stability AI API.
"""

import os
import time
import logging
import requests
from pathlib import Path
import base64
from PIL import Image
import io
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_images(scenes, output_dir="output/images", style="modern flat illustration, bright colours"):
    """
    Generate images for each scene using Stability AI API.
    
    Args:
        scenes (list): List of Scene objects with prompts
        output_dir (str): Directory to save the generated images
        style (str): Style description to append to prompts
        
    Returns:
        list: Paths to the generated images
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Get API key from environment variable
    api_key = os.getenv("STABILITY_API_KEY")
    if not api_key:
        logger.error("STABILITY_API_KEY environment variable not set")
        raise ValueError("STABILITY_API_KEY environment variable not set")
    
    # API endpoint for Stability AI
    api_host = os.getenv("STABILITY_API_HOST", "https://api.stability.ai")
    api_endpoint = f"{api_host}/v2beta/stable-diffusion/text-to-image"
    
    # Headers for API request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    image_paths = []
    
    logger.info(f"Generating {len(scenes)} images")
    
    for i, scene in enumerate(tqdm(scenes, desc="Generating images")):
        # Skip if no prompt
        if not scene.prompt:
            logger.warning(f"No prompt for scene {i+1}, skipping")
            continue
        
        # Enhance prompt with style
        enhanced_prompt = f"{scene.prompt} {style}"
        
        # Prepare payload for API request
        payload = {
            "model_id": "sd3.5-medium",
            "width": 1080,
            "height": 1920,  # Vertical format for reels
            "samples": 1,
            "steps": 30,
            "prompt": enhanced_prompt,
            "cfg_scale": 7.0
        }
        
        # File path for the image
        image_filename = f"scene_{i+1:03d}.png"
        image_path = os.path.join(output_dir, image_filename)
        
        # Try up to 3 times (initial attempt + 2 retries)
        max_retries = 2
        retry_count = 0
        success = False
        
        while not success and retry_count <= max_retries:
            try:
                logger.info(f"Generating image {i+1}/{len(scenes)}: {enhanced_prompt[:50]}...")
                
                # Make API request
                response = requests.post(
                    api_endpoint,
                    headers=headers,
                    json=payload
                )
                
                # Check for errors
                if response.status_code >= 500:
                    logger.warning(f"Server error (5xx): {response.status_code}. Retrying...")
                    retry_count += 1
                    time.sleep(2)  # Wait before retrying
                    continue
                
                # Raise exception for other errors
                response.raise_for_status()
                
                # Parse response
                data = response.json()
                
                # Save image
                if "artifacts" in data and len(data["artifacts"]) > 0:
                    for j, artifact in enumerate(data["artifacts"]):
                        if artifact["finishReason"] == "SUCCESS":
                            # Decode base64 image
                            image_data = base64.b64decode(artifact["base64"])
                            
                            # Save image
                            with open(image_path, "wb") as f:
                                f.write(image_data)
                            
                            logger.info(f"Image saved to {image_path}")
                            image_paths.append(image_path)
                            success = True
                            break
                
                # If we got here without success, log an error
                if not success:
                    logger.error(f"Failed to generate image: {data.get('message', 'Unknown error')}")
                    retry_count += 1
                
                # Rate limiting - don't exceed 1 request per second
                time.sleep(1)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error: {e}")
                retry_count += 1
                time.sleep(2)  # Wait before retrying
            
            except Exception as e:
                logger.error(f"Error generating image: {e}")
                retry_count += 1
                time.sleep(2)  # Wait before retrying
        
        # If all retries failed, log error but continue with next scene
        if not success:
            logger.error(f"Failed to generate image for scene {i+1} after {max_retries + 1} attempts")
    
    logger.info(f"Generated {len(image_paths)} images")
    return image_paths

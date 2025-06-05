"""
Scene Splitter module for chunking transcripts and generating image prompts.
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

class Scene:
    """Class to represent a scene with text, timestamp, and image prompt."""
    def __init__(self, text, start_time, end_time, prompt=None):
        self.text = text
        self.start_time = start_time
        self.end_time = end_time
        self.prompt = prompt
        
    def to_dict(self):
        """Convert scene to dictionary."""
        return {
            "text": self.text,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "prompt": self.prompt
        }

def split_scenes(transcript_path, max_words_per_scene=20, output_dir="output", filename="scenes.json"):
    """
    Split transcript into scenes and generate image prompts.
    
    Args:
        transcript_path (str): Path to the transcript JSON file
        max_words_per_scene (int): Maximum number of words per scene
        output_dir (str): Directory to save the scenes
        filename (str): Name of the output scenes file
        
    Returns:
        list: List of Scene objects
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
    
    logger.info(f"Processing transcript: {transcript_path}")
    
    try:
        # Load transcript JSON
        with open(transcript_path, "r") as f:
            transcript_data = json.load(f)
        
        # Extract segments from transcript
        segments = []
        if "segments" in transcript_data:
            segments = transcript_data["segments"]
        else:
            logger.warning("No segments found in transcript, falling back to text")
            # If no segments, try to use the full text
            if "text" in transcript_data:
                text = transcript_data["text"]
                segments = [{"text": text, "start": 0, "end": 60}]
            else:
                raise ValueError("Invalid transcript format: no segments or text found")
        
        # Process segments into scenes
        scenes = []
        current_scene_text = ""
        current_scene_start = None
        
        for segment in segments:
            segment_text = segment.get("text", "").strip()
            segment_start = segment.get("start", 0)
            segment_end = segment.get("end", segment_start + 5)
            
            # Skip empty segments
            if not segment_text:
                continue
            
            # Initialize current scene if this is the first segment
            if current_scene_start is None:
                current_scene_start = segment_start
            
            # Split segment into words
            words = segment_text.split()
            
            # Add words to current scene until max_words_per_scene is reached
            for word in words:
                if len(current_scene_text.split()) >= max_words_per_scene:
                    # Create a new scene
                    scene = Scene(
                        text=current_scene_text.strip(),
                        start_time=current_scene_start,
                        end_time=segment_end
                    )
                    scenes.append(scene)
                    
                    # Reset current scene
                    current_scene_text = word + " "
                    current_scene_start = segment_start
                else:
                    # Add word to current scene
                    current_scene_text += word + " "
        
        # Add the last scene if there's any text left
        if current_scene_text.strip():
            scene = Scene(
                text=current_scene_text.strip(),
                start_time=current_scene_start,
                end_time=segments[-1].get("end", current_scene_start + 5)
            )
            scenes.append(scene)
        
        logger.info(f"Split transcript into {len(scenes)} scenes")
        
        # Generate image prompts for each scene
        for i, scene in enumerate(scenes):
            logger.info(f"Generating prompt for scene {i+1}/{len(scenes)}")
            
            try:
                # Use GPT-4o-mini to generate image prompts
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a creative visual director. Create a vivid, detailed image prompt based on the provided text from a science podcast. The prompt should be suitable for image generation and capture the essence of the scientific concept being discussed. Focus on creating a visually engaging representation that would work well in a short video reel. Use modern flat illustration style with bright colors."},
                        {"role": "user", "content": f"Create an image prompt based on this text from a science podcast: '{scene.text}'"}
                    ],
                    max_tokens=100
                )
                
                # Extract prompt from response
                prompt = response.choices[0].message.content.strip()
                scene.prompt = prompt
                
                logger.info(f"Generated prompt: {prompt}")
                
            except Exception as e:
                logger.error(f"Error generating prompt for scene {i+1}: {e}")
                # Provide a fallback prompt based on the scene text
                scene.prompt = f"Scientific illustration of: {scene.text}"
        
        # Save scenes to JSON file
        with open(output_path, "w") as f:
            json.dump([scene.to_dict() for scene in scenes], f, indent=2)
        
        logger.info(f"Scenes saved to {output_path}")
        return scenes
        
    except Exception as e:
        logger.error(f"Error processing transcript: {e}")
        raise

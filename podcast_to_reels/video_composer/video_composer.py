"""
Video Composer module for assembling images and audio into a video.
"""

import os
import logging
from pathlib import Path
import numpy as np
from moviepy import (
    AudioFileClip,
    ImageClip,
    concatenate_videoclips,
    CompositeVideoClip,
    TextClip
)
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def compose_video(audio_path, image_paths, scenes, output_path="output/reel.mp4", fps=30, resolution=(1080, 1920)):
    """
    Compose a video from images and audio.
    
    Args:
        audio_path (str): Path to the audio file
        image_paths (list): List of paths to the image files
        scenes (list): List of Scene objects with timestamps
        output_path (str): Path to save the output video
        fps (int): Frames per second
        resolution (tuple): Video resolution (width, height)
        
    Returns:
        str: Path to the output video
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    logger.info(f"Composing video from {len(image_paths)} images and audio")

    try:
        # Ensure we have at least one image before loading audio
        if not image_paths:
            logger.error("No images provided for video composition")
            raise ValueError("No images provided for video composition")

        # Load audio
        logger.info(f"Loading audio: {audio_path}")
        audio_clip = AudioFileClip(audio_path)

        # Create video clips from images
        video_clips = []
        
        # Match images to scenes based on order
        # If we have fewer images than scenes, we'll reuse the last image
        for i, scene in enumerate(scenes):
            # Get corresponding image path (or use the last one if we run out)
            img_index = min(i, len(image_paths) - 1)
            image_path = image_paths[img_index]
            
            # Calculate duration for this scene
            duration = scene.end_time - scene.start_time
            
            logger.info(f"Creating clip for scene {i+1}: {image_path}, duration: {duration:.2f}s")
            
            # Create image clip
            img_clip = ImageClip(image_path, duration=duration)
            
            # Resize to fit the target resolution while maintaining aspect ratio
            # Use the resize method directly to avoid calling MoviePy's fx
            img_clip = img_clip.resize(width=resolution[0])
            
            # Center the image
            img_clip = img_clip.set_position("center")
            
            # Set start time to match the audio
            img_clip = img_clip.set_start(scene.start_time)
            
            # Add optional text overlay with the scene text
            if hasattr(scene, 'text') and scene.text:
                txt_clip = TextClip(
                    scene.text, 
                    fontsize=30, 
                    color='white',
                    bg_color='rgba(0,0,0,0.5)',
                    size=(resolution[0] - 40, None),
                    method='caption'
                )
                txt_clip = txt_clip.set_position(('center', 'bottom')).set_duration(duration).set_start(scene.start_time)
                
                # Composite image and text
                comp_clip = CompositeVideoClip([img_clip, txt_clip], size=resolution)
                video_clips.append(comp_clip)
            else:
                video_clips.append(img_clip)
        
        # Create a black background clip with the full duration
        total_duration = audio_clip.duration
        
        # Concatenate all clips
        logger.info("Concatenating video clips")
        final_clip = CompositeVideoClip(video_clips, size=resolution)
        final_clip.set_duration(total_duration)
        
        # Add audio
        logger.info("Adding audio to video")
        final_clip.set_audio(audio_clip)
        
        # Write output file
        logger.info(f"Writing video to {output_path}")
        final_clip.write_videofile(
            output_path,
            fps=fps,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
            threads=4
        )
        
        # Clean up
        final_clip.close()
        audio_clip.close()
        
        logger.info(f"Video saved to {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error composing video: {e}")
        raise

#!/usr/bin/env python3
"""
Main script to run the podcast-to-reels pipeline.
"""
import argparse
import os
import sys
from pathlib import Path

# Add the parent directory to sys.path to allow importing the package
sys.path.append(str(Path(__file__).parent.parent))

from podcast_to_reels.downloader import download_audio
from podcast_to_reels.transcriber import transcribe_audio
from podcast_to_reels.scene_splitter import split_scenes
from podcast_to_reels.image_generator import generate_images
from podcast_to_reels.video_composer import compose_video


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert a YouTube podcast to an illustrated video reel"
    )
    parser.add_argument(
        "--url", 
        required=True, 
        help="YouTube URL of the podcast"
    )
    parser.add_argument(
        "--duration", 
        type=int, 
        default=60, 
        help="Duration of the output video in seconds (default: 60)"
    )
    parser.add_argument(
        "--output", 
        default="output/reel.mp4", 
        help="Output file path (default: output/reel.mp4)"
    )
    return parser.parse_args()


def main():
    """Run the podcast-to-reels pipeline."""
    args = parse_arguments()
    
    print(f"Starting podcast-to-reels pipeline for URL: {args.url}")
    print(f"Target duration: {args.duration} seconds")
    
    # Step 1: Download audio from YouTube
    audio_path = download_audio(args.url, args.duration)
    print(f"Audio downloaded to: {audio_path}")
    
    # Step 2: Transcribe audio
    transcript_path = transcribe_audio(audio_path)
    print(f"Transcription saved to: {transcript_path}")
    
    # Step 3: Split transcript into scenes and generate prompts
    scenes = split_scenes(transcript_path)
    print(f"Generated {len(scenes)} scene prompts")
    
    # Step 4: Generate images for each scene
    image_paths = generate_images(scenes)
    print(f"Generated {len(image_paths)} images")
    
    # Step 5: Compose final video
    output_path = compose_video(audio_path, image_paths, scenes, args.output)
    print(f"Video reel created at: {output_path}")
    
    print("Pipeline completed successfully!")


if __name__ == "__main__":
    main()

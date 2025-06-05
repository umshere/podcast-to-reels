"""
Unit tests for the video composer module.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from podcast_to_reels.video_composer.video_composer import compose_video
from podcast_to_reels.scene_splitter.scene_splitter import Scene

class TestVideoComposer:
    
    @pytest.fixture
    def sample_scenes(self):
        # Create sample scenes for testing
        return [
            Scene(text="Scene 1", start_time=0, end_time=5, prompt="A scientific illustration of atoms"),
            Scene(text="Scene 2", start_time=5, end_time=10, prompt="A colorful DNA double helix")
        ]
    
    @pytest.fixture
    def sample_image_paths(self, tmp_path):
        # Create sample image files
        image_paths = []
        for i in range(2):
            image_path = tmp_path / f"image_{i}.png"
            # Create an empty file
            with open(image_path, "w") as f:
                f.write("")
            image_paths.append(str(image_path))
        return image_paths
    
    @pytest.fixture
    def sample_audio_path(self, tmp_path):
        # Create a sample audio file
        audio_path = tmp_path / "audio.mp3"
        # Create an empty file
        with open(audio_path, "w") as f:
            f.write("")
        return str(audio_path)
    
    @patch('podcast_to_reels.video_composer.video_composer.AudioFileClip')
    @patch('podcast_to_reels.video_composer.video_composer.ImageClip')
    @patch('podcast_to_reels.video_composer.video_composer.CompositeVideoClip')
    @patch('podcast_to_reels.video_composer.video_composer.TextClip')
    def test_compose_video_success(self, mock_text_clip, mock_composite_clip, mock_image_clip, 
                                  mock_audio_clip, sample_scenes, sample_image_paths, 
                                  sample_audio_path, tmp_path):
        # Mock MoviePy components
        mock_audio = MagicMock()
        mock_audio.duration = 10.0
        mock_audio_clip.return_value = mock_audio
        
        mock_img = MagicMock()
        mock_img.size = (1080, 1080)
        mock_image_clip.return_value = mock_img
        
        mock_txt = MagicMock()
        mock_text_clip.return_value = mock_txt
        
        mock_final = MagicMock()
        mock_composite_clip.return_value = mock_final
        
        # Call the function
        output_path = str(tmp_path / "output.mp4")
        result = compose_video(sample_audio_path, sample_image_paths, sample_scenes, output_path)
        
        # Check that the MoviePy components were called correctly
        assert mock_audio_clip.call_count == 1
        assert mock_image_clip.call_count == len(sample_scenes)
        assert mock_composite_clip.call_count > 0
        
        # Check that the write_videofile method was called
        assert mock_final.write_videofile.call_count == 1
        
        # Check that the result is the output path
        assert result == output_path
    
    def test_compose_video_no_images(self, sample_scenes, sample_audio_path):
        # Check that the function raises an exception when no images are provided
        with pytest.raises(ValueError, match="No images provided for video composition"):
            compose_video(sample_audio_path, [], sample_scenes)
    
    @patch('podcast_to_reels.video_composer.video_composer.AudioFileClip')
    def test_compose_video_audio_error(self, mock_audio_clip, sample_scenes, sample_image_paths, sample_audio_path):
        # Mock AudioFileClip to raise an exception
        mock_audio_clip.side_effect = Exception("Audio error")
        
        # Check that the function raises an exception
        with pytest.raises(Exception):
            compose_video(sample_audio_path, sample_image_paths, sample_scenes)

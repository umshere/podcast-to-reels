"""
Unit tests for the image generator module.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from podcast_to_reels.image_generator.image_generator import generate_images
from podcast_to_reels.scene_splitter.scene_splitter import Scene

class TestImageGenerator:
    
    @pytest.fixture
    def sample_scenes(self):
        # Create sample scenes for testing
        return [
            Scene(text="Scene 1", start_time=0, end_time=5, prompt="A scientific illustration of atoms"),
            Scene(text="Scene 2", start_time=5, end_time=10, prompt="A colorful DNA double helix")
        ]
    
    @patch('podcast_to_reels.image_generator.image_generator.requests.post')
    def test_generate_images_success(self, mock_post, sample_scenes, tmp_path):
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "artifacts": [
                {
                    "base64": "SGVsbG8gV29ybGQ=",  # "Hello World" in base64
                    "finishReason": "SUCCESS"
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # Mock environment variable
        with patch.dict(os.environ, {"STABILITY_API_KEY": "test_key"}):
            # Call the function
            output_dir = str(tmp_path)
            image_paths = generate_images(sample_scenes, output_dir=output_dir)
            
            # Check that the API was called correctly
            assert mock_post.call_count == len(sample_scenes)
            
            # Check that the output files were created
            assert len(image_paths) == len(sample_scenes)
            for path in image_paths:
                assert os.path.exists(path)
    
    def test_generate_images_missing_api_key(self, sample_scenes):
        # Mock environment variable to be empty
        with patch.dict(os.environ, {"STABILITY_API_KEY": ""}):
            # Check that the function raises an exception
            with pytest.raises(ValueError, match="STABILITY_API_KEY environment variable not set"):
                generate_images(sample_scenes)
    
    @patch('podcast_to_reels.image_generator.image_generator.requests.post')
    def test_generate_images_server_error_with_retry(self, mock_post, sample_scenes, tmp_path):
        # Mock responses: first a 500 error, then a success
        error_response = MagicMock()
        error_response.status_code = 500
        
        success_response = MagicMock()
        success_response.status_code = 200
        success_response.json.return_value = {
            "artifacts": [
                {
                    "base64": "SGVsbG8gV29ybGQ=",
                    "finishReason": "SUCCESS"
                }
            ]
        }
        
        # Set up the mock to return error then success
        mock_post.side_effect = [error_response, success_response]
        
        # Mock environment variable
        with patch.dict(os.environ, {"STABILITY_API_KEY": "test_key"}):
            # Call the function with just one scene to simplify testing
            output_dir = str(tmp_path)
            image_paths = generate_images([sample_scenes[0]], output_dir=output_dir)
            
            # Check that the API was called twice (initial + retry)
            assert mock_post.call_count == 2
            
            # Check that the output file was created
            assert len(image_paths) == 1
            assert os.path.exists(image_paths[0])
    
    @patch('podcast_to_reels.image_generator.image_generator.requests.post')
    def test_generate_images_max_retries_exceeded(self, mock_post, sample_scenes):
        # Mock responses: all 500 errors
        error_response = MagicMock()
        error_response.status_code = 500
        
        # Set up the mock to always return errors
        mock_post.return_value = error_response
        
        # Mock environment variable
        with patch.dict(os.environ, {"STABILITY_API_KEY": "test_key"}):
            # Call the function with just one scene
            image_paths = generate_images([sample_scenes[0]])
            
            # Check that the API was called the maximum number of times (initial + 2 retries)
            assert mock_post.call_count == 3
            
            # Check that no images were returned
            assert len(image_paths) == 0

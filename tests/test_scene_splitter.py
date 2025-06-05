"""
Unit tests for the scene splitter module.
"""

import os
import json
import pytest
from unittest.mock import patch, MagicMock
from podcast_to_reels.scene_splitter.scene_splitter import split_scenes, Scene

class TestSceneSplitter:
    
    @pytest.fixture
    def sample_transcript_path(self, tmp_path):
        # Create a sample transcript file
        transcript_path = tmp_path / "transcript.json"
        transcript_data = {
            "text": "This is a test transcript for the scene splitter module.",
            "segments": [
                {"text": "This is a test transcript", "start": 0, "end": 5},
                {"text": "for the scene splitter module.", "start": 5, "end": 10}
            ]
        }
        with open(transcript_path, "w") as f:
            json.dump(transcript_data, f)
        return str(transcript_path)
    
    @patch('podcast_to_reels.scene_splitter.scene_splitter.openai.OpenAI')
    def test_split_scenes_success(self, mock_openai, sample_transcript_path, tmp_path):
        # Mock OpenAI client and response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test image prompt"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Mock environment variable
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            # Call the function
            output_dir = str(tmp_path)
            scenes = split_scenes(sample_transcript_path, output_dir=output_dir)
            
            # Check that the OpenAI client was called correctly
            assert mock_client.chat.completions.create.call_count == len(scenes)
            
            # Check that the output file was created
            output_path = os.path.join(output_dir, "scenes.json")
            assert os.path.exists(output_path)
            
            # Check that the scenes were created correctly
            assert len(scenes) > 0
            for scene in scenes:
                assert isinstance(scene, Scene)
                assert scene.text
                assert scene.prompt
                assert scene.start_time >= 0
                assert scene.end_time > scene.start_time
    
    def test_split_scenes_missing_api_key(self, sample_transcript_path):
        # Mock environment variable to be empty
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            # Check that the function raises an exception
            with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable not set"):
                split_scenes(sample_transcript_path)
    
    def test_split_scenes_invalid_transcript(self, tmp_path):
        # Create an invalid transcript file
        invalid_path = tmp_path / "invalid.json"
        with open(invalid_path, "w") as f:
            f.write("Not a valid JSON")
        
        # Mock environment variable
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            # Check that the function raises an exception
            with pytest.raises(Exception):
                split_scenes(str(invalid_path))
    
    @patch('podcast_to_reels.scene_splitter.scene_splitter.openai.OpenAI')
    def test_split_scenes_api_error(self, mock_openai, sample_transcript_path):
        # Mock OpenAI client to raise an exception
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API error")
        mock_openai.return_value = mock_client
        
        # Mock environment variable
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            # Check that the function raises an exception
            with pytest.raises(Exception):
                split_scenes(sample_transcript_path)

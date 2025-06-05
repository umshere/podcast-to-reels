"""
Unit tests for the transcriber module.
"""

import os
import json
import pytest
from unittest.mock import patch, MagicMock
from podcast_to_reels.transcriber.transcriber import transcribe_audio

class TestTranscriber:
    
    @patch('podcast_to_reels.transcriber.transcriber.openai.OpenAI')
    def test_transcribe_audio_success(self, mock_openai, tmp_path):
        # Mock OpenAI client and response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.to_dict.return_value = {
            "text": "Test transcript",
            "segments": [
                {"text": "Test transcript", "start": 0, "end": 5}
            ]
        }
        mock_client.audio.transcriptions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create a temporary audio file
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"\x00")

        # Mock environment variable
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            # Call the function
            result = transcribe_audio(str(audio_path))
            
            # Check that the OpenAI client was called correctly
            mock_client.audio.transcriptions.create.assert_called_once()
            
            # Check that the output path is correct
            assert result == os.path.join("output", "transcript.json")
            
            # Check that the file was written
            assert os.path.exists(result)
    
    def test_transcribe_audio_missing_api_key(self, tmp_path):
        # Create a temporary audio file
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"\x00")

        # Mock environment variable to be empty
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            # Check that the function raises an exception
            with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable not set"):
                transcribe_audio(str(audio_path))
    
    @patch('podcast_to_reels.transcriber.transcriber.openai.OpenAI')
    def test_transcribe_audio_api_error(self, mock_openai, tmp_path):
        # Mock OpenAI client to raise an exception
        mock_client = MagicMock()
        mock_client.audio.transcriptions.create.side_effect = Exception("API error")
        mock_openai.return_value = mock_client
        
        # Create a temporary audio file
        audio_path = tmp_path / "audio.mp3"
        audio_path.write_bytes(b"\x00")

        # Mock environment variable
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            # Check that the function raises an exception
            with pytest.raises(Exception):
                transcribe_audio(str(audio_path))
    
    def test_transcribe_audio_file_not_found(self):
        # Mock environment variable
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            # Check that the function raises an exception
            with pytest.raises(FileNotFoundError):
                transcribe_audio("nonexistent_file.mp3")

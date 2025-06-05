"""
Unit tests for the downloader module.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from podcast_to_reels.downloader.downloader import download_audio

class TestDownloader:
    
    @patch('podcast_to_reels.downloader.downloader.subprocess.check_output')
    @patch('podcast_to_reels.downloader.downloader.subprocess.run')
    def test_download_audio_short_video(self, mock_run, mock_check_output):
        # Mock video duration to be less than requested duration
        mock_check_output.return_value = "30\n"
        
        # Call the function
        result = download_audio("https://youtu.be/dQw4w9WgXcQ", duration=60)
        
        # Check that the correct commands were called
        assert mock_check_output.call_count == 1
        assert mock_run.call_count == 1
        
        # Check that the output path is correct
        assert result == os.path.join("output", "audio.mp3")
    
    @patch('podcast_to_reels.downloader.downloader.subprocess.check_output')
    @patch('podcast_to_reels.downloader.downloader.subprocess.run')
    @patch('podcast_to_reels.downloader.downloader.tempfile.NamedTemporaryFile')
    def test_download_audio_long_video(self, mock_temp_file, mock_run, mock_check_output):
        # Mock video duration to be more than requested duration
        mock_check_output.return_value = "120\n"
        
        # Mock temporary file
        mock_temp = MagicMock()
        mock_temp.name = "/tmp/temp_audio.mp3"
        mock_temp_file.return_value = mock_temp
        
        # Call the function
        result = download_audio("https://youtu.be/dQw4w9WgXcQ", duration=60)
        
        # Check that the correct commands were called
        assert mock_check_output.call_count == 1
        assert mock_run.call_count == 2  # Download and trim
        
        # Check that the output path is correct
        assert result == os.path.join("output", "audio.mp3")
    
    @patch('podcast_to_reels.downloader.downloader.subprocess.check_output')
    def test_download_audio_error(self, mock_check_output):
        # Mock subprocess to raise an exception
        mock_check_output.side_effect = Exception("Command failed")
        
        # Check that the function raises an exception
        with pytest.raises(Exception):
            download_audio("https://youtu.be/invalid_url")

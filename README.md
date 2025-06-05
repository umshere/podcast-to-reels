# Podcast-to-Reels

An automated pipeline that converts YouTube science podcasts into visually engaging short-form video reels suitable for Instagram Reels/TikTok.

## Overview

This project provides an end-to-end solution for transforming dialogue-style science podcasts from YouTube into illustrated video reels. The pipeline:

1. Downloads audio from a YouTube URL
2. Transcribes the audio using OpenAI's Whisper API
3. Splits the transcript into semantic chunks
4. Generates vivid image prompts for each chunk
5. Creates images using Stability AI's API
6. Assembles a final video with synchronized audio and images

## Features

- Modular Python architecture with clean separation of concerns
- Robust error handling and retry mechanisms
- Comprehensive test suite with high coverage
- Detailed logging throughout the pipeline
- Configurable output parameters (duration, resolution, etc.)
- CI/CD integration via GitHub Actions
- Optional Flask web interface

## Requirements

- Python 3.11 or higher
- FFmpeg installed on your system
- OpenAI API key (for transcription and prompt generation)
- Stability AI API key (for image generation)

## Installation

### Option 1: Using pip

```bash
# Clone the repository
git clone https://github.com/yourusername/podcast-to-reels.git
cd podcast-to-reels

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Using Poetry (recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/podcast-to-reels.git
cd podcast-to-reels

# Install Poetry if you don't have it
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install
```

## Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` to add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   STABILITY_API_KEY=your_stability_api_key_here
   ```

## Usage

### Basic Usage

```bash
python scripts/run_pipeline.py --url <YOUTUBE_URL> --duration 60 --start-time 0
```

This will:
1. Download audio from the specified YouTube URL
2. Process it through the pipeline
3. Generate a video reel at `output/reel.mp4`

### Advanced Options

```bash
python scripts/run_pipeline.py --url <YOUTUBE_URL> --duration 30 --start-time 10 --output custom_output.mp4
```

### Web Interface

You can also run the pipeline through a simple Flask web app:

```bash
python -m web.app
```

Open your browser to `http://localhost:5000` and submit a YouTube URL with start
and duration values. The generated reel will appear in the `output/` folder.


## Pipeline Architecture

The pipeline consists of five main modules:

1. **Downloader** – [`downloader.py`](podcast_to_reels/downloader/downloader.py)
2. **Transcriber** – [`transcriber.py`](podcast_to_reels/transcriber/transcriber.py)
3. **Scene Splitter** – [`scene_splitter.py`](podcast_to_reels/scene_splitter/scene_splitter.py)
4. **Image Generator** – [`image_generator.py`](podcast_to_reels/image_generator/image_generator.py)
5. **Video Composer** – [`video_composer.py`](podcast_to_reels/video_composer/video_composer.py)

For a full diagram of how these components interact, see the [Architecture Diagram](docs/architecture_diagram.md).  Additional details for each module are provided in [Modules Overview](docs/modules_overview.md).

## Development

### Running Tests

Install the project in editable mode so that the `podcast_to_reels` package is
available on your Python path:

```bash
pip install -e .
```

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=podcast_to_reels tests/

# Run tests and generate HTML coverage report
pytest --cov=podcast_to_reels --cov-report=html tests/
```

### Project Structure

```
podcast-to-reels/
├── podcast_to_reels/       # Main package
│   ├── downloader/         # YouTube audio extraction
│   ├── transcriber/        # Audio to text conversion
│   ├── scene_splitter/     # Transcript chunking and prompt generation
│   ├── image_generator/    # Generate images from prompts
│   ├── video_composer/     # Assemble final video with audio
│   └── utils/              # Shared utilities
├── scripts/                # Command-line scripts
│   └── run_pipeline.py     # Main entry point
├── web/                    # Flask web application
│   └── templates/          # HTML templates
├── tests/                  # Unit tests
├── output/                 # Generated artifacts
├── docs/                   # Documentation
├── .github/workflows/      # CI configuration
├── requirements.txt        # Dependencies
└── README.md               # This file
```

## Deploy to Replit or Render

### Replit Deployment

1. Create a new Replit project and import from GitHub
2. Set environment variables in the Replit Secrets tab
3. Install dependencies with `pip install -r requirements.txt`
4. Run with `python scripts/run_pipeline.py --url <URL> --duration 30`

### Render Deployment

1. Create a new Web Service on Render
2. Connect to your GitHub repository
3. Set environment variables in the Render dashboard
4. Set the build command: `pip install -r requirements.txt`
5. Set the start command: `python scripts/run_pipeline.py --url <URL> --duration 30`

## Troubleshooting

### Common Issues

- **FFmpeg not found**: Ensure FFmpeg is installed and in your PATH
- **API rate limits**: The pipeline respects rate limits, but you may need to adjust timing
- **Memory issues**: Processing large videos may require significant memory

### API Costs

The pipeline is designed to keep cloud costs under $0.25 per run:
- OpenAI Whisper API: ~$0.10 per minute of audio
- GPT-4o-mini: ~$0.01 for prompt generation
- Stability AI: ~$0.02 per image (typically 5-10 images per minute)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube downloading
- [OpenAI](https://openai.com/) for transcription and text generation
- [Stability AI](https://stability.ai/) for image generation
- [MoviePy](https://zulko.github.io/moviepy/) for video composition

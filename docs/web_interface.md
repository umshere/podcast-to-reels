# Web Interface

This project includes a small Flask app that runs the entire pipeline from the browser.

## Running Locally

1. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in your API keys.
3. Start the Flask development server
   ```bash
   FLASK_APP=web/app.py flask run
   ```
4. Open your browser to `http://localhost:5000` and submit a YouTube URL with the start and end times for the clip.

The app will display progress messages and provide a link to download the generated reel when finished.

## Deployment

The web interface can be deployed to any platform that supports Python web applications. Set the start command to run `flask run` and ensure the environment variables from `.env` are configured.

## Directory

Generated files are saved under `output/web/`.

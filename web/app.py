"""Simple Flask UI for running the podcast-to-reels pipeline."""

from flask import (
    Flask,
    request,
    render_template,
    send_from_directory,
)
from pathlib import Path
import json
from uuid import uuid4

from podcast_to_reels.downloader import download_audio
from podcast_to_reels.transcriber import transcribe_audio
from podcast_to_reels.scene_splitter import split_scenes
from podcast_to_reels.image_generator import generate_images
from podcast_to_reels.video_composer import compose_video

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    """Render the form and handle pipeline execution."""
    if request.method == 'POST':
        url = request.form['url']
        start = int(request.form.get('start_time', 0))
        end = int(request.form.get('end_time', start + 60))
        duration = max(1, end - start)

        messages = []

        audio = download_audio(url, duration=duration, start_time=start)
        messages.append('Audio downloaded')

        transcript_path = transcribe_audio(audio)
        messages.append('Audio transcribed')

        try:
            with open(transcript_path) as f:
                data = json.load(f)
            full_text = data.get('text') or ' '.join(seg.get('text', '') for seg in data.get('segments', []))
            snippet = full_text[:200].strip()
            if snippet:
                messages.append(f'Transcript preview: {snippet}...')
        except Exception:
            pass

        scenes = split_scenes(transcript_path)
        messages.append('Scenes created')

        images = generate_images(scenes)
        messages.append('Images generated')

        out_dir = Path('output/web')
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = out_dir / f"reel_{uuid4().hex[:8]}.mp4"
        compose_video(audio, images, scenes, str(output_path))
        messages.append('Video composed')

        reel_link = url_for('download', filename=output_path.name)
        return render_template('result.html', messages=messages, reel_path=reel_link)

    return render_template('form.html')


@app.route('/download/<path:filename>')
def download(filename):
    """Serve generated video files."""
    return send_from_directory('output/web', filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


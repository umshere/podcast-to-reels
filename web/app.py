from flask import Flask, request, render_template_string
from pathlib import Path

from podcast_to_reels.downloader import download_audio
from podcast_to_reels.transcriber import transcribe_audio
from podcast_to_reels.scene_splitter import split_scenes
from podcast_to_reels.image_generator import generate_images
from podcast_to_reels.video_composer import compose_video

app = Flask(__name__)

FORM_HTML = """
<!doctype html>
<title>Podcast to Reels</title>
<h1>Create Reel</h1>
<form method=post>
  YouTube URL: <input type=text name=url required><br>
  Start time (sec): <input type=number name=start value=0><br>
  Duration (sec): <input type=number name=duration value=60><br>
  <input type=submit value='Generate'>
</form>
{% if output %}
<p>Video created: {{ output }}</p>
{% endif %}
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    output = None
    if request.method == 'POST':
        url = request.form['url']
        start = int(request.form.get('start', 0))
        duration = int(request.form.get('duration', 60))
        audio = download_audio(url, duration=duration, start_time=start)
        transcript = transcribe_audio(audio)
        scenes = split_scenes(transcript)
        images = generate_images(scenes)
        output_path = Path('output') / 'web_reel.mp4'
        compose_video(audio, images, scenes, str(output_path))
        output = str(output_path)
    return render_template_string(FORM_HTML, output=output)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


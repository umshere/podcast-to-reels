from flask import Flask, render_template, request
import os
from podcast_to_reels.downloader import download_audio
from podcast_to_reels.transcriber import transcribe_audio
from podcast_to_reels.scene_splitter import split_scenes
from podcast_to_reels.image_generator import generate_images
from podcast_to_reels.video_composer import compose_video

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        start_time = int(request.form.get('start_time', 0))
        end_time = int(request.form.get('end_time', 60))
        duration = max(0, end_time - start_time)

        output_dir = os.path.join('output', 'web')
        os.makedirs(output_dir, exist_ok=True)

        messages = []
        audio_path = download_audio(url, duration=duration, start_time=start_time, output_dir=output_dir)
        messages.append(f"Audio downloaded to: {audio_path}")

        transcript_path = transcribe_audio(audio_path, output_dir=output_dir)
        messages.append(f"Transcript saved to: {transcript_path}")

        scenes = split_scenes(transcript_path, output_dir=output_dir)
        messages.append(f"Generated {len(scenes)} scenes")

        images_dir = os.path.join(output_dir, 'images')
        image_paths = generate_images(scenes, output_dir=images_dir)
        messages.append(f"Generated {len(image_paths)} images")

        reel_path = compose_video(audio_path, image_paths, scenes, os.path.join(output_dir, 'reel.mp4'))
        messages.append(f"Video reel created at: {reel_path}")

        return render_template('result.html', messages=messages, reel_path=reel_path)

    return render_template('form.html')

if __name__ == '__main__':
    app.run(debug=True)

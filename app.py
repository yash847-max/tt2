from flask import Flask, request, render_template_string, url_for
from TTS.api import TTS  # Replace gTTS with Coqui TTS
import os
import uuid
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/audio'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Coqui TTS (CPU-friendly model)
tts = TTS(model_name="tts_models/en/ljspeech/glow-tts", progress_bar=False, gpu=False)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Coqui TTS Converter</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        textarea { width: 100%; height: 150px; margin-bottom: 10px; }
        button { padding: 10px 15px; background: #4CAF50; color: white; border: none; cursor: pointer; }
        audio { width: 100%; margin-top: 20px; }
        .error { color: red; }
    </style>
</head>
<body>
    <h1>Text-to-Speech Converter</h1>
    <form method="POST" action="/generate_tts">
        <textarea name="text" placeholder="Enter text here..." required>{{ text if text }}</textarea><br>
        <label>Speed: <input type="range" name="speed" min="0.5" max="2" step="0.1" value="{{ speed if speed else 1 }}"></label>
        <button type="submit">Generate Speech</button>
    </form>
    
    {% if error %}
        <p class="error">{{ error }}</p>
    {% endif %}
    
    {% if audio_url %}
        <audio controls>
            <source src="{{ audio_url }}" type="audio/wav">
        </audio>
        <a href="{{ audio_url }}" download="speech.wav">
            <button>Download Audio</button>
        </a>
    {% endif %}
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate_tts', methods=['POST'])
def generate_tts():
    text = request.form.get('text', '').strip()
    speed = float(request.form.get('speed', 1.0))
    
    if not text:
        return render_template_string(HTML_TEMPLATE, error="Please enter some text")
    
    try:
        filename = f"tts_{uuid.uuid4().hex}.wav"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Generate speech with Coqui TTS
        tts.tts_to_file(text=text, file_path=filepath, speed=speed)
        
        return render_template_string(
            HTML_TEMPLATE,
            audio_url=url_for('static', filename=f'audio/{filename}'),
            text=text,
            speed=speed
        )
    except Exception as e:
        return render_template_string(
            HTML_TEMPLATE,
            error=f"Error: {str(e)}",
            text=text,
            speed=speed
        )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

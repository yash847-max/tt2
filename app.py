from flask import Flask, request, send_file, render_template_string, redirect, url_for
from gtts import gTTS
import io
import os
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/audio'

# Create audio directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Premium TTS Converter</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #4361ee;
            --secondary: #3a0ca3;
            --accent: #7209b7;
            --light: #f8f9fa;
            --dark: #212529;
            --success: #4cc9f0;
        }
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            padding: 2rem;
            color: var(--dark);
            line-height: 1.6;
        }
        .container {
            max-width: 800px;
            margin: 2rem auto;
            background: white;
            padding: 2.5rem;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: var(--primary);
            text-align: center;
            margin-bottom: 1.5rem;
            font-weight: 600;
        }
        .description {
            text-align: center;
            margin-bottom: 2rem;
            color: #6c757d;
        }
        textarea {
            width: 100%;
            padding: 1.2rem;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            font-size: 1rem;
            min-height: 180px;
            margin-bottom: 1.8rem;
            transition: all 0.3s ease;
            resize: vertical;
            font-family: inherit;
        }
        textarea:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.2);
        }
        .controls {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.8rem;
            margin-bottom: 2rem;
        }
        .control-group {
            display: flex;
            flex-direction: column;
        }
        label {
            margin-bottom: 0.7rem;
            font-weight: 500;
            color: var(--dark);
            font-size: 0.95rem;
        }
        select {
            padding: 0.8rem;
            border-radius: 8px;
            border: 2px solid #e9ecef;
            font-family: inherit;
            background-color: white;
            transition: all 0.3s;
        }
        select:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.2);
        }
        .range-container {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        input[type="range"] {
            flex: 1;
            -webkit-appearance: none;
            height: 8px;
            border-radius: 4px;
            background: #e9ecef;
            outline: none;
        }
        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: var(--primary);
            cursor: pointer;
            transition: all 0.2s;
        }
        input[type="range"]::-webkit-slider-thumb:hover {
            transform: scale(1.1);
            background: var(--secondary);
        }
        .speed-value {
            min-width: 40px;
            text-align: center;
            font-weight: 500;
            color: var(--primary);
        }
        .buttons {
            display: flex;
            gap: 1rem;
            margin-top: 1.5rem;
        }
        button {
            flex: 1;
            background: var(--primary);
            color: white;
            border: none;
            padding: 1rem;
            font-size: 1rem;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }
        button:hover {
            background: var(--secondary);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        button:active {
            transform: translateY(0);
        }
        button.secondary {
            background: white;
            color: var(--primary);
            border: 2px solid var(--primary);
        }
        button.secondary:hover {
            background: #f0f4ff;
        }
        .audio-container {
            margin-top: 2.5rem;
            padding: 1.5rem;
            background: #f8f9fa;
            border-radius: 10px;
            animation: fadeIn 0.5s ease;
            display: {% if audio_url %}block{% else %}none{% endif %};
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .audio-title {
            color: var(--dark);
            margin-bottom: 1rem;
            font-weight: 500;
        }
        audio {
            width: 100%;
            margin: 1rem 0;
        }
        .audio-controls {
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
        }
        .play-btn {
            background: var(--success);
        }
        .play-btn:hover {
            background: #3aa8d8;
        }
        .download-btn {
            background: var(--accent);
        }
        .download-btn:hover {
            background: #5a189a;
        }
        .error {
            color: #d62828;
            margin-top: 1rem;
            text-align: center;
            font-weight: 500;
        }
        .icon {
            width: 18px;
            height: 18px;
        }
        .hidden {
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Premium TTS Converter</h1>
        <p class="description">Convert any text to natural sounding speech with customizable voice options</p>
        
        <form action="/generate_tts" method="post">
            <textarea name="text" placeholder="Enter your text here..." required>{{ text if text }}</textarea>
            
            <div class="controls">
                <div class="control-group">
                    <label for="voice_type">Voice Type</label>
                    <select name="voice_type" id="voice_type">
                        <option value="male" {% if voice_type == 'male' %}selected{% endif %}>Male Voice</option>
                        <option value="female" {% if voice_type == 'female' %}selected{% endif %}>Female Voice</option>
                    </select>
                </div>
                
                <div class="control-group">
                    <label for="speed">Speech Speed</label>
                    <div class="range-container">
                        <input type="range" name="speed" id="speed" min="0.5" max="2" step="0.1" value="{{ speed }}">
                        <span class="speed-value" id="speedValue">{{ speed }}x</span>
                    </div>
                </div>
            </div>
            
            <div class="buttons">
                <button type="submit">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                    </svg>
                    Generate Speech
                </button>
            </div>
        </form>
        
        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}
        
        <div class="audio-container" id="audioContainer">
            <h3 class="audio-title">Your Generated Audio</h3>
            <audio controls id="audioPlayer" {% if not audio_url %}class="hidden"{% endif %}>
                {% if audio_url %}
                <source src="{{ audio_url }}" type="audio/mpeg">
                {% endif %}
            </audio>
            
            {% if audio_url %}
            <div class="audio-controls">
                <button class="play-btn" id="playBtn">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Play Audio
                </button>
                <a href="{{ audio_url }}" download="speech.mp3">
                    <button class="download-btn">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                        Download MP3
                    </button>
                </a>
            </div>
            {% endif %}
        </div>
    </div>

    <script>
        // Update speed value display
        const speedSlider = document.getElementById('speed');
        const speedValue = document.getElementById('speedValue');
        
        if (speedSlider && speedValue) {
            speedSlider.addEventListener('input', () => {
                speedValue.textContent = speedSlider.value + 'x';
            });
        }

        // Audio player controls
        document.addEventListener('DOMContentLoaded', () => {
            const audioPlayer = document.getElementById('audioPlayer');
            const playBtn = document.getElementById('playBtn');
            const audioContainer = document.getElementById('audioContainer');
            
            if (audioPlayer && playBtn) {
                // Show audio container if audio exists
                if (audioPlayer.children.length > 0) {
                    audioContainer.style.display = 'block';
                }
                
                // Custom play button functionality
                playBtn.addEventListener('click', () => {
                    if (audioPlayer.paused) {
                        audioPlayer.play();
                        playBtn.innerHTML = `
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            Pause Audio
                        `;
                    } else {
                        audioPlayer.pause();
                        playBtn.innerHTML = `
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            Play Audio
                        `;
                    }
                });
                
                // Update button when audio ends
                audioPlayer.addEventListener('ended', () => {
                    playBtn.innerHTML = `
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Play Again
                    `;
                });
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate_tts', methods=['POST'])
def generate_tts():
    text = request.form.get('text', '').strip()
    voice_type = request.form.get('voice_type', 'male')
    speed = float(request.form.get('speed', 1.0))
    
    if not text:
        return render_template_string(HTML_TEMPLATE, error="Please enter some text to convert")
    
    try:
        # Generate unique filename
        filename = f"tts_{uuid.uuid4().hex}.mp3"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Adjust parameters based on voice type
        lang = 'en-us' if voice_type == 'male' else 'en'
        
        # Create TTS with adjusted speed (gTTS doesn't support speed directly, we use slow param)
        slow = speed < 0.8  # For very slow speeds
        tts = gTTS(text=text, lang=lang, slow=slow)
        
        # Save to file
        tts.save(filepath)
        
        # Clean up old files (keep only the 5 most recent)
        audio_files = sorted(
            [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.startswith('tts_')],
            key=lambda x: os.path.getmtime(os.path.join(app.config['UPLOAD_FOLDER'], x)),
            reverse=True
        )
        for old_file in audio_files[5:]:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], old_file))
        
        return render_template_string(HTML_TEMPLATE,
                                   audio_url=url_for('static', filename=f'audio/{filename}'),
                                   text=text,
                                   voice_type=voice_type,
                                   speed=speed)
        
    except Exception as e:
        return render_template_string(HTML_TEMPLATE,
                                    text=text,
                                    voice_type=voice_type,
                                    speed=speed,
                                    error=f"Error generating speech: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)
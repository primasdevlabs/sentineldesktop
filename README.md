# Sentinel AI Assistant (JARVIS-Style)

Sentinel is a modular, event-driven, and highly extensible desktop AI assistant built in Python. It features wake-word detection, clap triggers, a futuristic liquid-orb UI, and neural voice synthesis.

---

## 🚀 Features

- **Wake Triggers**: Voice ("Sentinel") via Picovoice Porcupine & Double-Clap detection.
- **Neural TTS**: Real-time streaming human-like voice via ElevenLabs.
- **Conversational Brain**: Context-aware dialogue using Gemini 3.1.
- **Visuals**: Immersive, liquid-reactive Orb UI using PyQt6 and GLSL shaders.
- **Modular Skills**: Time, Date, and API-integrated Weather.

---

## 🛠 Prerequisites

Ensure you have the following installed on your system:
- **Python 3.9+**
- **mpv** (required for ElevenLabs audio streaming)
- **Balabolka/balcon.exe** (optional fallback for offline TTS)
- **Rhasspy** (for Speech-to-Text and NLU)

---

## 📦 Installation

1. **Clone the project** (or copy the `sentinel/` directory to your machine).
2. **Install Python dependencies**:
   ```bash
   pip install -r sentinel/requirements.txt
   ```
3. **Install System Dependencies** (example for Linux):
   ```bash
   # Ubuntu/Debian
   sudo apt-get install mpv libasound2-dev
   ```

---

## ⚙️ Configuration

Open `sentinel/config/config.yaml` and update the following:

### 1. Wake Word (Picovoice)
Get your free AccessKey at [Picovoice Console](https://console.picovoice.ai/).
```yaml
assistant:
  access_key: "YOUR_PICOVOICE_ACCESS_KEY"
```

### 2. Neural Voice (ElevenLabs)
Get your API key at [ElevenLabs](https://elevenlabs.io/).
**Set the environment variable**:
```bash
# Windows
set ELEVENLABS_API_KEY=your_key_here
# Linux/Mac
export ELEVENLABS_API_KEY=your_key_here
```

### 3. Weather (OpenWeatherMap)
Get your API key at [OpenWeatherMap](https://openweathermap.org/api).
```yaml
weather:
  api_key: "YOUR_API_KEY"
  city: "Your City"
```

### 4. STT (Rhasspy)
Ensure your Rhasspy instance is running and update the URL:
```yaml
rhasspy:
  url: "http://localhost:12101"
```

---

## 🎮 Usage

Run the assistant:
```bash
python -m sentinel.main
```

### Interaction:
- **Wake Word**: Say "Sentinel" followed by your request.
- **Clap**: Perform a double-clap to trigger listening mode.
- **UI**: 
  - **Double-click** the floating orb to enter/exit **Fullscreen Immersive Mode**.
  - **Interruption**: Speak while Sentinel is talking to instantly interrupt and start a new command.
- **Context Exit**: Say "Sentinel, stop" or "Never mind" to clear conversation memory.

---

## 🖥️ Always-On Mode (Autostart)

Sentinel is designed to be a background daemon. You have two options for autostart:

### Option 1: Automatic Registration (Recommended)
Open `sentinel/config/config.yaml` and set:
```yaml
system:
  autostart: true
  start_minimized: true
```
The next time you run `python -m sentinel.main`, Sentinel will register itself in your system's startup sequence (Windows Registry or Linux XDG).

### Option 2: Manual Windows Shortcut
1. Press `Win + R`, type `shell:startup`, and press Enter.
2. Right-click > New > Shortcut.
3. Target: `pythonw.exe C:\Path\To\Sentinel\jarvis\main.py` (using `pythonw` hides the console window).

---

## 🧩 Adding New Skills

Sentinel is modular. To add a new capability:
1. Create a folder in `sentinel/modules/skills/`.
2. Inherit from `BaseSkill` in `skill.py`.
3. Register the skill in `sentinel/main.py`.

---

## ⚠️ Troubleshooting

- **Mic Conflict**: Ensure only one process is accessing the microphone.
- **TTS Delay**: Check your internet connection for ElevenLabs or verify `mpv` is in your system PATH.
- **UI Performance**: Ensure your GPU drivers support OpenGL 3.3+.
-e 
### OpenRouter Integration
To use free models via OpenRouter, update `sentinel/config/config.yaml`:
```yaml
assistant:
  model: "openrouter/google/gemini-2.0-flash-lite:free"
```

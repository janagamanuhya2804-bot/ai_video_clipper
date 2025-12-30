# ContentAutomator

Transform your videos into engaging short-form clips with AI-generated music.

## Features

- 🎤 **Automatic Transcription** - Extract text from videos using Whisper
- 🤖 **AI Clip Analysis** - Gemini AI identifies the best moments
- 🎵 **Custom Music** - Stability AI generates background music
- ✂️ **Video Clipping** - Precise video segment extraction

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up API keys** (optional for demo mode):
   ```bash
   # Create .env file
   GEMINI_API_KEY=your_gemini_key
   STABILITY_API_KEY=your_stability_key
   ```

3. **Run the app:**
   ```bash
   streamlit run ui/app.py
   ```

4. **Use the interface:**
   - Upload a video or paste a transcript
   - Click "Generate Clips"
   - Download your clips and music

## Demo Mode

Try the full functionality without API keys:
- ✅ Sample content included
- ✅ Pre-generated clips and music
- ✅ All download features work
- ✅ Perfect for testing and demos

## Requirements

- Python 3.8+
- FFmpeg (for video processing)
- API keys (optional for demo mode)

## Output

- Video clips (MP4)
- Background music (MP3)
- Clip metadata (JSON)
- ZIP download with everything

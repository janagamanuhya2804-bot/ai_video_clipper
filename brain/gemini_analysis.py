import os
import json
import time
from typing import List, Dict
from dotenv import load_dotenv

# Modern Gemini SDK
import google.generativeai as genai

# ============================================================
# LOAD ENV
# ============================================================

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# ============================================================
# CONFIG
# ============================================================

MODEL_NAME = "gemini-2.0-flash"
CHUNK_SIZE = 40
MAX_OUTPUT_TOKENS = 512
TEMPERATURE = 0.4
MAX_RETRIES = 3

# ============================================================
# GEMINI SETUP (MODERN WAY)
# ============================================================

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    generation_config={
        "temperature": TEMPERATURE,
        "max_output_tokens": MAX_OUTPUT_TOKENS,
    },
)

# ============================================================


def _call_gemini(prompt: str) -> str:
    for attempt in range(MAX_RETRIES):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                raise
            wait = 2 ** attempt
            print(f"[Gemini] Error, retrying in {wait}s: {e}")
            time.sleep(wait)



def _build_prompt(segments: List[Dict]) -> str:
    transcript_text = "\n".join(
        f"[{s['start']:.2f} - {s['end']:.2f}] {s['text']}"
        for s in segments
    )

    return f"""
You are a professional video editor.

From the transcript below, select 2–3 engaging video clips.

Rules:
- Each clip must be 5–30 seconds
- Use timestamps exactly
- Return ONLY valid JSON
- No markdown
- No explanations

JSON format:
{{
  "clips": [
    {{
      "start": "HH:MM:SS",
      "end": "HH:MM:SS",
      "hook": "short engaging description",
      "music_mood": "energetic | calm | cinematic | hype"
    }}
  ]
}}

Transcript:
{transcript_text}
""".strip()



def _safe_json_load(text: str) -> Dict:
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError("No JSON found in Gemini response")
    return json.loads(text[start:end])


# ============================================================
# MAIN ANALYSIS
# ============================================================


def analyze_transcript(transcript: dict) -> dict:
    segments = transcript.get("segments", [])
    if not segments:
        return {"clips": []}

    all_clips = []

    for i in range(0, len(segments), CHUNK_SIZE):
        chunk = segments[i : i + CHUNK_SIZE]
        prompt = _build_prompt(chunk)

        try:
            raw_text = _call_gemini(prompt)
            parsed = _safe_json_load(raw_text)
            clips = parsed.get("clips", [])
            if not isinstance(clips, list):
                raise ValueError("'clips' is not a list")
            all_clips.extend(clips)
        except Exception as e:
            print("[Gemini] Chunk failed:", e)

    if not all_clips:
        print("[Demo Mode] Using fallback clips")
        return {
            "clips": [
                {
                    "start": "00:00:10",
                    "end": "00:00:45",
                    "hook": "Key insight that hooks the viewer",
                    "music_mood": "energetic",
                }
            ]
        }

    return {"clips": all_clips}

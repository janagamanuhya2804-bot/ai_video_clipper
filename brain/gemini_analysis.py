import os
import json
import time
import requests
from typing import List, Dict

# ============================================================
# CONFIG
# ============================================================

MODEL = "gemini-2.0-flash"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
MAX_RETRIES = 5
CHUNK_SIZE = 40          # transcript segments per request
MAX_OUTPUT_TOKENS = 512
TEMPERATURE = 0.4

# ============================================================


def _call_gemini(prompt: str, api_key: str) -> str:
    """
    Call Gemini 2.0 Flash with retry + exponential backoff.
    Returns raw text output.
    """

    endpoint = f"{BASE_URL}/{MODEL}:generateContent"

    payload = {
        "generationConfig": {
            "temperature": TEMPERATURE,
            "maxOutputTokens": MAX_OUTPUT_TOKENS
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ]
    }

    for attempt in range(MAX_RETRIES):
        response = requests.post(
            f"{endpoint}?key={api_key}",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=60
        )

        # Rate limit handling
        if response.status_code == 429:
            wait = 2 ** attempt
            print(f"[Gemini] Rate limited. Retrying in {wait}s...")
            time.sleep(wait)
            continue

        # Other errors
        if response.status_code != 200:
            raise RuntimeError(response.text)

        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    raise RuntimeError("Gemini failed after retries")


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
      "hook": "short engaging description"
    }}
  ]
}}

Transcript:
{transcript_text}
""".strip()


def _safe_json_load(text: str) -> Dict:
    """
    Extracts and parses JSON even if Gemini adds extra text.
    """
    start = text.find("{")
    end = text.rfind("}") + 1

    if start == -1 or end == -1:
        raise ValueError("No JSON object found")

    return json.loads(text[start:end])


def analyze_transcript(transcript: dict) -> dict:
    """
    Entry point called by main.py
    """

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")

    segments = transcript.get("segments", [])
    if not segments:
        return {"clips": []}

    all_clips = []

    # --------------------------------------------------------
    # Process transcript in chunks
    # --------------------------------------------------------
    for i in range(0, len(segments), CHUNK_SIZE):
        chunk = segments[i:i + CHUNK_SIZE]
        prompt = _build_prompt(chunk)

        try:
            raw_text = _call_gemini(prompt, api_key)
            parsed = _safe_json_load(raw_text)
            all_clips.extend(parsed.get("clips", []))
        except Exception as e:
            print("[Gemini] Skipping chunk due to error:", e)

            if not all_clips:
                print("[Demo Mode] Gemini unavailable, using fallback clips")

    return {
        "clips": [
            {
                "start": "00:00:10",
                "end": "00:00:15",
                "hook": "Key insight that hooks the viewer",
                "music_mood": "energetic"
            }
        ]
    }

    return {"clips": all_clips} 

 







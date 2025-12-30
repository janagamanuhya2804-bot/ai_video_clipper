import os
import requests
from typing import Dict, List
from datetime import timedelta
import time

# ============================================================
# CONFIG
# ============================================================

STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
STABILITY_BASE_URL = "https://api.stability.ai/v2beta/audio/stable-audio-2/text-to-audio"

# Note: STABILITY_API_KEY is optional - will use mock data if not available

# ============================================================
# UTILS
# ============================================================


def seconds_to_hhmmss(seconds: float) -> str:
    return str(timedelta(seconds=int(seconds))).zfill(8)


# ============================================================
# TRANSCRIPT SLICE
# ============================================================


def extract_transcript_for_clip(segments: List[Dict], start: str, end: str) -> str:
    """
    start, end: HH:MM:SS
    Returns transcript text falling inside this time window
    """

    def to_seconds(ts: str) -> float:
        h, m, s = ts.split(":")
        return int(h) * 3600 + int(m) * 60 + int(s)

    start_s = to_seconds(start)
    end_s = to_seconds(end)

    texts = []
    for seg in segments:
        if seg["end"] >= start_s and seg["start"] <= end_s:
            texts.append(seg["text"])

    return " ".join(texts)


# ============================================================
# STABILITY AI MUSIC GENERATION
# ============================================================


def generate_background_music(prompt_text: str, mood: str) -> Dict:
    """
    Generate background music using Stability AI's Stable Audio API or return mock data if API is unavailable
    """
    
    # If no API key, return mock data
    if not STABILITY_API_KEY:
        print(f"[Stability] No API key found, using mock music for mood: {mood}")
        return {
            "id": f"mock_music_{int(time.time())}",
            "status": "completed",
            "url": None,
            "title": f"Background Music - {mood.title()}",
            "mood": mood,
            "prompt": prompt_text[:100] + "..." if len(prompt_text) > 100 else prompt_text,
            "mock": True
        }
    
    # Prepare data for Stability AI Stable Audio (using form data format)
    data = {
        "prompt": f"Instrumental background music, {mood} mood. {prompt_text[:200]}",
        "output_format": "mp3",
        "duration": 20,  # 20 seconds as shown in example
        "model": "stable-audio-2.5"
    }

    headers = {
        "authorization": f"Bearer {STABILITY_API_KEY}",
        "accept": "audio/*"
    }

    # Use form data format with empty files dict as shown in the example
    files = {"none": ""}

    try:
        response = requests.post(
            STABILITY_BASE_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=60,  # Music generation can take longer
        )

        if response.status_code == 200:
            # Direct audio response - save to file
            audio_filename = f"generated_music_{int(time.time())}.mp3"
            audio_path = f"output/{audio_filename}"
            
            os.makedirs("output", exist_ok=True)
            with open(audio_path, 'wb') as f:
                f.write(response.content)
            
            print(f"[Stability] Successfully generated music: {audio_path}")
            return {
                "id": f"stability_music_{int(time.time())}",
                "status": "completed",
                "url": audio_path,
                "title": f"Background Music - {mood.title()}",
                "mood": mood,
                "prompt": data["prompt"],
                "duration": 20,
                "file_path": audio_path
            }
        
        elif response.status_code == 503:
            print(f"[Stability] Service temporarily unavailable, using mock music for mood: {mood}")
            return {
                "id": f"mock_music_{int(time.time())}",
                "status": "service_unavailable",
                "url": None,
                "title": f"Background Music - {mood.title()}",
                "mood": mood,
                "prompt": data["prompt"],
                "mock": True,
                "error": "Stability AI temporarily unavailable"
            }
        
        elif response.status_code == 401:
            print(f"[Stability] Invalid API key, using mock music")
            return {
                "id": f"mock_music_{int(time.time())}",
                "status": "auth_error",
                "url": None,
                "title": f"Background Music - {mood.title()}",
                "mood": mood,
                "prompt": data["prompt"],
                "mock": True,
                "error": "Invalid Stability AI API key"
            }
        
        else:
            # Handle other error responses
            try:
                error_info = response.json()
                error_msg = str(error_info)
            except:
                error_msg = response.text
            
            print(f"[Stability] API error {response.status_code}: {error_msg}")
            return {
                "id": f"mock_music_{int(time.time())}",
                "status": "api_error",
                "url": None,
                "title": f"Background Music - {mood.title()}",
                "mood": mood,
                "prompt": data["prompt"],
                "mock": True,
                "error": f"API returned {response.status_code}: {error_msg}"
            }
        
    except requests.exceptions.RequestException as e:
        print(f"[Stability] Request failed: {e}, using mock music")
        return {
            "id": f"mock_music_{int(time.time())}",
            "status": "request_failed",
            "url": None,
            "title": f"Background Music - {mood.title()}",
            "mood": mood,
            "prompt": f"Instrumental background music, {mood} mood. {prompt_text[:200]}",
            "mock": True,
            "error": str(e)
        }


# ============================================================
# MAIN PIPELINE STEP
# ============================================================


def generate_music_for_clips(transcript: Dict, clips: List[Dict]) -> List[Dict]:
    """
    Returns clips with background_music_url attached
    """

    segments = transcript.get("segments", [])

    enriched = []
    for i, clip in enumerate(clips, 1):
        print(f"[Music] Generating music for clip {i}/{len(clips)}")
        
        text_context = extract_transcript_for_clip(
            segments,
            clip["start"],
            clip["end"],
        )

        try:
            music = generate_background_music(
                prompt_text=text_context,
                mood=clip.get("music_mood", "cinematic"),
            )
            clip["background_music"] = music
            print(f"[Music] Clip {i} music: {music.get('status', 'unknown')}")
            
        except Exception as e:
            print(f"[Music] Failed to generate music for clip {i}: {e}")
            clip["background_music"] = {
                "id": f"error_music_{i}",
                "status": "error",
                "url": None,
                "title": f"Music Generation Failed",
                "mood": clip.get("music_mood", "cinematic"),
                "error": str(e),
                "mock": True
            }

        enriched.append(clip)

    return enriched
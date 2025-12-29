import whisper


def generate_transcript(video_path: str) -> dict:
    """
    Returns:
    {
        "text": full_transcript,
        "segments": [
            { "start": float, "end": float, "text": str }
        ]
    }
    """

    model = whisper.load_model("base")
    result = model.transcribe(video_path)

    transcript = {
        "text": result["text"],
        "segments": []
    }

    for seg in result["segments"]:
        transcript["segments"].append({
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"]
        })

    return transcript

import json
from brain.transcript import generate_transcript
from brain.gemini_analysis import analyze_transcript
from brain.clipper import cut_clips


if __name__ == "__main__":
    video_path = "input/sample.mp4"

    transcript = generate_transcript(video_path)
    clips_json = analyze_transcript(transcript)

    # 👇 SEE GEMINI OUTPUT
    print("\n=== CLIP SUGGESTIONS ===")
    print(json.dumps(clips_json, indent=2))

    # 👇 SAVE IT
    with open("clips.json", "w", encoding="utf-8") as f:
        json.dump(clips_json, f, indent=2)

    print("\nSaved clips.json")

    cut_clips(video_path, clips_json)




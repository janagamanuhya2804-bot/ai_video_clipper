from brain.transcript import generate_transcript
from brain.gemini_analysis import analyze_transcript
from brain.stability_music_generation import generate_music_for_clips

if __name__ == "__main__":
    video_path = "/home/dawn/Downloads/processed_videoplayback.mp4"
    
    print("🎤 Generating transcript...")
    transcript = generate_transcript(video_path)
    
    print("🤖 Analyzing content...")
    analysis = analyze_transcript(transcript)
    
    print("🎵 Generating music...")
    final_clips = generate_music_for_clips(transcript=transcript, clips=analysis["clips"])
    
    print("✅ Complete!")
    print(f"Generated {len(final_clips)} clips with music")




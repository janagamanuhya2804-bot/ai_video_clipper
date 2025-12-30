"""
Demo data and mock functions for the content automation system
"""
import os
import shutil
from typing import Dict, List
import time

# Demo transcript data
DEMO_TRANSCRIPT = {
    "text": "Welcome to our amazing product demonstration. Today we're going to show you how artificial intelligence can transform your content creation workflow. This revolutionary technology analyzes your videos and automatically generates engaging short-form clips. The AI understands context, identifies key moments, and even suggests the perfect background music for each clip. Whether you're a content creator, marketer, or educator, this tool will save you hours of manual editing work.",
    "segments": [
        {
            "start": 0.0,
            "end": 15.0,
            "text": "Welcome to our amazing product demonstration. Today we're going to show you how artificial intelligence can transform your content creation workflow."
        },
        {
            "start": 15.0,
            "end": 30.0,
            "text": "This revolutionary technology analyzes your videos and automatically generates engaging short-form clips."
        },
        {
            "start": 30.0,
            "end": 45.0,
            "text": "The AI understands context, identifies key moments, and even suggests the perfect background music for each clip."
        },
        {
            "start": 45.0,
            "end": 60.0,
            "text": "Whether you're a content creator, marketer, or educator, this tool will save you hours of manual editing work."
        }
    ]
}

# Demo clips data
DEMO_CLIPS = [
    {
        "start": "00:00:00",
        "end": "00:00:15",
        "hook": "Revolutionary AI transforms content creation workflow",
        "music_mood": "energetic"
    },
    {
        "start": "00:00:15",
        "end": "00:00:30",
        "hook": "Automatic short-form clip generation technology",
        "music_mood": "cinematic"
    },
    {
        "start": "00:00:30",
        "end": "00:00:45",
        "hook": "AI understands context and identifies key moments",
        "music_mood": "uplifting"
    }
]

def get_demo_transcript(video_path: str = None) -> Dict:
    """Return demo transcript data"""
    print("[Demo] Using demo transcript data")
    return DEMO_TRANSCRIPT

def get_demo_analysis(transcript: Dict) -> Dict:
    """Return demo analysis with clips"""
    print("[Demo] Using demo clip analysis")
    return {"clips": DEMO_CLIPS.copy()}

def get_demo_music_for_clips(transcript: Dict, clips: List[Dict]) -> List[Dict]:
    """Return clips with demo music data"""
    print("[Demo] Using demo music generation")
    
    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)
    
    # Copy existing demo audio files or create references
    demo_audio_files = [
        "output/generated_music_1767037003.mp3",
        "output/demo_music_energetic.mp3",
        "output/demo_music_cinematic.mp3",
        "output/demo_music_uplifting.mp3"
    ]
    
    enriched_clips = []
    for i, clip in enumerate(clips, 1):
        # Use existing audio file if available, otherwise create a mock reference
        audio_file = None
        if i <= len(demo_audio_files) and os.path.exists(demo_audio_files[i-1]):
            audio_file = demo_audio_files[i-1]
        elif os.path.exists("output/generated_music_1767037003.mp3"):
            # Use the existing generated music file for all clips in demo
            audio_file = "output/generated_music_1767037003.mp3"
        
        clip["background_music"] = {
            "id": f"demo_music_{i}",
            "status": "completed",
            "url": audio_file,
            "title": f"Demo Background Music - {clip.get('music_mood', 'cinematic').title()}",
            "mood": clip.get('music_mood', 'cinematic'),
            "prompt": f"Instrumental background music, {clip.get('music_mood', 'cinematic')} mood. Demo content for content automation system.",
            "duration": 20,
            "demo": True
        }
        
        enriched_clips.append(clip)
    
    return enriched_clips

def setup_demo_video_clips():
    """Set up demo video clips by copying existing clip or creating placeholders"""
    os.makedirs("output", exist_ok=True)
    
    # If we have an existing clip, use it for all demo clips
    existing_clip = "output/clip_1.mp4"
    
    if os.path.exists(existing_clip):
        # Copy the existing clip to create demo clips
        for i in range(1, 4):  # Create 3 demo clips
            demo_clip_path = f"output/demo_clip_{i}.mp4"
            if not os.path.exists(demo_clip_path):
                try:
                    shutil.copy2(existing_clip, demo_clip_path)
                    print(f"[Demo] Created demo clip: {demo_clip_path}")
                except Exception as e:
                    print(f"[Demo] Could not copy clip: {e}")

def get_demo_video_clips(video_path: str, clips_data: Dict):
    """Mock video clipping for demo mode"""
    print("[Demo] Using demo video clips")
    
    # Set up demo clips
    setup_demo_video_clips()
    
    # Return success - clips are already set up
    return True

def create_demo_audio_files():
    """Create or ensure demo audio files exist"""
    os.makedirs("output", exist_ok=True)
    
    # If we have the generated music file, create copies with descriptive names
    source_audio = "output/generated_music_1767037003.mp3"
    
    if os.path.exists(source_audio):
        demo_files = [
            "output/demo_music_energetic.mp3",
            "output/demo_music_cinematic.mp3", 
            "output/demo_music_uplifting.mp3"
        ]
        
        for demo_file in demo_files:
            if not os.path.exists(demo_file):
                try:
                    shutil.copy2(source_audio, demo_file)
                    print(f"[Demo] Created demo audio: {demo_file}")
                except Exception as e:
                    print(f"[Demo] Could not copy audio: {e}")

# Initialize demo files when module is imported
create_demo_audio_files()
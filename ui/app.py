import streamlit as st
import json
import sys
import os
import zipfile
from pathlib import Path

# Allow imports from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from brain.transcript import generate_transcript
from brain.gemini_analysis import analyze_transcript
from brain.stability_music_generation import generate_music_for_clips
from brain.clipper import cut_clips
from brain.demo_data import (
    get_demo_transcript, 
    get_demo_analysis, 
    get_demo_music_for_clips, 
    get_demo_video_clips
)

# Helper functions
def get_video_path(clip_idx, demo_mode):
    """Get the correct video path based on mode"""
    if demo_mode:
        demo_path = f"output/demo_clip_{clip_idx}.mp4"
        if os.path.exists(demo_path):
            return demo_path
        elif os.path.exists("output/clip_1.mp4"):
            return "output/clip_1.mp4"
    else:
        regular_path = f"output/clip_{clip_idx}.mp4"
        if os.path.exists(regular_path):
            return regular_path
    return None

def create_zip_file(clips, has_video, demo_mode):
    """Create ZIP file with all content"""
    try:
        os.makedirs("output", exist_ok=True)
        zip_path = "output/all_clips.zip"
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            # Add clips data
            clips_json = json.dumps({"clips": clips}, indent=2)
            zipf.writestr("clips.json", clips_json)
            
            for idx, clip in enumerate(clips, 1):
                # Add video
                if has_video:
                    video_path = get_video_path(idx, demo_mode)
                    if video_path:
                        zipf.write(video_path, f"videos/clip_{idx}.mp4")
                
                # Add audio
                if "background_music" in clip and clip["background_music"].get("url"):
                    audio_path = clip["background_music"]["url"]
                    if os.path.exists(audio_path):
                        zipf.write(audio_path, f"audio/music_{idx}.mp3")
        
        return zip_path
    except Exception as e:
        st.error(f"Failed to create ZIP: {e}")
        return None

st.set_page_config(
    page_title="Content Automation",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for aesthetic dark theme
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main app styling */
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Inter', sans-serif;
        color: #e2e8f0;
    }
    
    /* Main container */
    .main-container {
        background: rgba(30, 41, 59, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 3rem;
        margin: 2rem auto;
        max-width: 1200px;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(148, 163, 184, 0.1);
    }
    
    /* Header styling */
    .header {
        text-align: center;
        margin-bottom: 3rem;
    }
    
    .header h1 {
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    
    .header p {
        color: #94a3b8;
        font-size: 1.2rem;
        font-weight: 400;
        margin-bottom: 2rem;
    }
    
    /* Card styling */
    .card {
        background: rgba(51, 65, 85, 0.8);
        border-radius: 20px;
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(148, 163, 184, 0.1);
        transition: all 0.4s ease;
    }
    
    .card:hover {
        transform: translateY(-4px);
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
        border-color: rgba(96, 165, 250, 0.3);
    }
    
    /* Input section styling */
    .input-section {
        background: linear-gradient(135deg, rgba(51, 65, 85, 0.9) 0%, rgba(30, 41, 59, 0.9) 100%);
        border-radius: 20px;
        padding: 2.5rem;
        margin: 2rem 0;
        border: 2px solid rgba(96, 165, 250, 0.2);
        backdrop-filter: blur(10px);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #ec4899 100%);
        color: white;
        border: none;
        border-radius: 16px;
        padding: 1rem 2.5rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.4s ease;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 40px rgba(59, 130, 246, 0.6);
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 50%, #db2777 100%);
    }
    
    /* Clip card styling */
    .clip-card {
        background: linear-gradient(135deg, rgba(71, 85, 105, 0.8) 0%, rgba(51, 65, 85, 0.8) 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        border: 1px solid rgba(148, 163, 184, 0.15);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
        transition: all 0.4s ease;
        backdrop-filter: blur(10px);
    }
    
    .clip-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 45px rgba(0, 0, 0, 0.25);
        border-color: rgba(167, 139, 250, 0.4);
    }
    
    /* Download section */
    .download-section {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
        border-radius: 20px;
        padding: 2.5rem;
        margin: 2rem 0;
        border: 2px solid rgba(16, 185, 129, 0.3);
        backdrop-filter: blur(10px);
    }
    
    /* Success/Info messages */
    .stSuccess {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.15) 100%);
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-radius: 16px;
        color: #10b981;
    }
    
    .stInfo {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(37, 99, 235, 0.15) 100%);
        border: 1px solid rgba(59, 130, 246, 0.4);
        border-radius: 16px;
        color: #3b82f6;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.15) 100%);
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-radius: 16px;
        color: #ef4444;
    }
    
    /* Demo mode badge */
    .demo-badge {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(217, 119, 6, 0.2) 100%);
        color: #f59e0b;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 0.95rem;
        display: inline-block;
        margin: 0.5rem 0;
        border: 1px solid rgba(245, 158, 11, 0.4);
        backdrop-filter: blur(10px);
    }
    
    /* Text styling */
    h1, h2, h3, h4, h5, h6 {
        color: #f1f5f9;
    }
    
    p, div, span {
        color: #cbd5e1;
    }
    
    /* Animated elements */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(40px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in {
        animation: fadeInUp 0.8s ease-out;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #ec4899 100%);
    }
    
    /* File uploader styling */
    .stFileUploader > div > div {
        background: linear-gradient(135deg, rgba(51, 65, 85, 0.6) 0%, rgba(30, 41, 59, 0.6) 100%);
        border: 2px dashed rgba(96, 165, 250, 0.4);
        border-radius: 16px;
        padding: 2.5rem;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    
    /* Audio player styling */
    audio {
        width: 100%;
        border-radius: 12px;
        margin: 1rem 0;
        filter: sepia(20%) saturate(70%) hue-rotate(200deg);
    }
    
    /* Radio button styling */
    .stRadio > div {
        background: rgba(51, 65, 85, 0.5);
        border-radius: 12px;
        padding: 1rem;
        backdrop-filter: blur(10px);
    }
    
    /* Text area styling */
    .stTextArea > div > div > textarea {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 12px;
        color: #e2e8f0;
    }
    
    /* Checkbox styling */
    .stCheckbox > label {
        color: #cbd5e1;
        font-weight: 500;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-container {
            margin: 1rem;
            padding: 2rem;
        }
        
        .header h1 {
            font-size: 2.5rem;
        }
        
        .card {
            padding: 2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Main container
st.markdown('<div class="main-container fade-in">', unsafe_allow_html=True)

# Beautiful header
st.markdown("""
<div class="header">
    <h1>Content Automation</h1>
    <p>Transform your videos into engaging clips with AI-generated music</p>
</div>
""", unsafe_allow_html=True)

# Demo mode toggle with beautiful styling
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    demo_mode = st.checkbox("Demo Mode (No API keys needed)", key="demo_toggle")
    if demo_mode:
        st.markdown('<div class="demo-badge">Demo Mode Active - Try it instantly!</div>', unsafe_allow_html=True)

# Input section with card styling
st.markdown('<div class="input-section">', unsafe_allow_html=True)
st.markdown("### Choose Your Input")

input_method = st.radio(
    "Select input method:",
    ["Upload Video", "Paste Transcript"], 
    horizontal=True,
    key="input_method"
)

uploaded_video = None
transcript_text = None

if input_method == "Upload Video":
    uploaded_video = st.file_uploader(
        "Drop your video file here or click to browse",
        type=['mp4', 'avi', 'mov', 'mkv'],
        help="Supported formats: MP4, AVI, MOV, MKV"
    )
    if uploaded_video:
        st.success(f"{uploaded_video.name} uploaded successfully!")
else:
    transcript_text = st.text_area(
        "Paste your transcript:",
        height=150,
        placeholder="Enter your transcript here...",
        help="Paste the text content you want to turn into clips"
    )

st.markdown('</div>', unsafe_allow_html=True)

# Generate button with beautiful styling
st.markdown('<div style="text-align: center; margin: 2rem 0;">', unsafe_allow_html=True)
generate_clicked = st.button("Generate Amazing Clips", type="primary", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Processing logic
if generate_clicked:
    if not demo_mode and input_method == "Upload Video" and not uploaded_video:
        st.error("Please upload a video file")
    elif not demo_mode and input_method == "Paste Transcript" and not transcript_text.strip():
        st.error("Please enter a transcript")
    else:
        # Save uploaded video if needed
        temp_video_path = None
        if uploaded_video and not demo_mode:
            temp_video_path = f"temp_{uploaded_video.name}"
            with open(temp_video_path, "wb") as f:
                f.write(uploaded_video.getbuffer())

        # Processing with beautiful progress indicators
        progress_container = st.container()
        
        with progress_container:
            with st.spinner("Creating your amazing clips..."):
                try:
                    if demo_mode:
                        # Demo mode - use pre-generated content
                        st.info("Demo Mode: Using pre-generated content")
                        transcript = get_demo_transcript()
                        analysis = get_demo_analysis(transcript)
                        final_clips = get_demo_music_for_clips(transcript, analysis["clips"])
                        if input_method == "Upload Video":
                            get_demo_video_clips(temp_video_path, {"clips": final_clips})
                    else:
                        # Real processing
                        if input_method == "Upload Video":
                            st.info("Generating transcript from video...")
                            transcript = generate_transcript(temp_video_path)
                        else:
                            transcript = {
                                "text": transcript_text,
                                "segments": [{"start": 0, "end": 30, "text": transcript_text}]
                            }
                        
                        st.info("Analyzing content with AI...")
                        analysis = analyze_transcript(transcript)
                        
                        st.info("Generating background music...")
                        final_clips = generate_music_for_clips(transcript=transcript, clips=analysis["clips"])
                        
                        if input_method == "Upload Video":
                            st.info("Extracting video clips...")
                            cut_clips(temp_video_path, {"clips": final_clips})

                    # Store results
                    st.session_state.clips = final_clips
                    st.session_state.has_video = input_method == "Upload Video"
                    st.session_state.demo_mode = demo_mode
                    st.session_state.processed = True

                    st.success("Clips generated successfully!")

                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Results section with beautiful styling
if st.session_state.get('processed', False):
    st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
    st.markdown("## Your Amazing Clips")
    
    clips = st.session_state.clips
    
    # Download section with beautiful styling
    st.markdown('<div class="download-section">', unsafe_allow_html=True)
    st.markdown("### Download Your Content")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Download All Files", use_container_width=True, key="download_all"):
            zip_path = create_zip_file(clips, st.session_state.get('has_video', False), st.session_state.get('demo_mode', False))
            if zip_path:
                with open(zip_path, "rb") as f:
                    st.download_button(
                        "Download ZIP Package",
                        data=f.read(),
                        file_name="clips_and_music.zip",
                        mime="application/zip",
                        use_container_width=True
                    )
    
    with col2:
        # Download JSON
        clips_json = json.dumps({"clips": clips}, indent=2)
        st.download_button(
            "Download Clip Data",
            data=clips_json,
            file_name="clips.json",
            mime="application/json",
            use_container_width=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Individual clips with beautiful cards
    st.markdown("### Individual Clips")
    
    for idx, clip in enumerate(clips, 1):
        st.markdown('<div class="clip-card">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"#### Clip {idx}")
            
            # Clip info with clean styling
            st.markdown(f"""
            <div style="margin: 1rem 0;">
                <p><strong>Duration:</strong> {clip['start']} → {clip['end']}</p>
                <p><strong>Hook:</strong> {clip['hook']}</p>
                <p><strong>Mood:</strong> {clip.get('music_mood', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Audio player with styling
            if "background_music" in clip and clip["background_music"].get("url"):
                audio_path = clip["background_music"]["url"]
                if os.path.exists(audio_path):
                    st.markdown("**Preview Audio:**")
                    st.audio(audio_path)
        
        with col2:
            st.markdown("#### Downloads")
            
            # Individual downloads with beautiful buttons
            if st.session_state.get('has_video', False):
                video_path = get_video_path(idx, st.session_state.get('demo_mode', False))
                if video_path and os.path.exists(video_path):
                    with open(video_path, "rb") as f:
                        st.download_button(
                            f"Video {idx}",
                            data=f.read(),
                            file_name=f"clip_{idx}.mp4",
                            mime="video/mp4",
                            key=f"video_{idx}",
                            use_container_width=True
                        )
            
            # Audio download
            if "background_music" in clip and clip["background_music"].get("url"):
                audio_path = clip["background_music"]["url"]
                if os.path.exists(audio_path):
                    with open(audio_path, "rb") as f:
                        st.download_button(
                            f"Audio {idx}",
                            data=f.read(),
                            file_name=f"music_{idx}.mp3",
                            mime="audio/mp3",
                            key=f"audio_{idx}",
                            use_container_width=True
                        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Close main container
st.markdown('</div>', unsafe_allow_html=True)

# Beautiful footer
st.markdown("""
<div style="text-align: center; margin-top: 3rem; padding: 2rem;">
    <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(51, 65, 85, 0.7) 100%); 
                backdrop-filter: blur(20px); 
                border-radius: 20px; 
                padding: 2rem; 
                border: 1px solid rgba(148, 163, 184, 0.2);">
        <h3 style="background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #f472b6 100%); 
                   -webkit-background-clip: text; 
                   -webkit-text-fill-color: transparent; 
                   margin-bottom: 1rem;">
            Transform Your Content with AI
        </h3>
        <p style="color: #94a3b8; font-size: 1.1rem; margin: 0;">
            Create engaging short-form clips with custom background music in minutes
        </p>
    </div>
</div>
""", unsafe_allow_html=True)
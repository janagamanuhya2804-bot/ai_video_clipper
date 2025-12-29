import streamlit as st
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from brain.gemini_analysis import analyze_transcript

st.set_page_config(page_title="Content Automation for Creators")
st.title("🎬 Content Automation for Creators")
st.write("Paste a transcript or test the AI-generated clips pipeline.")
# Simple transcript input
transcript_text = st.text_area(
    "Transcript",
    height=200,
    placeholder="Paste transcript text here..."
)

if st.button("Generate Clips"):
    if not transcript_text.strip():
        st.warning("Please enter a transcript.")
    else:
        # Minimal transcript structure
        transcript = {
            "segments": [
                {
                    "start": 0,
                    "end": 30,
                    "text": transcript_text
                }
            ]
        }

        with st.spinner("Analyzing with AI..."):
            result = analyze_transcript(transcript)

        st.success("Clips generated!")

        st.subheader("Generated Clips")
        st.json(result)

        # Save output for demo
        with open("clips.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        st.caption("Output saved to clips.json")
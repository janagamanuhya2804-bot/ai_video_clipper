import streamlit as st
import json
import sys
import os

# Allow imports from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from brain.gemini_analysis import analyze_transcript

st.set_page_config(page_title="Content Automation for Creators")

st.title("🎬 Content Automation for Creators")
st.write("Paste a transcript and let AI generate short-form clips.")

transcript_text = st.text_area(
    "Transcript",
    height=200,
    placeholder="Paste transcript text here..."
)

if st.button("Generate Clips"):
    if not transcript_text.strip():
        st.warning("Please enter a transcript.")
    else:
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

        clips = result.get("clips", [])

        if not clips:
            st.warning("No clips generated.")
        else:
            st.subheader("🎞️ Suggested Clips")

            for idx, clip in enumerate(clips, start=1):
                with st.container():
                    st.markdown(f"### Clip {idx}")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown(f"**⏱ Start:** `{clip['start']}`")
                        st.markdown(f"**⏹ End:** `{clip['end']}`")

                    with col2:
                        st.markdown(f"**🎯 Hook:** {clip['hook']}")
                        st.markdown(
                            f"<span style='background-color:#e0f2fe; padding:6px; border-radius:6px;'>🎵 {clip.get('music_mood','')}</span>",
                            unsafe_allow_html=True
                        )

                    st.divider()

        # Save output for demo
        with open("clips.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        st.caption("Output saved to clips.json")


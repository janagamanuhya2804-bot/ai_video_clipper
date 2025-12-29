# 🎬 AI Video Clipper — Content Automation for Creators

## 🚀 Problem
Content creators spend hours manually finding highlights, cutting videos, and choosing music for short-form platforms like Instagram Reels, YouTube Shorts, and TikTok.

This process is repetitive, time-consuming, and not scalable.

---

## 💡 Solution
AI Video Clipper automates the entire workflow:

**Long Video / Transcript → AI Analysis → Auto-Generated Clips**

Using Google Gemini and automation logic, creators get ready-to-post clip suggestions in seconds.

---

## 🧠 How It Works
1. User provides a transcript (or video → transcript)
2. **Gemini AI** analyzes the content to:
   - Identify engaging moments
   - Generate clip timestamps
   - Suggest music mood
3. The system outputs structured clip data
4. (Optional) FFmpeg can auto-cut the clips

The system includes **graceful fallback mode** to ensure demos never fail due to API rate limits.

---

## 🖥️ Tech Stack
- **Python**
- **Streamlit** — UI
- **Google Gemini API** — AI analysis
- **FFmpeg** — video clipping (local / cloud)
- **GitHub** — version control

---

## ▶️ How to Run Locally

```bash
# create virtual environment
python -m venv .venv
source .venv/Scripts/activate  # Windows

# install dependencies
python -m pip install -r requirements.txt

# set API key (or use .env)
set GEMINI_API_KEY=YOUR_KEY

# run the app
streamlit run ui/app.py

import os
import sys
from dotenv import load_dotenv

# Load environment variables
try:
    load_dotenv()  # looks for .env at project root
except Exception:
    pass  # if python-dotenv not installed, env must be exported in shell

# Add project root to Python path
ROOT = os.path.dirname(os.path.abspath(__file__))          # .../Buildathon/ai_core
ROOT = os.path.dirname(ROOT)                               # .../Buildathon (project root)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Import required modules
from input_preprocessing.router import preprocess_request
from ai_core.multimodel_inference_gateway import multimodal_infer_gemini
from ai_core.weather_reports import get_weather_by_coords
from ai_core.incident_judge import judge_incident_with_gemini
import streamlit as st

if os.getenv("GROQ_API_KEY"):
    print("GROQ_API_KEY detected")
else:
    print("GROQ_API_KEY not found. Put it in .env at project root or export in shell.")


st.set_page_config(page_title="Disaster Intake → Multimodal Agent", layout="centered")
st.title("Step 1–2: Intake Preprocessing + Multimodal Inference")

channel = st.selectbox("Channel", ["app", "whatsapp", "sms"], index=0)
text = st.text_area("Message text (SMS/WhatsApp/App)", height=120, placeholder="Describe the situation, people affected, landmarks, etc.")
latlon = st.text_input("Location (optional lat,lon)", placeholder="12.9716,77.5946")

uploaded_files = st.file_uploader(
    "Upload media (images/audio/video). Multiple files supported.",
    type=["jpg","jpeg","png","webp","mp3","wav","m4a","aac","mp4","mov","mkv"],
    accept_multiple_files=True
)

if st.button("Process"):
    uploads = []
    for f in uploaded_files or []:
        uploads.append((f.name, f.getvalue(), f.type or ""))
    print(f"--- Inputs: channel={channel}, text_len={len(text)}, latlon={latlon}, uploads_count={len(uploads)} ---")
    incident = preprocess_request(channel, text, latlon, uploads)
    print("--- Incident after preprocessing ---")
    st.subheader("Normalized Incident")
    st.json(incident.model_dump())

    # Optional: show first image preview to confirm correct upload
    if uploaded_files:
        for f in uploaded_files:
            if (f.type or "").startswith("image/"):
                st.image(f)
                break 
    st.subheader("Multimodal Agent Inference (What happened?)")
    # result = multimodal_infer_openai(incident)
    incident_request = multimodal_infer_gemini(incident)
    # after: result = multimodal_infer_gemini(incident)
    lat,lan=3.0878,80.2785
    realworld_context = get_weather_by_coords(lat,lan)
    
    judge = judge_incident_with_gemini(incident_request, realworld_context)
    if not judge.get("real_incident", False):
        priority = 0
    else:
        sev = (judge.get("final_severity") or incident_request.get("severity","Unknown")).lower()
        base = 10 if sev == "critical" else 8 if sev == "high" else 5 if sev in ["moderate","medium"] else 3
        bonus = 2 if judge.get("verdict_score_0_10",0) >= 8 else 1 if judge.get("verdict_score_0_10",0) >= 5 else 0
        priority = min(10, base + bonus)

    st.json({"judge": judge, "priority_score_0_10": priority})
    print("all the process completed successfully",judge)

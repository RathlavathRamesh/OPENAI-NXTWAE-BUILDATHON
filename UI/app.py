import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))          # .../Buildathon/UI
ROOT = os.path.dirname(ROOT)                               # .../Buildathon (project root)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
    
from ai_core.multimodal_inference_gateway import multimodal_infer_openai

import streamlit as st
from input_preprocessing.router import preprocess_request


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
    result = multimodal_infer_openai(incident)
    print("--- Multimodal Inference Result ---")
    print(result)
    st.json(result)

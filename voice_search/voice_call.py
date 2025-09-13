import os, base64, requests
from flask import Flask, request, Response, jsonify
from twilio.twiml.voice_response import VoiceResponse, Dial
from dotenv import load_dotenv

# Load env (TWILIO vars optional for this prototype)
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_ASR_MODEL = os.getenv("GROQ_ASR_MODEL", "whisper-large-v3-turbo")
GROQ_TRANSCRIBE_URL = "https://api.groq.com/openai/v1/audio/transcriptions"  # OpenAI‑compatible [7]

PERSONAL_MOBILE_E164 = os.getenv("PERSONAL_MOBILE_E164")  # e.g., +91XXXXXXXXXX

from input_preprocessing.router import preprocess_request
from ai_core.groq_multimodal_inference_gateway import multimodal_infer_groq

app = Flask(__name__)

@app.route("/voice", methods=["POST"])
def voice_inbound():
    # TwiML: brief disclosure + forward to personal phone with recording enabled
    vr = VoiceResponse()
    vr.say("This call may be recorded for safety and quality.", voice="alice")
    dial = Dial(
        PERSONAL_MOBILE_E164,
        record="record-from-answer-dual",  # record both legs once answered [4]
        recording_status_callback="/recording_done",  # webhook when recording ready [1]
        recording_status_callback_event="completed",  # trigger on completion [1]
    )
    vr.append(dial)
    return Response(str(vr), mimetype="text/xml")

@app.route("/recording_done", methods=["POST"])
def recording_done():
    # Twilio sends RecordingUrl and call metadata here [1][5]
    recording_url = request.form.get("RecordingUrl", "")
    call_sid = request.form.get("CallSid", "")
    from_number = request.form.get("From", "")
    duration = request.form.get("RecordingDuration", "")
    # Download the media (commonly mp3 or wav). Append extension to get a media file. [5]
    media_url = recording_url + ".mp3"
    audio_resp = requests.get(media_url, timeout=120)
    audio_resp.raise_for_status()
    audio_bytes = audio_resp.content
    mime = "audio/mpeg"

    # Transcribe with Groq Whisper (hosted; no local model) [7]
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    files = {"file": ("call.mp3", audio_bytes, mime)}
    data = {"model": GROQ_ASR_MODEL}
    asr = requests.post(GROQ_TRANSCRIBE_URL, headers=headers, data=data, files=files, timeout=240)
    asr.raise_for_status()
    transcript_text = asr.json().get("text", "")

    # Optional: capture caller location; for prototype leave blank or parse a lat,lon from IVR flow later
    latlon = request.form.get("CallerLatLong", "")

    # Build uploads tuple like the UI path expects
    uploads = [("call.mp3", audio_bytes, mime)]
    incident = preprocess_request(channel="voice", text=transcript_text, latlon=latlon, uploads=uploads)

    # Run multimodal inference (text only unless MMS/images were provided)
    result = multimodal_infer_groq(incident)

    # Return JSON for logging; Twilio only needs 200 OK
    return jsonify({
        "ok": True,
        "call_sid": call_sid,
        "from": from_number,
        "duration_sec": duration,
        "incident": incident.model_dump(),
        "inference": result
    })

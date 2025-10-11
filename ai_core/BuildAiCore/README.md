# Disaster Response AI System (Gemini Only)

A clean 3-layer AI system for processing disaster reports using only Gemini APIs.

## 📁 Clean File Structure

```
BuildAiCore/
├── config.py                          # Your API key goes here
├── start_server.py                    # Start the server
├── app.py                            # Main FastAPI application
├── preprocess_agent.py               # Layer 1: Preprocess Agent
├── analysis_agent.py                 # Layer 2: Analysis Agent
├── judge_agent.py                    # Layer 3: Judge Agent
├── agent1_multimodal_processor_gemini.py  # Gemini-only processor
├── schemas.py                        # Pydantic models
├── requirements.txt                  # Dependencies
├── test_api.py                       # Full test script
├── quick_test.py                     # Quick test (runs once)
├── simple_test.json                  # Sample request (text)
├── video_test.json                   # Sample request (video)
└── README.md                         # This file
```

## 🚀 Quick Start

### 1. Add Your API Key
Edit `config.py`:
```python
GEMINI_API_KEY = "your_actual_gemini_api_key_here"
```

### 2. Start the Server
```bash
python start_server.py
```

### 3. Test the API
```bash
python quick_test.py
```

## 🧪 Testing

- **Quick test**: `python quick_test.py` (runs once and exits)
- **Full test**: `python test_api.py` (detailed output)
- **Postman**: Use `simple_test.json` or `video_test.json`

## 📊 API Endpoint

- **URL**: `POST http://localhost:8000/take_request`
- **Documentation**: `http://localhost:8000/docs`

## 🎯 Sample Request

```json
{
  "channel": "app",
  "text": "URGENT: There's a severe flood in our area! Water is rising rapidly and my family of 4 is trapped on the second floor. The main road is completely submerged and cars are floating. Please send help immediately!",
  "location": {
    "lat": 12.9716,
    "lon": 77.5946
  },
  "media_items": [],
  "incident_id": "flood_001"
}
```

## ✅ Features

- ✅ **Text Analysis**: Process SMS, WhatsApp, App messages
- ✅ **Image Analysis**: Analyze disaster scene images
- ✅ **Video Analysis**: Extract frames and analyze video content
- ✅ **Audio Analysis**: Transcribe and analyze audio reports
- ✅ **Real-world Data**: Fetch weather and geospatial data
- ✅ **3-Layer Processing**: Preprocess → Analysis → Judge
- ✅ **Gemini Only**: Uses only your Gemini API key
- ✅ **JSON API**: Easy integration with other systems

## 🎉 That's it!

Clean, simple, and ready to use! 🚀

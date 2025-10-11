#!/usr/bin/env python3
"""
Test script for file upload endpoint
"""

import requests
import os

def test_upload_endpoint():
    """Test the upload_request endpoint with form-data"""
    print("🧪 Testing file upload endpoint...")
    
    url = "http://localhost:8000/upload_request"
    
    # Test data
    data = {
        "channel": "whatsapp",
        "text": "Emergency! Building collapse in downtown area. Multiple people trapped. Sending video evidence.",
        "lat": 12.9716,
        "lon": 77.5946,
        "incident_id": "collapse_001"
    }
    
    # Test with a sample file (if exists)
    files = {}
    test_file = "test_video.mp4"
    if os.path.exists(test_file):
        files["files"] = (test_file, open(test_file, "rb"), "video/mp4")
        print(f"📁 Using test file: {test_file}")
    else:
        print("ℹ️  No test file found, testing without files")
    
    try:
        response = requests.post(url, data=data, files=files)
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"🎯 Priority: {result['final_results']['priority_score']}/10")
            print(f"🔍 Authentic: {result['final_results']['authentic']}")
            print(f"⚠️  Severity: {result['final_results']['severity']}")
            print(f"📝 Summary: {result['final_results']['summary'][:100]}...")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    finally:
        if files:
            files["files"][1].close()

if __name__ == "__main__":
    test_upload_endpoint()

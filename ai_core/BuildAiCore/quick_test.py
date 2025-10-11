#!/usr/bin/env python3
"""
Quick test script - runs once and exits
"""

import requests
import json

def quick_test():
    """Quick test of the API"""
    
    print("⚡ Quick API Test")
    print("=" * 30)
    
    # Simple test data
    test_data = {
        "channel": "app",
        "text": "URGENT: Flood emergency! Family trapped!",
        "location": {"lat": 12.9716, "lon": 77.5946},
        "media_items": [],
        "incident_id": "quick_test_001"
    }
    
    try:
        print("🔄 Sending request...")
        response = requests.post(
            "http://localhost:8000/take_request",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            final = result.get('final_results', {})
            
            print("✅ Success!")
            print(f"🎯 Priority: {final.get('priority_score_0_10', 0)}/10")
            print(f"🔍 Authentic: {final.get('incident_authentic', False)}")
            print(f"⚠️  Severity: {final.get('final_severity', 'Unknown')}")
            
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start it with: python start_server.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    quick_test()

#!/usr/bin/env python3
"""
Test the Disaster Response API
"""

import requests
import json
import time

def test_api():
    """Test the API with a sample request"""
    
    print("🧪 Testing Disaster Response API")
    print("=" * 40)
    
    # Test data
    test_data = {
        "channel": "app",
        "text": "URGENT: There's a severe flood in our area! Water is rising rapidly and my family of 4 is trapped on the second floor. The main road is completely submerged and cars are floating. Please send help immediately!",
        "location": {
            "lat": 12.9716,
            "lon": 77.5946
        },
        "media_items": [],
        "incident_id": "test_flood_001",
        "metadata": {
            "source": "mobile_app",
            "user_id": "user_12345",
            "priority": "high"
        }
    }
    
    try:
        print(f"📝 Text: {test_data['text'][:50]}...")
        print(f"📍 Location: {test_data['location']}")
        print(f"📎 Media items: {len(test_data['media_items'])}")
        print("\n🔄 Sending request...")
        
        # Make request
        start_time = time.time()
        response = requests.post(
            "http://localhost:8000/take_request",
            json=test_data,
            timeout=30
        )
        end_time = time.time()
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"⏱️  Response Time: {end_time - start_time:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Request successful!")
            print(f"🆔 Request ID: {result.get('request_id')}")
            print(f"📊 Status: {result.get('status')}")
            print(f"⏱️  Processing Time: {result.get('processing_time_ms')}ms")
            
            # Show final results
            final_results = result.get('final_results', {})
            print(f"\n🎯 Final Results:")
            print(f"   Priority: {final_results.get('priority_score_0_10', 0)}/10")
            print(f"   Authentic: {final_results.get('incident_authentic', False)}")
            print(f"   Severity: {final_results.get('final_severity', 'Unknown')}")
            
            if final_results.get('recommendations'):
                print(f"   Recommendations:")
                for i, rec in enumerate(final_results['recommendations'][:3], 1):
                    print(f"     {i}. {rec}")
            
            # Show layer 1 analysis
            layer1 = result.get('layer1_preprocess', {})
            situation = layer1.get('situation_analysis', {})
            print(f"\n🔍 Layer 1 Analysis:")
            print(f"   Situation: {situation.get('situation_summary', 'No summary')[:100]}...")
            print(f"   Hazards: {len(situation.get('hazards', []))} detected")
            print(f"   Severity: {situation.get('severity', 'Unknown')}")
            
            return True
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the server is running:")
        print("   python start_server.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_api()
    if success:
        print("\n🎉 API test successful!")
    else:
        print("\n❌ API test failed!")

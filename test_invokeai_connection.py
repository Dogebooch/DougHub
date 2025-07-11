#!/usr/bin/env python3
"""
Test script to verify InvokeAI connection and API endpoints
"""

import requests
import json

def test_invokeai_connection():
    """Test basic connection to InvokeAI server"""
    try:
        # Test basic connectivity - try different endpoints
        endpoints = [
            "http://127.0.0.1:9090/api/v1/models",
            "http://127.0.0.1:9090/api/v1/model",
            "http://127.0.0.1:9090/api/models",
            "http://127.0.0.1:9090/api/v1/",
            "http://127.0.0.1:9090/"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint)
                print(f"Testing {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    print(f"✅ Working endpoint: {endpoint}")
                    try:
                        data = response.json()
                        print(f"Response: {json.dumps(data, indent=2)[:200]}...")
                    except:
                        print(f"Response: {response.text[:200]}...")
                    break
            except requests.exceptions.ConnectionError:
                print(f"❌ Cannot connect to {endpoint}")
                continue
                
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False
    
    return True

def test_image2image_endpoint():
    """Test the image2image endpoint with different variations"""
    endpoints = [
        "http://127.0.0.1:9090/api/v1/generate/image2image",
        "http://127.0.0.1:9090/api/v1/generate",
        "http://127.0.0.1:9090/api/generate",
        "http://127.0.0.1:9090/api/v1/inpaint"
    ]
    
    test_payload = {
        "prompt": "test",
        "init_image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",  # 1x1 transparent PNG
        "denoising_strength": 0.75,
        "model": "Dreamshaper 8",
        "image_mode": "IMAGE2IMAGE",
        "scheduler": "DPM++_2M_Karras",
        "cfg_scale": 6.5,
        "steps": 28,
        "width": 512,
        "height": 512
    }
    
    for endpoint in endpoints:
        try:
            print(f"\nTesting {endpoint}...")
            response = requests.post(endpoint, json=test_payload)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Image2Image endpoint is working!")
                return endpoint
            else:
                print(f"Error: {response.text[:200]}...")
        except Exception as e:
            print(f"❌ Error testing {endpoint}: {e}")
    
    return None

if __name__ == "__main__":
    print("Testing InvokeAI connection...")
    if test_invokeai_connection():
        print("\n✅ Connection successful!")
        working_endpoint = test_image2image_endpoint()
        if working_endpoint:
            print(f"✅ Working endpoint: {working_endpoint}")
        else:
            print("❌ No working image2image endpoint found")
    else:
        print("❌ Connection failed!") 
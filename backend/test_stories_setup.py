#!/usr/bin/env python3
"""
Simple test script to verify stories functionality
"""

import requests
import json
import sys
import os

# Configuration
BASE_URL = "http://localhost:8000"

def test_database_connection():
    """Test if the API is running"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ API is running")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the backend is running.")
        return False
    except Exception as e:
        print(f"��� Error connecting to API: {e}")
        return False

def test_stories_endpoint():
    """Test if stories endpoint exists"""
    try:
        # This should return 401 (unauthorized) since we don't have a token
        # But it proves the endpoint exists
        response = requests.get(f"{BASE_URL}/stories/")
        if response.status_code == 401:
            print("✅ Stories endpoint exists (needs authentication)")
            return True
        elif response.status_code == 200:
            print("✅ Stories endpoint exists and accessible")
            return True
        else:
            print(f"⚠️ Stories endpoint returned unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing stories endpoint: {e}")
        return False

def test_upload_endpoint():
    """Test if upload endpoint exists"""
    try:
        # This should return 401 (unauthorized) or 422 (missing file)
        response = requests.post(f"{BASE_URL}/upload/media")
        if response.status_code in [401, 422]:
            print("✅ Upload endpoint exists")
            return True
        else:
            print(f"⚠️ Upload endpoint returned unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing upload endpoint: {e}")
        return False

def main():
    print("🔬 TESTING STORIES SETUP")
    print("=" * 40)
    
    # Test API connection
    if not test_database_connection():
        print("\n❌ Cannot proceed with tests - API is not accessible")
        return False
    
    # Test stories endpoint
    if not test_stories_endpoint():
        print("\n❌ Stories endpoint is not working properly")
        return False
    
    # Test upload endpoint
    if not test_upload_endpoint():
        print("\n❌ Upload endpoint is not working properly")
        return False
    
    print("\n" + "=" * 40)
    print("✅ ALL TESTS PASSED!")
    print("✅ Stories functionality should be working")
    print("\n📋 Next steps:")
    print("1. Try creating a story from the frontend")
    print("2. Check browser console for any errors")
    print("3. If there are still issues, check backend logs")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

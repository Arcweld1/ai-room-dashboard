#!/usr/bin/env python3
"""
Test suite for AI Room Dashboard improvements
Tests the new features and enhancements added to the application.
"""

import os
import sys
import requests
import json
import tempfile
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:5000"
TEST_FILE_CONTENT = """Test file for AI Room Dashboard
This is a test file to verify file upload and processing functionality.
The application should be able to read this content and integrate it with AI conversations.
"""

def test_health_endpoint():
    """Test the enhanced health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "apis" in data
        assert "version" in data
        
        print("✅ Health endpoint test passed")
        return True
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

def test_api_status_endpoint():
    """Test the new API status endpoint"""
    print("Testing API status endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "apis" in data
        assert "timestamp" in data
        assert "openai" in data["apis"]
        assert "gemini" in data["apis"]
        
        print("✅ API status endpoint test passed")
        return True
    except Exception as e:
        print(f"❌ API status endpoint test failed: {e}")
        return False

def test_file_upload():
    """Test the enhanced file upload functionality"""
    print("Testing file upload...")
    try:
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(TEST_FILE_CONTENT)
            temp_file_path = f.name
        
        # Test file upload
        with open(temp_file_path, 'rb') as f:
            files = {'file': ('test.txt', f, 'text/plain')}
            response = requests.post(f"{BASE_URL}/upload", files=files)
        
        # Clean up
        os.unlink(temp_file_path)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "filename" in data
        assert "content_preview" in data
        
        print("✅ File upload test passed")
        return True
    except Exception as e:
        print(f"❌ File upload test failed: {e}")
        return False

def test_chat_error_handling():
    """Test improved chat error handling"""
    print("Testing chat error handling...")
    try:
        # Test chat without API keys (should fail gracefully)
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"message": "Hello", "ai_provider": "openai"},
            headers={"Content-Type": "application/json"}
        )
        
        # Should return an error but not crash
        assert response.status_code in [400, 500]
        data = response.json()
        assert "error" in data
        
        print("✅ Chat error handling test passed")
        return True
    except Exception as e:
        print(f"❌ Chat error handling test failed: {e}")
        return False

def test_main_page():
    """Test that the main page loads correctly"""
    print("Testing main page...")
    try:
        response = requests.get(BASE_URL)
        assert response.status_code == 200
        assert "AI Room Dashboard" in response.text
        
        print("✅ Main page test passed")
        return True
    except Exception as e:
        print(f"❌ Main page test failed: {e}")
        return False

def test_history_page():
    """Test that the history page loads correctly"""
    print("Testing history page...")
    try:
        response = requests.get(f"{BASE_URL}/history")
        assert response.status_code == 200
        assert "Conversation History" in response.text
        
        print("✅ History page test passed")
        return True
    except Exception as e:
        print(f"❌ History page test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and return results"""
    print("=" * 50)
    print("AI Room Dashboard - Improvement Tests")
    print("=" * 50)
    
    tests = [
        test_main_page,
        test_history_page,
        test_health_endpoint,
        test_api_status_endpoint,
        test_file_upload,
        test_chat_error_handling
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()
    
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    print("=" * 50)
    
    if passed == total:
        print("🎉 All tests passed! The improvements are working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the logs above.")
    
    return passed == total

if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get(BASE_URL, timeout=5)
    except requests.exceptions.RequestException:
        print(f"❌ Cannot connect to {BASE_URL}")
        print("Please make sure the application is running with: python main.py")
        sys.exit(1)
    
    success = run_all_tests()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Automated test script to verify complete stories functionality
"""

import os
import sys
import requests
import json
from sqlalchemy import create_engine, text

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_api_connection():
    """Test if API is running"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_database_structure():
    """Test database structure"""
    try:
        from core.database import engine
        
        with engine.connect() as conn:
            # Test background_color column
            result = conn.execute(text("""
                SELECT CHARACTER_MAXIMUM_LENGTH 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'stories' 
                AND COLUMN_NAME = 'background_color'
            """)).fetchone()
            
            if not result or result[0] < 255:
                return False, "background_color column too small"
            
            # Test media_url column
            result = conn.execute(text("""
                SELECT CHARACTER_MAXIMUM_LENGTH 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'stories' 
                AND COLUMN_NAME = 'media_url'
            """)).fetchone()
            
            if not result or result[0] < 500:
                return False, "media_url column too small"
            
            return True, "Database structure OK"
            
    except Exception as e:
        return False, f"Database error: {e}"

def test_stories_endpoint():
    """Test stories endpoint"""
    try:
        response = requests.get("http://localhost:8000/stories/", timeout=5)
        # Should return 401 (unauthorized) since we don't have token
        return response.status_code == 401
    except:
        return False

def test_upload_endpoint():
    """Test upload endpoint"""
    try:
        response = requests.post("http://localhost:8000/upload/media", timeout=5)
        # Should return 401 or 422 (missing file)
        return response.status_code in [401, 422]
    except:
        return False

def test_gradient_storage():
    """Test gradient storage in database"""
    try:
        from core.database import engine
        
        test_gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        
        with engine.connect() as conn:
            # Try to insert test gradient
            conn.execute(text("""
                INSERT INTO stories (author_id, content, background_color, duration_hours, expires_at, created_at, views_count)
                VALUES (1, 'GRADIENT_TEST_AUTO', :gradient, 24, NOW() + INTERVAL 24 HOUR, NOW(), 0)
            """), {"gradient": test_gradient})
            
            # Verify it was stored correctly
            result = conn.execute(text("""
                SELECT background_color FROM stories 
                WHERE content = 'GRADIENT_TEST_AUTO'
                LIMIT 1
            """)).fetchone()
            
            success = result and result[0] == test_gradient
            
            # Clean up
            conn.execute(text("DELETE FROM stories WHERE content = 'GRADIENT_TEST_AUTO'"))
            conn.commit()
            
            return success
            
    except Exception as e:
        print(f"Gradient test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 AUTOMATED STORIES TESTING")
    print("=" * 50)
    
    tests = [
        ("API Connection", test_api_connection),
        ("Database Structure", lambda: test_database_structure()[0]),
        ("Stories Endpoint", test_stories_endpoint),
        ("Upload Endpoint", test_upload_endpoint),
        ("Gradient Storage", test_gradient_storage),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
            results.append(result)
        except Exception as e:
            print(f"❌ FAIL {test_name} - {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    
    if all(results):
        print("🎉 ALL TESTS PASSED!")
        print("✅ Stories functionality is fully working")
        print("\n📋 What's working:")
        print("- ✅ Backend API running")
        print("- ✅ Database structure correct")
        print("- ✅ Stories endpoints available")
        print("- ✅ Upload endpoints available")
        print("- ✅ CSS gradients can be stored")
        print("\n🚀 You're ready to create stories!")
        return True
    else:
        failed_count = sum(1 for r in results if not r)
        print(f"❌ {failed_count}/{len(tests)} TESTS FAILED")
        print("\n🔧 Run this to fix issues:")
        print("python run_stories_fix.py")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

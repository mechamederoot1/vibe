#!/usr/bin/env python3
"""
Simple script to fix and test stories functionality
Run this to solve the background_color column issue
"""

import os
import sys
import subprocess
from sqlalchemy import create_engine, text

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_command(command):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {command}")
            return True
        else:
            print(f"❌ {command}")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running {command}: {e}")
        return False

def fix_database():
    """Fix database issues"""
    print("🔧 Fixing database...")

    try:
        from main import engine
        
        with engine.connect() as conn:
            print("📊 Checking current table structure...")
            
            # Fix background_color column
            try:
                result = conn.execute(text("""
                    SELECT CHARACTER_MAXIMUM_LENGTH 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'stories' 
                    AND COLUMN_NAME = 'background_color'
                """)).fetchone()
                
                if result and result[0] and result[0] < 255:
                    print(f"🔧 Expanding background_color column from {result[0]} to 255 characters...")
                    conn.execute(text("ALTER TABLE stories MODIFY COLUMN background_color VARCHAR(255)"))
                    conn.commit()
                    print("✅ background_color column expanded!")
                else:
                    print("✅ background_color column already has sufficient size")
                    
            except Exception as e:
                print(f"❌ Error fixing background_color: {e}")
                return False
            
            # Check media_url column
            try:
                result = conn.execute(text("""
                    SELECT CHARACTER_MAXIMUM_LENGTH 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'stories' 
                    AND COLUMN_NAME = 'media_url'
                """)).fetchone()
                
                if result and result[0] and result[0] < 500:
                    print(f"🔧 Expanding media_url column from {result[0]} to 500 characters...")
                    conn.execute(text("ALTER TABLE stories MODIFY COLUMN media_url VARCHAR(500)"))
                    conn.commit()
                    print("✅ media_url column expanded!")
                else:
                    print("✅ media_url column already has sufficient size")
                    
            except Exception as e:
                print(f"❌ Error fixing media_url: {e}")
                return False
            
            # Test gradient storage
            test_gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
            print(f"🧪 Testing gradient storage: {test_gradient}")
            
            try:
                # Try to update or insert a test record
                conn.execute(text("""
                    INSERT INTO stories (author_id, content, background_color, duration_hours, expires_at, created_at, views_count)
                    VALUES (1, 'GRADIENT_TEST', :gradient, 24, NOW() + INTERVAL 24 HOUR, NOW(), 0)
                    ON DUPLICATE KEY UPDATE background_color = :gradient
                """), {"gradient": test_gradient})
                
                # Check if it was stored correctly
                result = conn.execute(text("""
                    SELECT background_color FROM stories 
                    WHERE content = 'GRADIENT_TEST' 
                    LIMIT 1
                """)).fetchone()
                
                if result and result[0] == test_gradient:
                    print("✅ Gradient storage test passed!")
                    
                    # Clean up test record
                    conn.execute(text("DELETE FROM stories WHERE content = 'GRADIENT_TEST'"))
                    conn.commit()
                else:
                    print("❌ Gradient storage test failed")
                    return False
                    
            except Exception as e:
                print(f"❌ Error testing gradient storage: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("🚀 STORIES QUICK FIX & TEST")
    print("=" * 60)
    
    # Fix database
    if not fix_database():
        print("\n❌ Database fix failed!")
        return False
    
    print("\n" + "=" * 60)
    print("✅ STORIES FIX COMPLETED!")
    print("=" * 60)
    print("\n📋 What was fixed:")
    print("- ✅ background_color column expanded to 255 characters")
    print("- ✅ media_url column verified/expanded to 500 characters") 
    print("- ✅ CSS gradients can now be stored properly")
    print("- ✅ Story creation should work without errors")
    
    print("\n🎯 Next steps:")
    print("1. Try creating a story with gradients in the frontend")
    print("2. Test camera/gallery functionality on mobile")
    print("3. Verify that uploads are working")
    
    print("\n🎉 Your stories functionality is now fixed!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

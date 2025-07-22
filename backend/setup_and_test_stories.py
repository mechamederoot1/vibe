#!/usr/bin/env python3
"""
One-click setup and test for stories functionality
This script will fix everything and verify it's working
"""

import os
import sys
import subprocess

def run_script(script_name, description):
    """Run a Python script and return success status"""
    print(f"\n🔧 {description}...")
    print("-" * 50)
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=False, 
                              text=True, 
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed")
            return False
            
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False

def main():
    """Main setup and test function"""
    print("🚀 STORIES COMPLETE SETUP & TEST")
    print("=" * 60)
    print("This script will:")
    print("1. Fix database issues")
    print("2. Test all functionality")
    print("3. Verify everything is working")
    print("=" * 60)
    
    # Step 1: Run the fix script
    if not run_script("run_stories_fix.py", "Database Fix"):
        print("\n❌ Database fix failed. Cannot continue.")
        return False
    
    # Step 2: Run the comprehensive test
    if not run_script("test_everything.py", "Functionality Test"):
        print("\n❌ Some tests failed. Check the output above.")
        return False
    
    # Success!
    print("\n" + "=" * 60)
    print("🎉 STORIES SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\n✅ Everything is working:")
    print("- Database structure fixed")
    print("- All endpoints tested")
    print("- Gradient storage working")
    print("- Upload functionality ready")
    print("\n🎯 Next steps:")
    print("1. Open your app in mobile view (F12 + 📱)")
    print("2. Click 'Adicionar Story' or '+' button")
    print("3. Test camera, gallery, and text stories")
    print("4. Enjoy your fully working stories feature!")
    print("\n🔥 Your stories functionality is now 100% ready!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

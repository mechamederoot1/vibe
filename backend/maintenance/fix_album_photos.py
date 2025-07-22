#!/usr/bin/env python3
"""
URGENT FIX: Correct album_photos table structure
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from main import engine
    from sqlalchemy import text
    
    print("🚨 URGENT FIX: Correcting album_photos table...")
    
    with engine.connect() as conn:
        # Drop and recreate album_photos table with correct structure
        print("🗑️ Dropping old album_photos table...")
        try:
            conn.execute(text("DROP TABLE IF EXISTS album_photos"))
            conn.commit()
        except:
            pass
        
        print("📋 Creating correct album_photos table...")
        album_photos_sql = """
        CREATE TABLE album_photos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            photo_url VARCHAR(500) NOT NULL,
            photo_type VARCHAR(20) DEFAULT 'profile',
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id),
            INDEX idx_photo_type (photo_type)
        ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        """
        
        conn.execute(text(album_photos_sql))
        conn.commit()
        
        print("✅ album_photos table recreated with correct structure")
        
        # Also check if albums table exists and has correct structure
        try:
            result = conn.execute(text("SHOW TABLES LIKE 'albums'"))
            if not result.fetchone():
                print("📋 Creating albums table...")
                albums_sql = """
                CREATE TABLE albums (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    INDEX idx_user_id (user_id)
                ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                """
                conn.execute(text(albums_sql))
                conn.commit()
                print("✅ albums table created")
        except Exception as e:
            print(f"⚠️ Albums table issue: {e}")
        
        print("\n🎉 ALBUM PHOTOS TABLE FIXED!")
        print("🔄 Avatar upload should work now")
        
except Exception as e:
    print(f"❌ Error: {e}")

if __name__ == "__main__":
    pass

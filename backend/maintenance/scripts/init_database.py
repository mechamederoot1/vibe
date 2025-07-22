#!/usr/bin/env python3
"""
Complete database initialization script
Creates all tables with proper structure for the Vibe social network
"""
import os
import sys
from urllib.parse import quote_plus

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.exc import OperationalError
    import pymysql
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    def get_database_url():
        """Get database URL from environment or defaults"""
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            return database_url

        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "3306")
        db_user = os.getenv("DB_USER", "root")
        db_password = os.getenv("DB_PASSWORD", "Evo@000#!")
        db_name = os.getenv("DB_NAME", "vibe")

        encoded_password = quote_plus(db_password)
        return f"mysql+pymysql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"

    def create_database_if_not_exists():
        """Create database if it doesn't exist"""
        print("🔍 Checking if database exists...")
        
        # Connect without database name first
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = int(os.getenv("DB_PORT", "3306"))
        db_user = os.getenv("DB_USER", "root")
        db_password = os.getenv("DB_PASSWORD", "Evo@000#!")
        db_name = os.getenv("DB_NAME", "vibe")
        
        connection = pymysql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE {db_name}")
        connection.commit()
        connection.close()
        
        print(f"✅ Database '{db_name}' ready")

    def init_database():
        """Initialize all database tables"""
        print("🚀 VIBE DATABASE INITIALIZATION")
        print("=" * 50)
        
        # Ensure database exists
        create_database_if_not_exists()
        
        # Connect to database
        database_url = get_database_url()
        engine = create_engine(database_url, pool_pre_ping=True)
        
        print("📋 Creating tables...")
        
        with engine.connect() as conn:
            # Drop all tables if they exist (fresh start)
            drop_tables_sql = """
            SET FOREIGN_KEY_CHECKS = 0;
            DROP TABLE IF EXISTS album_photos;
            DROP TABLE IF EXISTS albums;
            DROP TABLE IF EXISTS follows;
            DROP TABLE IF EXISTS blocks;
            DROP TABLE IF EXISTS media_files;
            DROP TABLE IF EXISTS messages;
            DROP TABLE IF EXISTS shares;
            DROP TABLE IF EXISTS comments;
            DROP TABLE IF EXISTS reactions;
            DROP TABLE IF EXISTS friendships;
            DROP TABLE IF EXISTS notifications;
            DROP TABLE IF EXISTS story_overlays;
            DROP TABLE IF EXISTS story_tags;
            DROP TABLE IF EXISTS story_views;
            DROP TABLE IF EXISTS stories;
            DROP TABLE IF EXISTS posts;
            DROP TABLE IF EXISTS users;
            SET FOREIGN_KEY_CHECKS = 1;
            """
            
            for sql in drop_tables_sql.split(';'):
                if sql.strip():
                    try:
                        conn.execute(text(sql))
                    except:
                        pass
            
            conn.commit()
            print("🗑️ Cleaned existing tables")
            
            # Create users table
            users_sql = """
                        CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                display_id VARCHAR(20) UNIQUE,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                gender VARCHAR(10),
                birth_date DATE,
                phone VARCHAR(20),
                username VARCHAR(50) UNIQUE,
                nickname VARCHAR(50),
                bio TEXT,
                avatar VARCHAR(500),
                cover_photo VARCHAR(500),
                location VARCHAR(100),
                website VARCHAR(200),
                relationship_status VARCHAR(20),
                work VARCHAR(100),
                education VARCHAR(100),
                profile_visibility VARCHAR(20) DEFAULT 'public',
                friend_request_privacy VARCHAR(20) DEFAULT 'everyone',
                post_visibility VARCHAR(20) DEFAULT 'public',
                story_visibility VARCHAR(20) DEFAULT 'public',
                email_visibility VARCHAR(20) DEFAULT 'private',
                phone_visibility VARCHAR(20) DEFAULT 'private',
                birth_date_visibility VARCHAR(20) DEFAULT 'friends',
                email_notifications BOOLEAN DEFAULT TRUE,
                push_notifications BOOLEAN DEFAULT TRUE,
                friend_request_notifications BOOLEAN DEFAULT TRUE,
                comment_notifications BOOLEAN DEFAULT TRUE,
                reaction_notifications BOOLEAN DEFAULT TRUE,
                message_notifications BOOLEAN DEFAULT TRUE,
                story_notifications BOOLEAN DEFAULT TRUE,
                is_active BOOLEAN DEFAULT TRUE,
                is_verified BOOLEAN DEFAULT FALSE,
                account_deactivated BOOLEAN DEFAULT FALSE,
                deactivated_at DATETIME NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                                INDEX idx_email (email),
                INDEX idx_username (username),
                INDEX idx_display_id (display_id),
                INDEX idx_is_active (is_active)
            ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """
            
            conn.execute(text(users_sql))
            print("✅ Users table created")
            
            # Create posts table
            posts_sql = """
            CREATE TABLE posts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                author_id INT NOT NULL,
                content TEXT NOT NULL,
                post_type VARCHAR(20) DEFAULT 'post',
                media_type VARCHAR(50),
                media_url VARCHAR(500),
                media_metadata TEXT,
                privacy VARCHAR(20) DEFAULT 'public',
                is_profile_update BOOLEAN DEFAULT FALSE,
                is_cover_update BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                reactions_count INT DEFAULT 0,
                comments_count INT DEFAULT 0,
                shares_count INT DEFAULT 0,
                FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_author_id (author_id),
                INDEX idx_created_at (created_at),
                INDEX idx_privacy (privacy)
            ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """
            
            conn.execute(text(posts_sql))
            print("✅ Posts table created")
            
            # Create stories table
            stories_sql = """
            CREATE TABLE stories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                author_id INT NOT NULL,
                content TEXT,
                media_type VARCHAR(50),
                media_url VARCHAR(500),
                background_color VARCHAR(7),
                duration_hours INT DEFAULT 24,
                max_duration_seconds INT DEFAULT 25,
                archived BOOLEAN DEFAULT FALSE,
                archived_at DATETIME NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME,
                views_count INT DEFAULT 0,
                FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_author_id (author_id),
                INDEX idx_expires_at (expires_at),
                INDEX idx_archived (archived)
            ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """
            
            conn.execute(text(stories_sql))
            print("✅ Stories table created")
            
            # Create story_views table
            story_views_sql = """
            CREATE TABLE story_views (
                id INT AUTO_INCREMENT PRIMARY KEY,
                story_id INT NOT NULL,
                viewer_id INT NOT NULL,
                viewed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE,
                FOREIGN KEY (viewer_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_story_viewer (story_id, viewer_id),
                INDEX idx_story_id (story_id),
                INDEX idx_viewer_id (viewer_id)
            ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """
            
            conn.execute(text(story_views_sql))
            print("✅ Story views table created")
            
            # Create story_tags table
            story_tags_sql = """
            CREATE TABLE story_tags (
                id INT AUTO_INCREMENT PRIMARY KEY,
                story_id INT NOT NULL,
                tagged_user_id INT NOT NULL,
                x_position FLOAT,
                y_position FLOAT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE,
                FOREIGN KEY (tagged_user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_story_id (story_id),
                INDEX idx_tagged_user_id (tagged_user_id)
            ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """
            
            conn.execute(text(story_tags_sql))
            print("✅ Story tags table created")
            
            # Create story_overlays table
            story_overlays_sql = """
            CREATE TABLE story_overlays (
                id INT AUTO_INCREMENT PRIMARY KEY,
                story_id INT NOT NULL,
                overlay_type VARCHAR(20) NOT NULL,
                content TEXT,
                x_position FLOAT,
                y_position FLOAT,
                width FLOAT,
                height FLOAT,
                rotation FLOAT DEFAULT 0,
                font_size INT,
                font_color VARCHAR(7),
                background_color VARCHAR(7),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE,
                INDEX idx_story_id (story_id)
            ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """
            
            conn.execute(text(story_overlays_sql))
            print("✅ Story overlays table created")
            
            # Create notifications table
            notifications_sql = """
            CREATE TABLE notifications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                recipient_id INT NOT NULL,
                sender_id INT,
                notification_type VARCHAR(50) NOT NULL,
                title VARCHAR(200),
                message TEXT,
                data TEXT,
                is_read BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recipient_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE SET NULL,
                INDEX idx_recipient_id (recipient_id),
                INDEX idx_is_read (is_read),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """
            
            conn.execute(text(notifications_sql))
            print("✅ Notifications table created")
            
            # Create friendships table
            friendships_sql = """
            CREATE TABLE friendships (
                id INT AUTO_INCREMENT PRIMARY KEY,
                requester_id INT NOT NULL,
                addressee_id INT NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (requester_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (addressee_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_friendship (requester_id, addressee_id),
                INDEX idx_requester_id (requester_id),
                INDEX idx_addressee_id (addressee_id),
                INDEX idx_status (status)
            ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """
            
            conn.execute(text(friendships_sql))
            print("✅ Friendships table created")
            
            # Create reactions table
            reactions_sql = """
            CREATE TABLE reactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                post_id INT NOT NULL,
                reaction_type VARCHAR(20) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_post_reaction (user_id, post_id),
                INDEX idx_post_id (post_id),
                INDEX idx_reaction_type (reaction_type)
            ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """
            
            conn.execute(text(reactions_sql))
            print("✅ Reactions table created")
            
            # Create comments table
            comments_sql = """
            CREATE TABLE comments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                post_id INT NOT NULL,
                author_id INT NOT NULL,
                content TEXT NOT NULL,
                parent_id INT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
                FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (parent_id) REFERENCES comments(id) ON DELETE CASCADE,
                INDEX idx_post_id (post_id),
                INDEX idx_author_id (author_id),
                INDEX idx_parent_id (parent_id)
            ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """
            
            conn.execute(text(comments_sql))
            print("✅ Comments table created")
            
            # Create shares table
            shares_sql = """
            CREATE TABLE shares (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                post_id INT NOT NULL,
                shared_with_comment TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_post_id (post_id)
            ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """
            
            conn.execute(text(shares_sql))
            print("✅ Shares table created")
            
            # Create messages table
            messages_sql = """
            CREATE TABLE messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                sender_id INT NOT NULL,
                recipient_id INT NOT NULL,
                content TEXT,
                message_type VARCHAR(20) DEFAULT 'text',
                media_url VARCHAR(500),
                media_metadata TEXT,
                is_read BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (recipient_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_sender_id (sender_id),
                INDEX idx_recipient_id (recipient_id),
                INDEX idx_is_read (is_read),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """
            
            conn.execute(text(messages_sql))
            print("✅ Messages table created")
            
            # Create media_files table
            media_files_sql = """
            CREATE TABLE media_files (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                filename VARCHAR(255) NOT NULL,
                original_filename VARCHAR(255),
                file_path VARCHAR(500) NOT NULL,
                file_size BIGINT,
                mime_type VARCHAR(100),
                media_type VARCHAR(20),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_media_type (media_type)
            ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """
            
            conn.execute(text(media_files_sql))
            print("✅ Media files table created")
            
            # Create blocks table
            blocks_sql = """
            CREATE TABLE blocks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                blocker_id INT NOT NULL,
                blocked_id INT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (blocker_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (blocked_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_block (blocker_id, blocked_id),
                INDEX idx_blocker_id (blocker_id),
                INDEX idx_blocked_id (blocked_id)
            ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """
            
            conn.execute(text(blocks_sql))
            print("✅ Blocks table created")
            
            # Create follows table
            follows_sql = """
            CREATE TABLE follows (
                id INT AUTO_INCREMENT PRIMARY KEY,
                follower_id INT NOT NULL,
                followed_id INT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (follower_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (followed_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_follow (follower_id, followed_id),
                INDEX idx_follower_id (follower_id),
                INDEX idx_followed_id (followed_id)
            ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """
            
            conn.execute(text(follows_sql))
            print("✅ Follows table created")
            
            # Create albums table
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
            print("✅ Albums table created")
            
            # Create album_photos table
            album_photos_sql = """
            CREATE TABLE album_photos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                album_id INT NOT NULL,
                photo_url VARCHAR(500) NOT NULL,
                caption TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (album_id) REFERENCES albums(id) ON DELETE CASCADE,
                INDEX idx_album_id (album_id)
            ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """
            
            conn.execute(text(album_photos_sql))
            print("✅ Album photos table created")
            
            conn.commit()
            
        print("\n🎉 DATABASE INITIALIZATION COMPLETE!")
        print("=" * 50)
        print("✅ All 15 tables created successfully")
        print("🔄 You can now restart your backend server")
        print("\n📋 Created tables:")
        print("   - users (with profile fields)")
        print("   - posts (with profile update flags)")
        print("   - stories, story_views, story_tags, story_overlays")
        print("   - notifications, friendships, reactions")
        print("   - comments, shares, messages")
        print("   - media_files, blocks, follows")
        print("   - albums, album_photos")

except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("💡 Install required packages:")
    print("   pip install sqlalchemy pymysql python-dotenv")
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n��� Make sure your MySQL server is running and credentials are correct")

if __name__ == "__main__":
    init_database()

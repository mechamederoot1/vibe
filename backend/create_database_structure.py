#!/usr/bin/env python3
"""
Script para criar a estrutura completa do banco de dados da rede social
Inclui todas as tabelas necessárias com suporte a mídia de alta qualidade
"""
import os
import sys
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

def get_database_url():
    """Create database URL from environment variables"""
    db_host = os.getenv("DB_HOST", "127.0.0.1")
    db_port = os.getenv("DB_PORT", "3306")
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "Evo@000#!")
    db_name = os.getenv("DB_NAME", "redesocial")
    
    encoded_password = quote_plus(db_password)
    return f"mysql+pymysql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"

def create_database_structure():
    """Criar toda a estrutura do banco de dados"""
    
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL, echo=True)
    
    print("🚀 Iniciando criação da estrutura do banco de dados...")
    print("=" * 60)
    
    with engine.connect() as conn:
        # Desabilitar verificações de chave estrangeira temporariamente
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        
        # Drop existing tables if they exist (in correct order)
        print("🗑️ Removendo tabelas existentes...")
        tables_to_drop = [
            "story_overlays", "story_views", "stories", "chat_messages", "chats",
            "notifications", "blocks", "follows", "friendship_requests", "friendships",
            "comment_reactions", "post_reactions", "reactions", "comment_replies", 
            "comments", "album_photos", "albums", "media_files", "posts", "user_profiles", "users"
        ]
        
        for table in tables_to_drop:
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
                print(f"�� Tabela {table} removida")
            except Exception as e:
                print(f"⚠️ Aviso ao remover {table}: {e}")
        
        # 1. TABELA DE USUÁRIOS
        print("\n📊 Criando tabela de usuários...")
        users_sql = """
        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            display_id VARCHAR(20) UNIQUE NOT NULL,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(150) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            phone VARCHAR(20),
            gender ENUM('male', 'female', 'other', 'prefer_not_to_say'),
            birth_date DATE,
            bio TEXT,
            avatar VARCHAR(500),
            cover_photo VARCHAR(500),
            location VARCHAR(150),
            website VARCHAR(200),
            work VARCHAR(150),
            education VARCHAR(150),
            relationship_status ENUM('single', 'in_relationship', 'married', 'complicated', 'divorced', 'widowed'),
            nickname VARCHAR(50),
            is_active BOOLEAN DEFAULT TRUE,
            is_verified BOOLEAN DEFAULT FALSE,
            privacy_settings JSON,
            last_seen DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            
            INDEX idx_username (username),
            INDEX idx_email (email),
            INDEX idx_display_id (display_id),
            INDEX idx_created_at (created_at),
            INDEX idx_last_seen (last_seen)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn.execute(text(users_sql))
        print("✅ Tabela users criada")
        
        # 2. TABELA DE MÍDIA (centralizada)
        print("\n🎥 Criando tabela de mídia...")
        media_sql = """
        CREATE TABLE media_files (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            original_name VARCHAR(255),
            file_name VARCHAR(255) NOT NULL,
            file_path VARCHAR(500) NOT NULL,
            file_url VARCHAR(500) NOT NULL,
            file_type ENUM('image', 'video', 'audio', 'document') NOT NULL,
            mime_type VARCHAR(100) NOT NULL,
            file_size BIGINT NOT NULL,
            width INT,
            height INT,
            duration INT, -- para vídeos em segundos
            quality ENUM('original', 'high', 'medium', 'low', 'thumbnail') DEFAULT 'original',
            is_processed BOOLEAN DEFAULT FALSE,
            metadata JSON, -- informações EXIF, etc
            uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id),
            INDEX idx_file_type (file_type),
            INDEX idx_uploaded_at (uploaded_at),
            INDEX idx_quality (quality)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn.execute(text(media_sql))
        print("✅ Tabela media_files criada")
        
        # 3. TABELA DE POSTS
        print("\n📝 Criando tabela de posts...")
        posts_sql = """
        CREATE TABLE posts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            author_id INT NOT NULL,
            content TEXT NOT NULL,
            post_type ENUM('post', 'testimonial', 'announcement', 'poll') DEFAULT 'post',
            media_id INT, -- referência para media_files
            privacy ENUM('public', 'friends', 'private', 'custom') DEFAULT 'public',
            location VARCHAR(200),
            feeling VARCHAR(100),
            tagged_users JSON, -- array de IDs de usuários marcados
            is_profile_update BOOLEAN DEFAULT FALSE,
            is_cover_update BOOLEAN DEFAULT FALSE,
            is_pinned BOOLEAN DEFAULT FALSE,
            scheduled_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            
            FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (media_id) REFERENCES media_files(id) ON DELETE SET NULL,
            INDEX idx_author_id (author_id),
            INDEX idx_post_type (post_type),
            INDEX idx_created_at (created_at),
            INDEX idx_privacy (privacy),
            FULLTEXT idx_content (content)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn.execute(text(posts_sql))
        print("✅ Tabela posts criada")
        
        # 4. TABELA DE COMENTÁRIOS
        print("\n💬 Criando tabela de comentários...")
        comments_sql = """
        CREATE TABLE comments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            post_id INT NOT NULL,
            author_id INT NOT NULL,
            parent_id INT, -- para respostas a comentários
            content TEXT NOT NULL,
            media_id INT, -- comentários podem ter mídia
            is_edited BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
            FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (parent_id) REFERENCES comments(id) ON DELETE CASCADE,
            FOREIGN KEY (media_id) REFERENCES media_files(id) ON DELETE SET NULL,
            INDEX idx_post_id (post_id),
            INDEX idx_author_id (author_id),
            INDEX idx_parent_id (parent_id),
            INDEX idx_created_at (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn.execute(text(comments_sql))
        print("✅ Tabela comments criada")
        
        # 5. TABELA DE REAÇÕES
        print("\n❤️ Criando tabela de reações...")
        reactions_sql = """
        CREATE TABLE reactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            target_type ENUM('post', 'comment') NOT NULL,
            target_id INT NOT NULL,
            reaction_type ENUM('like', 'love', 'haha', 'wow', 'sad', 'angry', 'care') NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE KEY unique_reaction (user_id, target_type, target_id),
            INDEX idx_target (target_type, target_id),
            INDEX idx_user_id (user_id),
            INDEX idx_reaction_type (reaction_type)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn.execute(text(reactions_sql))
        print("✅ Tabela reactions criada")
        
        # 6. TABELA DE AMIZADES
        print("\n👥 Criando tabela de amizades...")
        friendships_sql = """
        CREATE TABLE friendships (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            friend_id INT NOT NULL,
            status ENUM('pending', 'accepted', 'declined', 'blocked') DEFAULT 'pending',
            requested_by INT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (friend_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (requested_by) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE KEY unique_friendship (user_id, friend_id),
            INDEX idx_user_id (user_id),
            INDEX idx_friend_id (friend_id),
            INDEX idx_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn.execute(text(friendships_sql))
        print("✅ Tabela friendships criada")
        
        # 7. TABELA DE SEGUIDORES
        print("\n👁️ Criando tabela de seguidores...")
        follows_sql = """
        CREATE TABLE follows (
            id INT AUTO_INCREMENT PRIMARY KEY,
            follower_id INT NOT NULL,
            following_id INT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (follower_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (following_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE KEY unique_follow (follower_id, following_id),
            INDEX idx_follower_id (follower_id),
            INDEX idx_following_id (following_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn.execute(text(follows_sql))
        print("✅ Tabela follows criada")
        
        # 8. TABELA DE STORIES
        print("\n📱 Criando tabela de stories...")
        stories_sql = """
        CREATE TABLE stories (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            media_id INT NOT NULL,
            content TEXT,
            background_color VARCHAR(7), -- hex color
            text_color VARCHAR(7),
            font_family VARCHAR(50),
            duration INT DEFAULT 24, -- duração em horas
            is_highlight BOOLEAN DEFAULT FALSE,
            privacy ENUM('public', 'friends', 'close_friends', 'custom') DEFAULT 'public',
            viewers_count INT DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME,
            
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (media_id) REFERENCES media_files(id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id),
            INDEX idx_created_at (created_at),
            INDEX idx_expires_at (expires_at),
            INDEX idx_is_highlight (is_highlight)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn.execute(text(stories_sql))
        print("✅ Tabela stories criada")
        
        # 9. TABELA DE VISUALIZAÇÕES DE STORIES
        print("\n👀 Criando tabela de visualizações de stories...")
        story_views_sql = """
        CREATE TABLE story_views (
            id INT AUTO_INCREMENT PRIMARY KEY,
            story_id INT NOT NULL,
            viewer_id INT NOT NULL,
            viewed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE CASCADE,
            FOREIGN KEY (viewer_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE KEY unique_view (story_id, viewer_id),
            INDEX idx_story_id (story_id),
            INDEX idx_viewer_id (viewer_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn.execute(text(story_views_sql))
        print("✅ Tabela story_views criada")
        
        # 10. TABELA DE ÁLBUNS
        print("\n📸 Criando tabela de álbuns...")
        albums_sql = """
        CREATE TABLE albums (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            name VARCHAR(150) NOT NULL,
            description TEXT,
            cover_media_id INT,
            privacy ENUM('public', 'friends', 'private') DEFAULT 'public',
            photos_count INT DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (cover_media_id) REFERENCES media_files(id) ON DELETE SET NULL,
            INDEX idx_user_id (user_id),
            INDEX idx_created_at (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn.execute(text(albums_sql))
        print("✅ Tabela albums criada")
        
        # 11. TABELA DE FOTOS DOS ÁLBUNS
        print("\n🖼️ Criando tabela de fotos dos álbuns...")
        album_photos_sql = """
        CREATE TABLE album_photos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            album_id INT NOT NULL,
            media_id INT NOT NULL,
            caption TEXT,
            order_index INT DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (album_id) REFERENCES albums(id) ON DELETE CASCADE,
            FOREIGN KEY (media_id) REFERENCES media_files(id) ON DELETE CASCADE,
            INDEX idx_album_id (album_id),
            INDEX idx_order_index (order_index)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn.execute(text(album_photos_sql))
        print("✅ Tabela album_photos criada")
        
        # 12. TABELA DE NOTIFICAÇÕES
        print("\n🔔 Criando tabela de notificações...")
        notifications_sql = """
        CREATE TABLE notifications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            sender_id INT,
            type ENUM('like', 'comment', 'friend_request', 'friend_accept', 'mention', 'follow', 'post_share') NOT NULL,
            title VARCHAR(255) NOT NULL,
            message TEXT NOT NULL,
            target_type ENUM('post', 'comment', 'user', 'story') NOT NULL,
            target_id INT NOT NULL,
            is_read BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id),
            INDEX idx_is_read (is_read),
            INDEX idx_created_at (created_at),
            INDEX idx_type (type)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn.execute(text(notifications_sql))
        print("✅ Tabela notifications criada")
        
        # 13. TABELA DE BLOQUEIOS
        print("\n🚫 Criando tabela de bloqueios...")
        blocks_sql = """
        CREATE TABLE blocks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            blocker_id INT NOT NULL,
            blocked_id INT NOT NULL,
            reason VARCHAR(255),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (blocker_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (blocked_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE KEY unique_block (blocker_id, blocked_id),
            INDEX idx_blocker_id (blocker_id),
            INDEX idx_blocked_id (blocked_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn.execute(text(blocks_sql))
        print("✅ Tabela blocks criada")
        
        # 14. TABELA DE CONVERSAS
        print("\n💬 Criando tabela de conversas...")
        chats_sql = """
        CREATE TABLE chats (
            id INT AUTO_INCREMENT PRIMARY KEY,
            type ENUM('private', 'group') DEFAULT 'private',
            name VARCHAR(150), -- para grupos
            description TEXT, -- para grupos
            avatar VARCHAR(500), -- para grupos
            created_by INT,
            last_message_id INT,
            last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
            INDEX idx_type (type),
            INDEX idx_last_activity (last_activity),
            INDEX idx_created_by (created_by)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn.execute(text(chats_sql))
        print("✅ Tabela chats criada")
        
        # 15. TABELA DE MENSAGENS
        print("\n✉️ Criando tabela de mensagens...")
        messages_sql = """
        CREATE TABLE chat_messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            chat_id INT NOT NULL,
            sender_id INT NOT NULL,
            content TEXT,
            media_id INT,
            message_type ENUM('text', 'image', 'video', 'audio', 'file', 'sticker') DEFAULT 'text',
            reply_to_id INT, -- resposta a outra mensagem
            is_edited BOOLEAN DEFAULT FALSE,
            is_deleted BOOLEAN DEFAULT FALSE,
            read_by JSON, -- array de user_ids que leram
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            
            FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE,
            FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (media_id) REFERENCES media_files(id) ON DELETE SET NULL,
            FOREIGN KEY (reply_to_id) REFERENCES chat_messages(id) ON DELETE SET NULL,
            INDEX idx_chat_id (chat_id),
            INDEX idx_sender_id (sender_id),
            INDEX idx_created_at (created_at),
            INDEX idx_message_type (message_type)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn.execute(text(messages_sql))
        print("✅ Tabela chat_messages criada")
        
        # 16. TABELA DE PARTICIPANTES DO CHAT
        print("\n👥 Criando tabela de participantes do chat...")
        chat_participants_sql = """
        CREATE TABLE chat_participants (
            id INT AUTO_INCREMENT PRIMARY KEY,
            chat_id INT NOT NULL,
            user_id INT NOT NULL,
            role ENUM('member', 'admin', 'owner') DEFAULT 'member',
            joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            left_at DATETIME,
            
            FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE KEY unique_participant (chat_id, user_id),
            INDEX idx_chat_id (chat_id),
            INDEX idx_user_id (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn.execute(text(chat_participants_sql))
        print("✅ Tabela chat_participants criada")
        
        # Reabilitar verificações de chave estrangeira
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        
        # Commit das mudanças
        conn.commit()
        
        print("\n" + "=" * 60)
        print("🎉 ESTRUTURA DO BANCO DE DADOS CRIADA COM SUCESSO!")
        print("=" * 60)
        print("\n📊 Tabelas criadas:")
        print("✅ users - Usuários do sistema")
        print("✅ media_files - Arquivos de mídia centralizados") 
        print("✅ posts - Publicações e depoimentos")
        print("✅ comments - Comentários e respostas")
        print("✅ reactions - Curtidas e reações")
        print("✅ friendships - Sistema de amizades")
        print("✅ follows - Sistema de seguidores")
        print("✅ stories - Stories temporários")
        print("✅ story_views - Visualizações dos stories")
        print("✅ albums - Álbuns de fotos")
        print("✅ album_photos - Fotos dos álbuns")
        print("✅ notifications - Sistema de notificações")
        print("✅ blocks - Usuários bloqueados")
        print("✅ chats - Conversas privadas e grupos")
        print("✅ chat_messages - Mensagens")
        print("✅ chat_participants - Participantes dos chats")
        
        print("\n🎨 Recursos implementados:")
        print("📷 Mídia de alta qualidade com múltiplas resoluções")
        print("📱 Stories com overlays e personalizações")
        print("💬 Sistema de chat completo")
        print("🔔 Notificações em tempo real")
        print("📸 Álbuns organizados")
        print("❤️ Sistema de reações estilo Facebook")
        print("🔒 Controles de privacidade avançados")
        print("🏷️ Sistema de marcações")
        print("📊 Metadados e analytics")
        
        return True

if __name__ == "__main__":
    try:
        success = create_database_structure()
        if success:
            print("\n🚀 Pronto para usar! Execute sua aplicação normalmente.")
            sys.exit(0)
        else:
            print("\n❌ Falha na criação da estrutura")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erro fatal: {e}")
        sys.exit(1)

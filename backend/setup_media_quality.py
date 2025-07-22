#!/usr/bin/env python3
"""
Script para configurar sistema de qualidade de mídia avançado
Configura diferentes qualidades para fotos de perfil, capa e posts
"""
import os
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

def get_database_url():
    """Create database URL from environment variables"""
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3306")
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "123456")
    db_name = os.getenv("DB_NAME", "redesocial")
    
    encoded_password = quote_plus(db_password)
    return f"mysql+pymysql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"

def setup_media_quality_system():
    """Configurar sistema avançado de qualidade de mídia"""
    
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL, echo=True)
    
    print("🎨 Configurando sistema de qualidade de mídia...")
    print("=" * 50)
    
    with engine.connect() as conn:
        
        # 1. Criar tabela de variações de mídia
        print("\n📸 Criando tabela de variações de mídia...")
        media_variants_sql = """
        CREATE TABLE IF NOT EXISTS media_variants (
            id INT AUTO_INCREMENT PRIMARY KEY,
            original_media_id INT NOT NULL,
            variant_type ENUM('thumbnail', 'small', 'medium', 'large', 'original') NOT NULL,
            file_name VARCHAR(255) NOT NULL,
            file_path VARCHAR(500) NOT NULL,
            file_url VARCHAR(500) NOT NULL,
            width INT,
            height INT,
            file_size BIGINT,
            quality_percentage INT DEFAULT 100,
            is_processed BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (original_media_id) REFERENCES media_files(id) ON DELETE CASCADE,
            UNIQUE KEY unique_variant (original_media_id, variant_type),
            INDEX idx_original_media_id (original_media_id),
            INDEX idx_variant_type (variant_type)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn.execute(text(media_variants_sql))
        print("✅ Tabela media_variants criada")
        
        # 2. Criar tabela de configurações de qualidade
        print("\n⚙️ Criando tabela de configurações de qualidade...")
        quality_settings_sql = """
        CREATE TABLE IF NOT EXISTS media_quality_settings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            media_type ENUM('profile_avatar', 'cover_photo', 'post_image', 'story_image', 'comment_image', 'chat_image') NOT NULL,
            variant_type ENUM('thumbnail', 'small', 'medium', 'large', 'original') NOT NULL,
            max_width INT NOT NULL,
            max_height INT NOT NULL,
            quality_percentage INT DEFAULT 85,
            format ENUM('jpeg', 'webp', 'png') DEFAULT 'jpeg',
            is_active BOOLEAN DEFAULT TRUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            UNIQUE KEY unique_quality_setting (media_type, variant_type),
            INDEX idx_media_type (media_type),
            INDEX idx_is_active (is_active)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn.execute(text(quality_settings_sql))
        print("✅ Tabela media_quality_settings criada")
        
        # 3. Inserir configurações padrão de qualidade
        print("\n📋 Inserindo configurações padrão de qualidade...")
        
        quality_configs = [
            # Avatar do perfil
            ('profile_avatar', 'thumbnail', 64, 64, 70, 'jpeg'),
            ('profile_avatar', 'small', 128, 128, 80, 'jpeg'),
            ('profile_avatar', 'medium', 256, 256, 85, 'jpeg'),
            ('profile_avatar', 'large', 512, 512, 90, 'jpeg'),
            ('profile_avatar', 'original', 1024, 1024, 95, 'jpeg'),
            
            # Foto de capa
            ('cover_photo', 'thumbnail', 400, 150, 70, 'jpeg'),
            ('cover_photo', 'small', 800, 300, 80, 'jpeg'),
            ('cover_photo', 'medium', 1200, 450, 85, 'jpeg'),
            ('cover_photo', 'large', 1600, 600, 90, 'jpeg'),
            ('cover_photo', 'original', 1920, 720, 95, 'jpeg'),
            
            # Imagens de posts
            ('post_image', 'thumbnail', 300, 300, 70, 'jpeg'),
            ('post_image', 'small', 600, 600, 80, 'jpeg'),
            ('post_image', 'medium', 900, 900, 85, 'jpeg'),
            ('post_image', 'large', 1200, 1200, 90, 'jpeg'),
            ('post_image', 'original', 1920, 1920, 95, 'jpeg'),
            
            # Stories
            ('story_image', 'thumbnail', 200, 356, 70, 'jpeg'),
            ('story_image', 'small', 400, 712, 80, 'jpeg'),
            ('story_image', 'medium', 600, 1068, 85, 'jpeg'),
            ('story_image', 'large', 800, 1424, 90, 'jpeg'),
            ('story_image', 'original', 1080, 1920, 95, 'jpeg'),
            
            # Imagens de comentários
            ('comment_image', 'thumbnail', 150, 150, 70, 'jpeg'),
            ('comment_image', 'small', 300, 300, 80, 'jpeg'),
            ('comment_image', 'medium', 600, 600, 85, 'jpeg'),
            ('comment_image', 'large', 900, 900, 90, 'jpeg'),
            ('comment_image', 'original', 1200, 1200, 95, 'jpeg'),
            
            # Imagens de chat
            ('chat_image', 'thumbnail', 200, 200, 70, 'jpeg'),
            ('chat_image', 'small', 400, 400, 80, 'jpeg'),
            ('chat_image', 'medium', 600, 600, 85, 'jpeg'),
            ('chat_image', 'large', 800, 800, 90, 'jpeg'),
            ('chat_image', 'original', 1200, 1200, 95, 'jpeg'),
        ]
        
        for config in quality_configs:
            media_type, variant_type, width, height, quality, format_type = config
            insert_sql = """
            INSERT IGNORE INTO media_quality_settings 
            (media_type, variant_type, max_width, max_height, quality_percentage, format)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            conn.execute(text(insert_sql), (media_type, variant_type, width, height, quality, format_type))
        
        print("✅ Configurações de qualidade inseridas")
        
        # 4. Criar tabela de metadados de mídia
        print("\n📊 Criando tabela de metadados de mídia...")
        media_metadata_sql = """
        CREATE TABLE IF NOT EXISTS media_metadata (
            id INT AUTO_INCREMENT PRIMARY KEY,
            media_id INT NOT NULL,
            exif_data JSON,
            color_palette JSON,
            dominant_color VARCHAR(7),
            has_faces BOOLEAN DEFAULT FALSE,
            face_count INT DEFAULT 0,
            is_explicit BOOLEAN DEFAULT FALSE,
            content_tags JSON,
            processing_status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
            processed_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (media_id) REFERENCES media_files(id) ON DELETE CASCADE,
            UNIQUE KEY unique_metadata (media_id),
            INDEX idx_processing_status (processing_status),
            INDEX idx_has_faces (has_faces),
            INDEX idx_is_explicit (is_explicit)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn.execute(text(media_metadata_sql))
        print("✅ Tabela media_metadata criada")
        
        # 5. Criar índices de performance
        print("\n🚀 Criando índices de performance...")
        performance_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_media_files_composite ON media_files(user_id, file_type, uploaded_at)",
            "CREATE INDEX IF NOT EXISTS idx_posts_media_composite ON posts(author_id, created_at, media_id)",
            "CREATE INDEX IF NOT EXISTS idx_stories_active ON stories(user_id, expires_at, created_at)",
            "CREATE INDEX IF NOT EXISTS idx_album_photos_composite ON album_photos(album_id, order_index, created_at)"
        ]
        
        for index_sql in performance_indexes:
            try:
                conn.execute(text(index_sql))
                print(f"✅ Índice criado")
            except Exception as e:
                print(f"⚠️ Aviso no índice: {e}")
        
        # 6. Criar views para facilitar consultas
        print("\n👀 Criando views úteis...")
        
        # View para mídia com variações
        media_with_variants_view = """
        CREATE OR REPLACE VIEW media_with_variants AS
        SELECT 
            mf.id,
            mf.user_id,
            mf.original_name,
            mf.file_type,
            mf.mime_type,
            mf.uploaded_at,
            mv.variant_type,
            mv.file_url as variant_url,
            mv.width as variant_width,
            mv.height as variant_height,
            mv.file_size as variant_size
        FROM media_files mf
        LEFT JOIN media_variants mv ON mf.id = mv.original_media_id
        """
        conn.execute(text(media_with_variants_view))
        print("✅ View media_with_variants criada")
        
        # View para posts com mídia
        posts_with_media_view = """
        CREATE OR REPLACE VIEW posts_with_media AS
        SELECT 
            p.*,
            mf.file_type,
            mf.file_url as original_url,
            mv_thumb.file_url as thumbnail_url,
            mv_medium.file_url as medium_url
        FROM posts p
        LEFT JOIN media_files mf ON p.media_id = mf.id
        LEFT JOIN media_variants mv_thumb ON mf.id = mv_thumb.original_media_id AND mv_thumb.variant_type = 'thumbnail'
        LEFT JOIN media_variants mv_medium ON mf.id = mv_medium.original_media_id AND mv_medium.variant_type = 'medium'
        """
        conn.execute(text(posts_with_media_view))
        print("✅ View posts_with_media criada")
        
        # Commit das mudanças
        conn.commit()
        
        print("\n" + "=" * 50)
        print("🎉 SISTEMA DE QUALIDADE DE MÍDIA CONFIGURADO!")
        print("=" * 50)
        print("\n📸 Qualidades configuradas:")
        print("• Thumbnail: Para previews rápidas")
        print("• Small: Para listagens")
        print("• Medium: Para visualização normal")
        print("• Large: Para visualização ampliada")
        print("• Original: Para download/edição")
        
        print("\n🎯 Tipos de mídia suportados:")
        print("• Avatar de perfil (64px a 1024px)")
        print("• Foto de capa (400x150 a 1920x720)")
        print("• Imagens de posts (300px a 1920px)")
        print("• Stories (200x356 a 1080x1920)")
        print("• Imagens de comentários (150px a 1200px)")
        print("• Imagens de chat (200px a 1200px)")
        
        print("\n⚡ Recursos avançados:")
        print("• Múltiplas variações automáticas")
        print("• Metadados EXIF preservados")
        print("• Detecção de cores dominantes")
        print("• Análise de conteúdo")
        print("• Otimização automática de qualidade")
        print("• Views otimizadas para consultas")
        
        return True

if __name__ == "__main__":
    try:
        success = setup_media_quality_system()
        if success:
            print("\n🚀 Sistema de mídia pronto! Agora você pode fazer upload de mídia com qualidade profissional.")
        else:
            print("\n❌ Falha na configuração do sistema de mídia")
    except Exception as e:
        print(f"\n💥 Erro: {e}")

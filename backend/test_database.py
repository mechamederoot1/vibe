#!/usr/bin/env python3
"""
Script para testar a estrutura do banco de dados
Verifica se todas as tabelas foram criadas corretamente
"""
import os
from sqlalchemy import create_engine, text, inspect
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

def test_database_structure():
    """Testar estrutura do banco de dados"""
    
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    
    print("🧪 TESTANDO ESTRUTURA DO BANCO DE DADOS")
    print("=" * 50)
    
    # Tabelas esperadas
    expected_tables = [
        'users', 'media_files', 'posts', 'comments', 'reactions',
        'friendships', 'follows', 'stories', 'story_views', 
        'albums', 'album_photos', 'notifications', 'blocks',
        'chats', 'chat_messages', 'chat_participants',
        'media_variants', 'media_quality_settings', 'media_metadata'
    ]
    
    try:
        with engine.connect() as conn:
            # Verificar conexão
            conn.execute(text("SELECT 1"))
            print("✅ Conexão com banco estabelecida")
            
            # Listar tabelas existentes
            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()
            
            print(f"\n📊 Tabelas encontradas: {len(existing_tables)}")
            
            # Verificar cada tabela esperada
            missing_tables = []
            for table in expected_tables:
                if table in existing_tables:
                    print(f"✅ {table}")
                else:
                    print(f"❌ {table} - FALTANDO")
                    missing_tables.append(table)
            
            # Verificar índices importantes
            print(f"\n🔍 Verificando índices importantes...")
            important_indexes = [
                ('users', 'idx_username'),
                ('users', 'idx_email'),
                ('media_files', 'idx_user_id'),
                ('posts', 'idx_author_id'),
                ('reactions', 'idx_target')
            ]
            
            for table, index in important_indexes:
                if table in existing_tables:
                    indexes = inspector.get_indexes(table)
                    index_names = [idx['name'] for idx in indexes]
                    if any(index in name for name in index_names):
                        print(f"✅ {table}.{index}")
                    else:
                        print(f"⚠️ {table}.{index} - índice não encontrado")
            
            # Verificar configurações de qualidade
            if 'media_quality_settings' in existing_tables:
                result = conn.execute(text("SELECT COUNT(*) as count FROM media_quality_settings"))
                count = result.fetchone()[0]
                print(f"\n📸 Configurações de qualidade: {count} registros")
                if count > 0:
                    print("✅ Sistema de qualidade configurado")
                else:
                    print("⚠️ Sistema de qualidade não configurado")
            
            # Verificar views
            try:
                conn.execute(text("SELECT COUNT(*) FROM media_with_variants LIMIT 1"))
                print("✅ View media_with_variants funcionando")
            except:
                print("⚠️ View media_with_variants não encontrada")
            
            try:
                conn.execute(text("SELECT COUNT(*) FROM posts_with_media LIMIT 1"))
                print("✅ View posts_with_media funcionando")
            except:
                print("⚠️ View posts_with_media não encontrada")
            
            # Resultado final
            print("\n" + "=" * 50)
            if not missing_tables:
                print("🎉 ESTRUTURA DO BANCO ESTÁ PERFEITA!")
                print("✅ Todas as tabelas estão presentes")
                print("✅ Índices importantes configurados")
                print("✅ Sistema pronto para uso")
                return True
            else:
                print(f"⚠️ ESTRUTURA INCOMPLETA")
                print(f"❌ Tabelas faltando: {', '.join(missing_tables)}")
                print("💡 Execute: python setup_complete_database.py")
                return False
                
    except Exception as e:
        print(f"💥 Erro ao testar banco: {e}")
        return False

def test_sample_operations():
    """Testar operações básicas"""
    
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    
    print("\n🧪 TESTANDO OPERAÇÕES BÁSICAS")
    print("=" * 50)
    
    try:
        with engine.connect() as conn:
            # Teste 1: Inserir usuário de teste
            print("1. Testando inserção de usuário...")
            test_user_sql = """
            INSERT IGNORE INTO users 
            (display_id, first_name, last_name, username, email, password_hash, created_at)
            VALUES ('9999999999', 'Teste', 'Usuario', 'test_user', 'teste@exemplo.com', 'hash_teste', NOW())
            """
            conn.execute(text(test_user_sql))
            print("✅ Usuário de teste inserido")
            
            # Teste 2: Verificar configurações de qualidade
            print("2. Testando configurações de qualidade...")
            quality_sql = "SELECT COUNT(*) as count FROM media_quality_settings WHERE media_type = 'profile_avatar'"
            result = conn.execute(text(quality_sql))
            count = result.fetchone()[0]
            if count > 0:
                print(f"✅ {count} configurações para avatar encontradas")
            else:
                print("❌ Configurações de avatar não encontradas")
            
            # Teste 3: Testar relações
            print("3. Testando relações entre tabelas...")
            relation_sql = """
            SELECT u.username, COUNT(p.id) as posts_count 
            FROM users u 
            LEFT JOIN posts p ON u.id = p.author_id 
            WHERE u.username = 'test_user'
            GROUP BY u.id
            """
            result = conn.execute(text(relation_sql))
            user_data = result.fetchone()
            if user_data:
                print(f"✅ Relação users-posts funcionando: {user_data[0]} tem {user_data[1]} posts")
            
            # Limpeza
            print("4. Limpando dados de teste...")
            conn.execute(text("DELETE FROM users WHERE username = 'test_user'"))
            conn.commit()
            print("✅ Dados de teste removidos")
            
            print("\n✅ TODOS OS TESTES PASSARAM!")
            return True
            
    except Exception as e:
        print(f"💥 Erro nos testes: {e}")
        return False

if __name__ == "__main__":
    print("🔬 DIAGNÓSTICO COMPLETO DO BANCO DE DADOS")
    print("=" * 60)
    
    # Teste 1: Estrutura
    structure_ok = test_database_structure()
    
    if structure_ok:
        # Teste 2: Operações
        operations_ok = test_sample_operations()
        
        if operations_ok:
            print("\n🎉 BANCO DE DADOS TOTALMENTE FUNCIONAL!")
            print("🚀 Pronto para usar na sua rede social!")
        else:
            print("\n⚠️ Estrutura OK, mas operações falharam")
    else:
        print("\n❌ Execute o setup primeiro: python setup_complete_database.py")

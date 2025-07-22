#!/usr/bin/env python3
"""
Script para executar a configuração do banco de dados para verificação de e-mail
Este script adiciona as tabelas necessárias para armazenar tokens e códigos de verificação
"""

import os
import sys
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def get_database_connection():
    """Criar conexão com o banco de dados"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '3306'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'Evo@000#!'),
            database=os.getenv('DB_NAME', 'vibe'),
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        print(f"✅ Conectado ao banco: {connection.server_host}:{connection.server_port}")
        return connection
    except Error as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        return None

def create_email_verification_tables(connection):
    """Criar tabelas para verificação de e-mail"""
    
    # SQL para criar tabela de verificações de e-mail
    email_verifications_sql = """
    CREATE TABLE IF NOT EXISTS email_verifications (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        email VARCHAR(255) NOT NULL,
        verification_code VARCHAR(6) NOT NULL,
        verification_token VARCHAR(64) NOT NULL,
        expires_at DATETIME NOT NULL,
        verified BOOLEAN DEFAULT FALSE,
        verified_at DATETIME NULL,
        attempts INT DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        
        -- Índices para performance
        INDEX idx_user_id (user_id),
        INDEX idx_verification_code (verification_code),
        INDEX idx_verification_token (verification_token),
        INDEX idx_expires_at (expires_at),
        INDEX idx_verified (verified),
        
        -- Chave estrangeira para usuários
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        
        -- Constraint para garantir apenas uma verificação ativa por usuário
        UNIQUE KEY unique_user_verification (user_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    # SQL para criar tabela de logs de e-mail
    email_logs_sql = """
    CREATE TABLE IF NOT EXISTS email_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        email VARCHAR(255) NOT NULL,
        email_type ENUM('verification', 'password_reset', 'notification') DEFAULT 'verification',
        status ENUM('sent', 'failed', 'bounced') DEFAULT 'sent',
        error_message TEXT NULL,
        sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        
        -- Índices
        INDEX idx_user_id (user_id),
        INDEX idx_email_type (email_type),
        INDEX idx_status (status),
        INDEX idx_sent_at (sent_at),
        
        -- Chave estrangeira
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    # SQL para configurações do sistema
    system_config_sql = """
    CREATE TABLE IF NOT EXISTS system_config (
        id INT AUTO_INCREMENT PRIMARY KEY,
        config_key VARCHAR(100) UNIQUE NOT NULL,
        config_value TEXT NOT NULL,
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    # Configurações padrão
    config_inserts = [
        ("email_verification_enabled", "true", "Habilitar verificação de e-mail para novos usuários"),
        ("verification_code_expiry", "300000", "Tempo de expiração do código em milissegundos (5 minutos)"),
        ("max_resend_attempts", "5", "Máximo de tentativas de reenvio por hora"),
        ("resend_cooldown", "60000", "Tempo de espera entre reenvios em milissegundos (1 minuto)"),
        ("email_template_name", "Vibe", "Nome exibido nos e-mails"),
        ("email_template_from", "no-reply@meuvibe.com", "E-mail de origem para verificação")
    ]
    
    try:
        cursor = connection.cursor()
        
        # Criar tabela de verificações
        print("📋 Criando tabela email_verifications...")
        cursor.execute(email_verifications_sql)
        print("✅ Tabela email_verifications criada com sucesso")
        
        # Criar tabela de logs
        print("📋 Criando tabela email_logs...")
        cursor.execute(email_logs_sql)
        print("✅ Tabela email_logs criada com sucesso")
        
        # Criar tabela de configurações
        print("📋 Criando tabela system_config...")
        cursor.execute(system_config_sql)
        print("✅ Tabela system_config criada com sucesso")
        
        # Inserir configurações padrão
        print("📋 Inserindo configurações padrão...")
        for key, value, description in config_inserts:
            insert_sql = """
            INSERT IGNORE INTO system_config (config_key, config_value, description) 
            VALUES (%s, %s, %s)
            """
            cursor.execute(insert_sql, (key, value, description))
            print(f"   - {key}: {value}")
        
        connection.commit()
        cursor.close()
        
        print("\n🎉 Todas as tabelas foram criadas com sucesso!")
        
    except Error as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False
    
    return True

def add_user_email_columns(connection):
    """Adicionar colunas relacionadas à verificação de e-mail na tabela users"""
    
    columns_to_add = [
        ("email_verified_at", "DATETIME NULL", "Data de verificação do e-mail"),
        ("email_verification_required", "BOOLEAN DEFAULT TRUE", "Se verificação de e-mail é obrigatória")
    ]
    
    try:
        cursor = connection.cursor()
        
        for column_name, column_def, description in columns_to_add:
            try:
                # Verificar se a coluna já existe
                check_sql = """
                SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'users' AND COLUMN_NAME = %s
                """
                cursor.execute(check_sql, (os.getenv('DB_NAME', 'vibe'), column_name))
                
                if not cursor.fetchone():
                    # Adicionar coluna se não existir
                    alter_sql = f"ALTER TABLE users ADD COLUMN {column_name} {column_def}"
                    cursor.execute(alter_sql)
                    print(f"✅ Coluna '{column_name}' adicionada à tabela users")
                else:
                    print(f"⚠️ Coluna '{column_name}' já existe na tabela users")
                    
            except Error as e:
                print(f"❌ Erro ao adicionar coluna '{column_name}': {e}")
        
        connection.commit()
        cursor.close()
        
    except Error as e:
        print(f"❌ Erro ao modificar tabela users: {e}")
        return False
    
    return True

def verify_tables_created(connection):
    """Verificar se as tabelas foram criadas corretamente"""
    
    tables_to_check = ['email_verifications', 'email_logs', 'system_config']
    
    try:
        cursor = connection.cursor()
        
        print("\n🔍 Verificando tabelas criadas:")
        
        for table_name in tables_to_check:
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            if cursor.fetchone():
                print(f"✅ Tabela '{table_name}' existe")
                
                # Mostrar estrutura da tabela
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                print(f"   Colunas ({len(columns)}): {[col[0] for col in columns[:5]]}{'...' if len(columns) > 5 else ''}")
            else:
                print(f"❌ Tabela '{table_name}' não foi encontrada")
        
        # Verificar configurações inseridas
        cursor.execute("SELECT COUNT(*) FROM system_config WHERE config_key LIKE '%email%'")
        config_count = cursor.fetchone()[0]
        print(f"✅ Configurações de e-mail inseridas: {config_count}")
        
        cursor.close()
        
    except Error as e:
        print(f"❌ Erro ao verificar tabelas: {e}")

def main():
    """Função principal"""
    print("🚀 Configurando banco de dados para verificação de e-mail...")
    print("="*60)
    
    # Conectar ao banco
    connection = get_database_connection()
    if not connection:
        print("❌ Não foi possível conectar ao banco de dados")
        sys.exit(1)
    
    try:
        # Criar tabelas para verificação de e-mail
        if not create_email_verification_tables(connection):
            print("❌ Falha ao criar tabelas de verificação")
            sys.exit(1)
        
        # Adicionar colunas à tabela users
        if not add_user_email_columns(connection):
            print("❌ Falha ao modificar tabela users")
            sys.exit(1)
        
        # Verificar se tudo foi criado
        verify_tables_created(connection)
        
        print("\n" + "="*60)
        print("🎉 Configuração do banco concluída com sucesso!")
        print("\n📋 Próximos passos:")
        print("1. Iniciar microserviço de e-mail: cd backend/email-service && npm start")
        print("2. Iniciar backend principal: cd backend && python main.py")
        print("3. Testar verificação de e-mail no frontend")
        
    finally:
        if connection.is_connected():
            connection.close()
            print("\n🔌 Conexão com banco fechada")

if __name__ == "__main__":
    main()

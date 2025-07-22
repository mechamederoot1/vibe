#!/usr/bin/env python3
"""
Script para configurar as tabelas de verificação de e-mail no banco de dados
Executa automaticamente o SQL necessário para o sistema de verificação
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
        return connection
    except Error as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        return None

def execute_sql_file(connection, file_path):
    """Executar comandos SQL de um arquivo"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Dividir comandos SQL por ponto e vírgula
        commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
        
        cursor = connection.cursor()
        
        for command in commands:
            # Pular comentários e comandos vazios
            if command.startswith('--') or not command:
                continue
                
            try:
                cursor.execute(command)
                print(f"✅ Executado: {command[:50]}...")
            except Error as e:
                if "already exists" in str(e) or "Duplicate" in str(e):
                    print(f"⚠️ Já existe: {command[:50]}...")
                else:
                    print(f"❌ Erro em: {command[:50]}... -> {e}")
        
        connection.commit()
        cursor.close()
        
    except FileNotFoundError:
        print(f"❌ Arquivo SQL não encontrado: {file_path}")
    except Error as e:
        print(f"❌ Erro ao executar SQL: {e}")

def setup_email_verification():
    """Configurar sistema de verificação de e-mail"""
    print("🚀 Configurando sistema de verificação de e-mail...")
    
    # Conectar ao banco
    connection = get_database_connection()
    if not connection:
        sys.exit(1)
    
    try:
        # Executar script SQL
        sql_file = 'setup_email_verification.sql'
        if os.path.exists(sql_file):
            execute_sql_file(connection, sql_file)
        else:
            print(f"❌ Arquivo {sql_file} não encontrado")
            sys.exit(1)
        
        # Verificar se as tabelas foram criadas
        cursor = connection.cursor()
        
        # Verificar tabela email_verifications
        cursor.execute("SHOW TABLES LIKE 'email_verifications'")
        if cursor.fetchone():
            print("✅ Tabela 'email_verifications' criada com sucesso")
        else:
            print("❌ Falha ao criar tabela 'email_verifications'")
        
        # Verificar tabela email_logs
        cursor.execute("SHOW TABLES LIKE 'email_logs'")
        if cursor.fetchone():
            print("✅ Tabela 'email_logs' criada com sucesso")
        else:
            print("❌ Falha ao criar tabela 'email_logs'")
        
        # Verificar configurações
        cursor.execute("SHOW TABLES LIKE 'system_config'")
        if cursor.fetchone():
            print("✅ Tabela 'system_config' criada com sucesso")
            
            # Mostrar configurações inseridas
            cursor.execute("SELECT config_key, config_value FROM system_config WHERE config_key LIKE '%email%'")
            configs = cursor.fetchall()
            
            if configs:
                print("\n📧 Configurações de e-mail:")
                for key, value in configs:
                    print(f"  {key}: {value}")
        
        cursor.close()
        
        print("\n🎉 Configuração concluída com sucesso!")
        print("\n📋 Próximos passos:")
        print("1. Instalar dependências do microserviço de e-mail:")
        print("   cd backend/email-service && npm install")
        print("2. Iniciar o microserviço:")
        print("   npm start")
        print("3. Integrar com o frontend")
        
    except Error as e:
        print(f"❌ Erro durante a configuração: {e}")
        sys.exit(1)
    
    finally:
        if connection.is_connected():
            connection.close()

if __name__ == "__main__":
    setup_email_verification()

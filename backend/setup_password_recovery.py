#!/usr/bin/env python3
"""
Script para configurar o sistema de recuperação de senha no banco de dados
Vibe Social Network - Password Recovery Setup
"""

import mysql.connector
import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def get_db_connection():
    """Estabelece conexão com o banco de dados"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'vibe_user'),
            password=os.getenv('DB_PASSWORD', 'Dashwoodi@1995'),
            database=os.getenv('DB_NAME', 'vibe_social'),
            charset='utf8mb4'
        )
        return connection
    except mysql.connector.Error as err:
        print(f"❌ Erro ao conectar ao banco de dados: {err}")
        return None

def execute_sql_file(connection, filename):
    """Executa um arquivo SQL"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            sql_script = file.read()
        
        cursor = connection.cursor()
        
        # Dividir o script em comandos individuais
        commands = sql_script.split(';')
        
        for command in commands:
            command = command.strip()
            if command and not command.startswith('--'):
                try:
                    cursor.execute(command)
                    connection.commit()
                except mysql.connector.Error as err:
                    # Ignorar erros de "já existe" para procedures e events
                    if "already exists" not in str(err).lower():
                        print(f"⚠️  Aviso ao executar comando: {err}")
        
        cursor.close()
        return True
        
    except FileNotFoundError:
        print(f"❌ Arquivo SQL não encontrado: {filename}")
        return False
    except Exception as err:
        print(f"❌ Erro ao executar arquivo SQL: {err}")
        return False

def verify_setup(connection):
    """Verifica se a configuração foi bem-sucedida"""
    cursor = connection.cursor()
    
    try:
        # Verificar tabelas
        cursor.execute("SHOW TABLES LIKE 'password_recovery%'")
        tables = cursor.fetchall()
        
        print("\n📊 Verificação da instalação:")
        print("="*50)
        
        if len(tables) >= 2:
            print("✅ Tabelas criadas com sucesso:")
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print("❌ Algumas tabelas não foram criadas")
            return False
        
        # Verificar estrutura da tabela principal
        cursor.execute("DESCRIBE password_recovery")
        columns = cursor.fetchall()
        
        expected_columns = [
            'id', 'user_id', 'email', 'recovery_token', 
            'recovery_code', 'expires_at', 'used', 'used_at',
            'attempts', 'created_at', 'updated_at'
        ]
        
        found_columns = [col[0] for col in columns]
        missing_columns = set(expected_columns) - set(found_columns)
        
        if not missing_columns:
            print("✅ Estrutura da tabela password_recovery: OK")
        else:
            print(f"❌ Colunas faltando: {missing_columns}")
            return False
        
        # Verificar procedure
        cursor.execute("SHOW PROCEDURE STATUS WHERE Name = 'CleanExpiredPasswordRecoveryTokens'")
        procedures = cursor.fetchall()
        
        if procedures:
            print("✅ Procedure de limpeza criada: OK")
        else:
            print("⚠️  Procedure de limpeza não encontrada")
        
        # Verificar event
        cursor.execute("SHOW EVENTS WHERE Name = 'CleanPasswordRecoveryTokens'")
        events = cursor.fetchall()
        
        if events:
            print("✅ Event de limpeza automática criado: OK")
        else:
            print("⚠️  Event de limpeza não encontrado")
        
        # Verificar event scheduler
        cursor.execute("SHOW VARIABLES LIKE 'event_scheduler'")
        scheduler = cursor.fetchone()
        
        if scheduler and scheduler[1] == 'ON':
            print("✅ Event Scheduler ativo: OK")
        else:
            print("⚠️  Event Scheduler não está ativo")
        
        print("="*50)
        return True
        
    except mysql.connector.Error as err:
        print(f"❌ Erro na verificação: {err}")
        return False
    finally:
        cursor.close()

def main():
    """Função principal"""
    print("🚀 Configurando Sistema de Recuperação de Senha")
    print("Vibe Social Network - Password Recovery Setup")
    print("="*50)
    
    # Conectar ao banco
    print("📡 Conectando ao banco de dados...")
    connection = get_db_connection()
    
    if not connection:
        print("❌ Falha na conexão. Verifique as configurações do banco.")
        sys.exit(1)
    
    print("✅ Conexão estabelecida com sucesso!")
    
    # Executar script SQL
    print("\n📄 Executando script SQL...")
    sql_file = os.path.join(os.path.dirname(__file__), 'setup_password_recovery.sql')
    
    if execute_sql_file(connection, sql_file):
        print("✅ Script SQL executado com sucesso!")
    else:
        print("❌ Falha ao executar script SQL")
        connection.close()
        sys.exit(1)
    
    # Verificar instalação
    if verify_setup(connection):
        print("\n🎉 Sistema de recuperação de senha configurado com sucesso!")
        print("\n📋 Próximos passos:")
        print("1. Configurar o microserviço de e-mail com alias recuperacao@meuvibe.com")
        print("2. Testar o sistema de recuperação de senha")
        print("3. Monitorar logs em password_recovery_logs")
    else:
        print("\n⚠️  Configuração parcialmente concluída. Verifique os avisos acima.")
    
    connection.close()

if __name__ == "__main__":
    main()

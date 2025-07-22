#!/usr/bin/env python3
"""
Script para corrigir o tamanho da coluna gender na tabela users
Vibe Social Network - Gender Column Fix
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

def fix_gender_column(connection):
    """Corrige a coluna gender para suportar 'prefer_not_to_say'"""
    cursor = connection.cursor()
    
    try:
        # Verificar estrutura atual da coluna
        cursor.execute("DESCRIBE users")
        columns = cursor.fetchall()
        
        gender_column = None
        for col in columns:
            if col[0] == 'gender':
                gender_column = col
                break
        
        if gender_column:
            print(f"📋 Coluna gender atual: {gender_column[1]}")
            
            # Alterar a coluna para ENUM com os valores corretos
            alter_sql = """
            ALTER TABLE users 
            MODIFY COLUMN gender ENUM('male', 'female', 'other', 'prefer_not_to_say') 
            DEFAULT NULL
            """
            
            print("🔧 Alterando coluna gender...")
            cursor.execute(alter_sql)
            connection.commit()
            
            print("✅ Coluna gender alterada com sucesso!")
            
            # Verificar se a alteração foi aplicada
            cursor.execute("DESCRIBE users")
            columns_after = cursor.fetchall()
            
            for col in columns_after:
                if col[0] == 'gender':
                    print(f"✅ Nova definição: {col[1]}")
                    break
                    
        else:
            print("❌ Coluna gender não encontrada")
            return False
            
        return True
        
    except mysql.connector.Error as err:
        print(f"❌ Erro ao alterar coluna: {err}")
        return False
    finally:
        cursor.close()

def main():
    """Função principal"""
    print("🔧 Corrigindo coluna gender na tabela users")
    print("="*50)
    
    # Conectar ao banco
    print("📡 Conectando ao banco de dados...")
    connection = get_db_connection()
    
    if not connection:
        print("❌ Falha na conexão. Verifique as configurações do banco.")
        sys.exit(1)
    
    print("✅ Conexão estabelecida com sucesso!")
    
    # Corrigir coluna
    if fix_gender_column(connection):
        print("\n🎉 Coluna gender corrigida com sucesso!")
        print("📋 Agora suporta os valores:")
        print("   - 'male'")
        print("   - 'female'")
        print("   - 'other'")
        print("   - 'prefer_not_to_say'")
        print("\n✅ O registro de usuários deve funcionar normalmente agora.")
    else:
        print("\n❌ Falha ao corrigir a coluna gender")
        connection.close()
        sys.exit(1)
    
    connection.close()

if __name__ == "__main__":
    main()

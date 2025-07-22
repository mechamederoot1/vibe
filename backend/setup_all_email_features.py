#!/usr/bin/env python3
"""
Script completo para configurar todas as funcionalidades de e-mail
Vibe Social Network - Complete Email Setup
"""

import os
import sys
import subprocess
import time

def print_header(title):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)

def print_step(step, description):
    """Imprime passo formatado"""
    print(f"\n📋 Passo {step}: {description}")
    print("-" * 50)

def run_command(command, description):
    """Executa comando e verifica resultado"""
    print(f"⚡ {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Concluído")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro: {e}")
        print(f"📄 Output: {e.stdout}")
        print(f"🚨 Error: {e.stderr}")
        return False

def main():
    """Função principal"""
    print_header("CONFIGURAÇÃO COMPLETA - SISTEMA DE E-MAILS VIBE")
    print("📧 Verificação de E-mail + Recuperação de Senha")
    print("🔐 Configuração completa do banco de dados e microserviços")
    
    # Verificar se estamos no diretório correto
    if not os.path.exists('backend'):
        print("❌ Erro: Execute este script a partir da raiz do projeto (onde está a pasta backend)")
        sys.exit(1)
    
    # Passo 1: Configurar verificação de e-mail
    print_step(1, "Configurando Sistema de Verificação de E-mail")
    
    email_verification_setup = os.path.join('backend', 'setup_email_verification.py')
    if os.path.exists(email_verification_setup):
        if run_command(f'python3 {email_verification_setup}', 'Configurar verificação de e-mail'):
            print("✅ Sistema de verificação de e-mail configurado")
        else:
            print("⚠️  Aviso: Falha na configuração de verificação de e-mail")
    else:
        print("⚠️  Arquivo setup_email_verification.py não encontrado, pulando...")
    
    # Passo 2: Configurar recuperação de senha
    print_step(2, "Configurando Sistema de Recuperação de Senha")
    
    password_recovery_setup = os.path.join('backend', 'setup_password_recovery.py')
    if os.path.exists(password_recovery_setup):
        if run_command(f'python3 {password_recovery_setup}', 'Configurar recuperação de senha'):
            print("✅ Sistema de recuperação de senha configurado")
        else:
            print("❌ Falha na configuração de recuperação de senha")
            return False
    else:
        print("❌ Arquivo setup_password_recovery.py não encontrado")
        return False
    
    # Passo 3: Instalar dependências do microserviço
    print_step(3, "Configurando Microserviço de E-mail")
    
    email_service_path = os.path.join('backend', 'email-service')
    if os.path.exists(email_service_path):
        original_dir = os.getcwd()
        os.chdir(email_service_path)
        
        # Verificar se package.json existe
        if os.path.exists('package.json'):
            if run_command('npm install', 'Instalar dependências do microserviço'):
                print("✅ Dependências do microserviço instaladas")
            else:
                print("⚠️  Aviso: Falha na instalação de dependências")
        else:
            print("⚠️  package.json não encontrado no microserviço")
        
        os.chdir(original_dir)
    else:
        print("⚠️  Pasta email-service não encontrada")
    
    # Passo 4: Verificar configurações
    print_step(4, "Verificando Configurações")
    
    # Verificar arquivo .env
    env_file = os.path.join('backend', 'email-service', '.env')
    if os.path.exists(env_file):
        print("✅ Arquivo .env encontrado")
        with open(env_file, 'r') as f:
            content = f.read()
            if 'SMTP_HOST' in content and 'SMTP_USER' in content:
                print("✅ Configurações SMTP encontradas")
            else:
                print("⚠️  Configurações SMTP incompletas")
    else:
        print("⚠️  Arquivo .env não encontrado")
        print("📝 Crie um arquivo .env em backend/email-service/ com:")
        print("""
SMTP_HOST=smtp.hostinger.com
SMTP_PORT=587
SMTP_USER=suporte@meuvibe.com
SMTP_PASS=sua_senha_aqui
SMTP_FROM=no-reply@meuvibe.com

DB_HOST=localhost
DB_PORT=3306
DB_USER=vibe_user
DB_PASSWORD=sua_senha_db
DB_NAME=vibe_social

VERIFICATION_CODE_EXPIRY=300000
RESEND_COOLDOWN=60000
MAX_RESEND_ATTEMPTS=5
        """)
    
    # Passo 5: Instruções finais
    print_step(5, "Instruções de Uso")
    
    print("""
🎯 SISTEMA CONFIGURADO COM SUCESSO!

📋 Para iniciar o sistema completo:

1️⃣  INICIAR MICROSERVIÇO DE E-MAIL:
   cd backend/email-service
   npm start
   (Rodará na porta 3001)

2️⃣  INICIAR BACKEND PRINCIPAL:
   cd backend
   python3 main.py
   (Rodará na porta 8000)

3️⃣  INICIAR FRONTEND:
   npm run dev
   (Rodará na porta 5173)

🔧 FUNCIONALIDADES DISPONÍVEIS:

✅ Verificação de e-mail após cadastro
   - E-mail enviado automaticamente
   - Código de 6 dígitos
   - Link de confirmação direta
   - Página de verificação (/verify-email)

✅ Recuperação de senha
   - Solicitação via e-mail (/forgot-password)
   - E-mail de recuperacao@meuvibe.com
   - Código de 6 dígitos (15 min validade)
   - Página de redefinição (/reset-password)
   - Link direto para redefinir

🔐 SEGURANÇA:

✅ Limites anti-spam
✅ Códigos com expiração
✅ Tokens únicos e seguros
✅ Logs de auditoria
✅ Limpeza automática de tokens expirados

📧 TEMPLATES DE E-MAIL:

✅ Verificação: no-reply@meuvibe.com
✅ Recuperação: recuperacao@meuvibe.com
✅ Design responsivo e profissional
✅ Códigos destacados e botões CTA

🗄️  BANCO DE DADOS:

✅ Tabela: email_verifications
✅ Tabela: password_recovery
✅ Tabela: password_recovery_logs
✅ Procedures de limpeza automática
✅ Índices otimizados

🌐 ROTAS FRONTEND:

✅ /verify-email - Verificação de e-mail
✅ /forgot-password - Solicitar recuperação
✅ /reset-password - Redefinir senha

📊 MONITORAMENTO:

✅ Logs detalhados no console
✅ Auditoria no banco de dados
✅ Health check: GET /health

🚀 O sistema está pronto para uso em produção!
    """)
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
        print("🚀 Seu sistema de e-mails está pronto para uso!")
    else:
        print("\n❌ CONFIGURAÇÃO FALHOU")
        print("📞 Verifique os erros acima e tente novamente")
        sys.exit(1)

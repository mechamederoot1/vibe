#!/usr/bin/env python3
"""
Script de inicialização completa do sistema Vibe
Configura banco de dados, inicia microserviços e backend principal
"""

import os
import sys
import subprocess
import time
import threading
import signal
from pathlib import Path

def print_banner():
    """Exibir banner do sistema"""
    print("""
    ╔══════════════════════════════════════╗
    ║          🌟 VIBE SYSTEM 🌟          ║
    ║     Sistema de Verificação Email     ║
    ╚══════════════════════════════════════╝
    """)

def check_requirements():
    """Verificar dependências necessárias"""
    print("🔍 Verificando dependências...")
    
    # Verificar Python
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8+ é necessário")
        return False
    
    # Verificar Node.js
    try:
        node_result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if node_result.returncode == 0:
            print(f"✅ Node.js: {node_result.stdout.strip()}")
        else:
            print("❌ Node.js não encontrado")
            return False
    except FileNotFoundError:
        print("❌ Node.js não encontrado")
        return False
    
    # Verificar npm
    try:
        npm_result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if npm_result.returncode == 0:
            print(f"✅ npm: {npm_result.stdout.strip()}")
        else:
            print("❌ npm não encontrado")
            return False
    except FileNotFoundError:
        print("❌ npm não encontrado")
        return False
    
    return True

def setup_database():
    """Configurar banco de dados"""
    print("\n📊 Configurando banco de dados...")
    
    try:
        result = subprocess.run([
            sys.executable, 'setup_email_verification.py'
        ], cwd='backend', capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Banco de dados configurado com sucesso")
            print(result.stdout)
        else:
            print("❌ Erro ao configurar banco de dados:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Erro ao executar configuração do banco: {e}")
        return False
    
    return True

def install_email_service_deps():
    """Instalar dependências do microserviço de e-mail"""
    print("\n📦 Instalando dependências do microserviço de e-mail...")
    
    email_service_dir = Path('backend/email-service')
    if not email_service_dir.exists():
        print("❌ Diretório do microserviço não encontrado")
        return False
    
    try:
        result = subprocess.run(['npm', 'install'], cwd=email_service_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependências instaladas com sucesso")
        else:
            print("❌ Erro ao instalar dependências:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False
    
    return True

def install_backend_deps():
    """Instalar dependências do backend principal"""
    print("\n🐍 Instalando dependências do backend principal...")
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], cwd='backend', capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependências do backend instaladas")
        else:
            print("❌ Erro ao instalar dependências do backend:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Erro ao instalar dependências do backend: {e}")
        return False
    
    return True

def start_email_service():
    """Iniciar microserviço de e-mail"""
    print("\n📧 Iniciando microserviço de e-mail...")
    
    email_service_dir = Path('backend/email-service')
    
    try:
        process = subprocess.Popen(
            ['npm', 'start'],
            cwd=email_service_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Aguardar alguns segundos para verificar se iniciou
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ Microserviço de e-mail iniciado (PID: {})".format(process.pid))
            return process
        else:
            stdout, stderr = process.communicate()
            print("❌ Erro ao iniciar microserviço:")
            print(stderr)
            return None
    except Exception as e:
        print(f"❌ Erro ao iniciar microserviço: {e}")
        return None

def start_backend():
    """Iniciar backend principal"""
    print("\n🚀 Iniciando backend principal...")
    
    try:
        process = subprocess.Popen(
            [sys.executable, 'main.py'],
            cwd='backend',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Aguardar alguns segundos para verificar se iniciou
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ Backend principal iniciado (PID: {})".format(process.pid))
            return process
        else:
            stdout, stderr = process.communicate()
            print("❌ Erro ao iniciar backend:")
            print(stderr)
            return None
    except Exception as e:
        print(f"❌ Erro ao iniciar backend: {e}")
        return None

def start_frontend():
    """Iniciar frontend"""
    print("\n🌐 Iniciando frontend...")
    
    try:
        process = subprocess.Popen(
            ['npm', 'run', 'dev'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Aguardar alguns segundos para verificar se iniciou
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ Frontend iniciado (PID: {})".format(process.pid))
            return process
        else:
            stdout, stderr = process.communicate()
            print("❌ Erro ao iniciar frontend:")
            print(stderr)
            return None
    except Exception as e:
        print(f"❌ Erro ao iniciar frontend: {e}")
        return None

def show_status():
    """Mostrar status dos serviços"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║                    🎉 SISTEMA INICIADO! 🎉                ║
    ╠════════════════════════════════════════════════════════════╣
    ║  📧 Microserviço Email:  http://localhost:3001            ║
    ║  🚀 Backend API:         http://localhost:8000            ║
    ║  🌐 Frontend:            http://localhost:5173            ║
    ╠════════════════════════════════════════════════════════════╣
    ║  📋 Funcionalidades:                                       ║
    ║    ✅ Registro com verificação de e-mail                  ║
    ║    ✅ Códigos de 6 dígitos com expiração                  ║
    ║    ✅ Limitação de reenvio (1 min cooldown)               ║
    ║    ✅ Verificação via link no e-mail                      ║
    ║    ✅ Template HTML responsivo                             ║
    ╚════════════════════════════════════════════════════════════╝
    
    💡 Pressione Ctrl+C para parar todos os serviços
    """)

def signal_handler(signum, frame):
    """Handler para sinais de parada"""
    print("\n🛑 Parando todos os serviços...")
    sys.exit(0)

def main():
    """Função principal"""
    print_banner()
    
    # Registrar handler de sinal
    signal.signal(signal.SIGINT, signal_handler)
    
    # Verificar dependências
    if not check_requirements():
        print("\n❌ Falha na verificação de dependências")
        sys.exit(1)
    
    # Configurar banco de dados
    if not setup_database():
        print("\n❌ Falha na configuração do banco de dados")
        sys.exit(1)
    
    # Instalar dependências
    if not install_backend_deps():
        print("\n❌ Falha na instalação das dependências do backend")
        sys.exit(1)
    
    if not install_email_service_deps():
        print("\n❌ Falha na instalação das dependências do microserviço")
        sys.exit(1)
    
    # Iniciar serviços
    processes = []
    
    # Microserviço de e-mail
    email_process = start_email_service()
    if email_process:
        processes.append(email_process)
    else:
        print("\n❌ Falha ao iniciar microserviço de e-mail")
        sys.exit(1)
    
    # Backend principal
    backend_process = start_backend()
    if backend_process:
        processes.append(backend_process)
    else:
        print("\n❌ Falha ao iniciar backend principal")
        # Terminar microserviço se backend falhar
        email_process.terminate()
        sys.exit(1)
    
    # Frontend (opcional - pode estar rodando separadamente)
    frontend_process = start_frontend()
    if frontend_process:
        processes.append(frontend_process)
    
    # Mostrar status
    show_status()
    
    # Aguardar interrupção
    try:
        while True:
            time.sleep(1)
            
            # Verificar se algum processo morreu
            for process in processes[:]:
                if process.poll() is not None:
                    print(f"⚠️ Processo {process.pid} foi finalizado")
                    processes.remove(process)
    
    except KeyboardInterrupt:
        pass
    finally:
        # Terminar todos os processos
        print("\n🔄 Finalizando processos...")
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        
        print("✅ Todos os serviços foram finalizados")

if __name__ == "__main__":
    main()

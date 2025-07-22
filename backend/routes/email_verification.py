"""
Rotas de verificação de e-mail
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from datetime import datetime, timedelta
import random
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

from core.database import get_db, Base
from core.security import get_current_user
from models import User
from schemas import UserResponse

router = APIRouter(prefix="/email-verification", tags=["email-verification"])

# Modelo para verificações de e-mail
class EmailVerification(Base):
    __tablename__ = "email_verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    email = Column(String(255), nullable=False)
    verification_code = Column(String(6), nullable=False)
    verification_token = Column(String(64), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    verified = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True)
    attempts = Column(Integer, default=1)

def generate_verification_code():
    """Gera código de 6 dígitos"""
    return str(random.randint(100000, 999999))

def generate_verification_token():
    """Gera token de verificação"""
    return secrets.token_hex(32)

def create_email_template(first_name: str, code: str, token: str):
    """Cria template do e-mail de verificação"""
    base_url = "http://localhost:5173"
    verification_url = f"{base_url}/verify-email?token={token}"
    
    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Confirme seu e-mail - Vibe</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f7f7f7;
            }}
            .container {{
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .logo {{
                font-size: 32px;
                font-weight: bold;
                color: #6366f1;
                margin-bottom: 10px;
            }}
            .title {{
                font-size: 24px;
                margin-bottom: 20px;
                color: #1f2937;
            }}
            .code-container {{
                background: #f8fafc;
                border: 2px dashed #e2e8f0;
                border-radius: 8px;
                padding: 20px;
                text-align: center;
                margin: 20px 0;
            }}
            .verification-code {{
                font-size: 32px;
                font-weight: bold;
                color: #6366f1;
                letter-spacing: 4px;
                margin: 10px 0;
            }}
            .button {{
                display: inline-block;
                background: #6366f1;
                color: white;
                padding: 15px 30px;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 500;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">Vibe</div>
                <h1 class="title">Confirme seu e-mail</h1>
            </div>
            
            <p>Olá <strong>{first_name}</strong>,</p>
            
            <p>Bem-vindo ao Vibe! Para concluir seu cadastro, você precisa confirmar seu endereço de e-mail.</p>
            
            <div class="code-container">
                <p><strong>Seu código de verificação:</strong></p>
                <div class="verification-code">{code}</div>
                <p style="font-size: 14px; color: #6b7280;">Este código expira em 5 minutos</p>
            </div>
            
            <p style="text-align: center;">
                <strong>Ou clique no botão abaixo para confirmar automaticamente:</strong>
            </p>
            
            <div style="text-align: center;">
                <a href="{verification_url}" class="button">
                    ✓ Confirmar E-mail
                </a>
            </div>
            
            <p style="font-size: 14px; color: #6b7280; text-align: center; margin-top: 30px;">
                Este e-mail foi enviado para confirmar seu cadastro no Vibe.<br>
                &copy; 2024 Vibe. Todos os direitos reservados.
            </p>
        </div>
    </body>
    </html>
    """

@router.post("/send-verification")
async def send_verification_email(
    email: str,
    first_name: str,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Enviar e-mail de verificação"""
    try:
        # Verificar limite de tentativas (anti-spam)
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_attempts = db.query(EmailVerification).filter(
            EmailVerification.user_id == user_id,
            EmailVerification.created_at > one_hour_ago
        ).count()

        if recent_attempts >= 5:
            raise HTTPException(
                status_code=429,
                detail="Muitas tentativas. Tente novamente em 1 hora."
            )

        # Verificar cooldown (1 minuto)
        one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
        recent_attempt = db.query(EmailVerification).filter(
            EmailVerification.user_id == user_id,
            EmailVerification.created_at > one_minute_ago
        ).first()

        if recent_attempt:
            remaining_time = 60 - int((datetime.utcnow() - recent_attempt.created_at).total_seconds())
            if remaining_time > 0:
                raise HTTPException(
                    status_code=429,
                    detail=f"Aguarde {remaining_time} segundos antes de solicitar um novo código"
                )

        # Gerar código e token
        verification_code = generate_verification_code()
        verification_token = generate_verification_token()
        expires_at = datetime.utcnow() + timedelta(minutes=5)

        # Salvar no banco
        db_verification = EmailVerification(
            user_id=user_id,
            email=email,
            verification_code=verification_code,
            verification_token=verification_token,
            expires_at=expires_at
        )
        db.add(db_verification)
        db.commit()

        # Simular envio de e-mail (em produção, configure SMTP real)
        print(f"📧 E-mail de verificação para {email}")
        print(f"   Código: {verification_code}")
        print(f"   Token: {verification_token}")
        
        return {
            "success": True,
            "message": "E-mail de verificação enviado com sucesso",
            "expires_in": 300000,  # 5 minutos
            "cooldown_ms": 60000   # 1 minuto
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar e-mail: {str(e)}")

@router.post("/verify-code")
async def verify_code(
    user_id: int,
    code: str,
    db: Session = Depends(get_db)
):
    """Verificar código de 6 dígitos"""
    try:
        # Buscar código válido
        verification = db.query(EmailVerification).filter(
            EmailVerification.user_id == user_id,
            EmailVerification.verification_code == code,
            EmailVerification.verified == False,
            EmailVerification.expires_at > datetime.utcnow()
        ).first()

        if not verification:
            raise HTTPException(
                status_code=400,
                detail="Código inválido ou expirado"
            )

        # Marcar como verificado
        verification.verified = True
        verification.verified_at = datetime.utcnow()

        # Atualizar usuário como verificado
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_verified = True

        db.commit()

        return {
            "success": True,
            "message": "E-mail verificado com sucesso!"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao verificar código: {str(e)}")

@router.post("/verify-token")
async def verify_token(
    token: str,
    db: Session = Depends(get_db)
):
    """Verificar token do link do e-mail"""
    try:
        # Buscar token válido
        verification = db.query(EmailVerification).filter(
            EmailVerification.verification_token == token,
            EmailVerification.verified == False,
            EmailVerification.expires_at > datetime.utcnow()
        ).first()

        if not verification:
            raise HTTPException(
                status_code=400,
                detail="Token inválido ou expirado"
            )

        # Marcar como verificado
        verification.verified = True
        verification.verified_at = datetime.utcnow()

        # Atualizar usuário como verificado
        user = db.query(User).filter(User.id == verification.user_id).first()
        if user:
            user.is_verified = True

        db.commit()

        return {
            "success": True,
            "message": "E-mail verificado com sucesso!",
            "user_id": verification.user_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao verificar token: {str(e)}")

@router.get("/verification-status/{user_id}")
async def get_verification_status(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Verificar status de verificação do usuário"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        return {
            "success": True,
            "verified": user.is_verified or False
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao verificar status: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check do serviço de e-mail"""
    return {
        "status": "OK",
        "service": "Email Verification Service",
        "timestamp": datetime.utcnow().isoformat()
    }

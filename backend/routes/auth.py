"""
Rotas de autenticação
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from datetime import timedelta

from core.database import get_db
from core.security import hash_password, verify_password, create_access_token, get_current_user
from core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from models import User
from schemas import LoginRequest, Token, UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Verifica se o usuário já existe
        db_user = db.query(User).filter(User.email == user.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Cria novo usuário
        hashed_password = hash_password(user.password)

        # Converte birth_date string para objeto date
        birth_date_obj = user.get_birth_date_as_date() if user.birth_date else None

        db_user = User(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            password_hash=hashed_password,
            gender=user.gender,
            birth_date=birth_date_obj,
            phone=user.phone,
            is_active=True,
            is_verified=False  # Explicitly set as not verified
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Send verification email automatically using sync helper
        try:
            from .email_verification import create_verification_record
            verification_success = create_verification_record(
                user_id=db_user.id,
                email=db_user.email,
                first_name=db_user.first_name,
                db=db
            )

            if verification_success:
                print(f"📧 Verification email record created for {db_user.email}")
            else:
                print(f"⚠️ Could not create verification record for {db_user.email}")

        except Exception as email_error:
            print(f"⚠️ Failed to create verification email: {email_error}")
            # Don't fail registration if email sending fails
            pass

        return db_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == login_data.email).first()
        
        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/check-email")
def check_email_exists(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    return {"exists": user is not None}

@router.get("/check-username")
def check_username_exists(username: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.username == username,
        User.id != current_user.id  # Exclude current user
    ).first()
    return {"exists": user is not None}

@router.get("/check-username-public")
def check_username_exists_public(username: str, db: Session = Depends(get_db)):
    """Public route to check username availability during registration"""
    user = db.query(User).filter(User.username == username).first()
    return {"exists": user is not None}

@router.get("/verify-token")
async def verify_token(current_user: User = Depends(get_current_user)):
    return {"valid": True, "user": current_user}

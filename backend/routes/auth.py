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
        print(f"🔍 Registration attempt for email: {user.email}")

        # Validate required fields
        if not user.first_name or not user.first_name.strip():
            raise HTTPException(status_code=400, detail="Nome é obrigatório")
        if not user.last_name or not user.last_name.strip():
            raise HTTPException(status_code=400, detail="Sobrenome é obrigatório")
        if not user.email or not user.email.strip():
            raise HTTPException(status_code=400, detail="E-mail é obrigatório")
        if not user.password or len(user.password) < 6:
            raise HTTPException(status_code=400, detail="Senha deve ter pelo menos 6 caracteres")

        print(f"✅ Required fields validated")

        # Verifica se o usuário já existe
        db_user = db.query(User).filter(User.email == user.email).first()
        if db_user:
            print(f"❌ Email already registered: {user.email}")
            raise HTTPException(status_code=400, detail="Email already registered")

        print(f"✅ Email available: {user.email}")

        # Cria novo usuário
        try:
            hashed_password = hash_password(user.password)
            print(f"✅ Password hashed successfully")
        except Exception as hash_error:
            print(f"❌ Password hashing failed: {hash_error}")
            raise Exception(f"Password hashing error: {hash_error}")

        # Converte birth_date string para objeto date
        try:
            birth_date_obj = user.get_birth_date_as_date() if user.birth_date else None
            print(f"✅ Birth date processed: {birth_date_obj}")
        except Exception as date_error:
            print(f"❌ Birth date conversion failed: {date_error}")
            birth_date_obj = None

        print(f"🔍 Creating user with data:")
        print(f"   Name: {user.first_name} {user.last_name}")
        print(f"   Email: {user.email}")
        print(f"   Gender: {user.gender}")
        print(f"   Birth date: {birth_date_obj}")
        print(f"   Phone: {user.phone}")

        try:
            # Start with minimal required fields only
            db_user = User(
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                password_hash=hashed_password
            )

            # Add optional fields if they exist
            if user.gender:
                db_user.gender = user.gender
            if birth_date_obj:
                db_user.birth_date = birth_date_obj
            if user.phone:
                db_user.phone = user.phone

            print(f"✅ User object created with required fields")
        except Exception as user_creation_error:
            print(f"❌ User object creation failed: {user_creation_error}")
            raise Exception(f"User creation error: {user_creation_error}")

        try:
            db.add(db_user)
            print(f"✅ User added to session")
        except Exception as add_error:
            print(f"❌ Failed to add user to session: {add_error}")
            raise Exception(f"Session add error: {add_error}")

        try:
            db.commit()
            print(f"✅ Database commit successful")
        except Exception as commit_error:
            print(f"❌ Database commit failed: {commit_error}")
            raise Exception(f"Database commit error: {commit_error}")

        try:
            db.refresh(db_user)
            print(f"✅ User refreshed from database")
        except Exception as refresh_error:
            print(f"❌ Failed to refresh user: {refresh_error}")
            raise Exception(f"Refresh error: {refresh_error}")

        # TODO: Re-enable email verification after fixing database issues
        print(f"✅ User {db_user.id} created successfully: {db_user.email}")
        print(f"🔍 Debug - User verification status: {db_user.is_verified}")

        # Send verification email automatically using sync helper
        # try:
        #     from .email_verification import create_verification_record
        #     verification_success = create_verification_record(
        #         user_id=db_user.id,
        #         email=db_user.email,
        #         first_name=db_user.first_name,
        #         db=db
        #     )
        #
        #     if verification_success:
        #         print(f"📧 Verification email record created for {db_user.email}")
        #     else:
        #         print(f"⚠️ Could not create verification record for {db_user.email}")
        #
        # except Exception as email_error:
        #     print(f"⚠️ Failed to create verification email: {email_error}")
        #     # Don't fail registration if email sending fails
        #     pass

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

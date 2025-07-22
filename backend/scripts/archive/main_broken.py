from fastapi import FastAPI, HTTPException, Depends, status, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Date
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session, relationship
from datetime import datetime, timedelta, date
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, EmailStr
import os
from dotenv import load_dotenv
import json
import asyncio
from pathlib import Path

# Carrega variáveis de ambiente
load_dotenv()

# Configurações
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    gender = Column(String(10))
    birth_date = Column(Date)
    phone = Column(String(20))

    # Profile fields
    username = Column(String(50), unique=True, index=True)
    nickname = Column(String(50))
    bio = Column(Text)
    avatar = Column(String(500))
    cover_photo = Column(String(500))
    location = Column(String(100))
    website = Column(String(200))
    relationship_status = Column(String(20))  # single, in_relationship, married, etc
    work = Column(String(100))
    education = Column(String(100))

    # Privacy settings
    profile_visibility = Column(String(20), default="public")  # public, friends, private
    friend_request_privacy = Column(String(20), default="everyone")  # everyone, friends_of_friends, none
    post_visibility = Column(String(20), default="public")  # public, friends, private
    story_visibility = Column(String(20), default="public")  # public, friends, private
    email_visibility = Column(String(20), default="private")  # public, friends, private
    phone_visibility = Column(String(20), default="private")  # public, friends, private
    birth_date_visibility = Column(String(20), default="friends")  # public, friends, private

    # Notification settings
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    friend_request_notifications = Column(Boolean, default=True)
    comment_notifications = Column(Boolean, default=True)
    reaction_notifications = Column(Boolean, default=True)
    message_notifications = Column(Boolean, default=True)
    story_notifications = Column(Boolean, default=True)

    # Account settings
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    account_deactivated = Column(Boolean, default=False)
    deactivated_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    post_type = Column(String(20), default="post")
    media_type = Column(String(50))
    media_url = Column(String(500))
    media_metadata = Column(Text)
    privacy = Column(String(20), default="public")  # public, friends, private
    created_at = Column(DateTime, default=datetime.utcnow)
    reactions_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    
    author = relationship("User", backref="posts")

class Story(Base):
    __tablename__ = "stories"
    
    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text)
    media_type = Column(String(50))
    media_url = Column(String(500))
    background_color = Column(String(7))
    duration_hours = Column(Integer, default=24)
    max_duration_seconds = Column(Integer, default=25)  # Para vídeos
    archived = Column(Boolean, default=False)
    archived_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    views_count = Column(Integer, default=0)
    
    author = relationship("User", backref="stories")

class StoryView(Base):
    __tablename__ = "story_views"
    
    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False)
    viewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    viewed_at = Column(DateTime, default=datetime.utcnow)
    
    story = relationship("Story", backref="views")
    viewer = relationship("User", backref="story_views")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"))
    notification_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(Text)  # JSON data
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    recipient = relationship("User", foreign_keys=[recipient_id], backref="received_notifications")
    sender = relationship("User", foreign_keys=[sender_id], backref="sent_notifications")

class Friendship(Base):
    __tablename__ = "friendships"
    
    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    addressee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), default="pending")  # pending, accepted, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    requester = relationship("User", foreign_keys=[requester_id])
    addressee = relationship("User", foreign_keys=[addressee_id])

class Reaction(Base):
    __tablename__ = "reactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    reaction_type = Column(String(20), nullable=False)  # like, love, haha, wow, sad, angry, care, pride, grateful, celebrating
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", backref="reactions")
    post = relationship("Post", backref="reactions")

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    author = relationship("User", backref="comments")
    post = relationship("Post", backref="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")

class Share(Base):
    __tablename__ = "shares"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", backref="shares")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text)
    message_type = Column(String(20), default="text")  # text, image, video, audio, file
    media_url = Column(String(500))
    media_metadata = Column(Text)  # JSON metadata
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    sender = relationship("User", foreign_keys=[sender_id], backref="sent_messages")
    recipient = relationship("User", foreign_keys=[recipient_id], backref="received_messages")

class MediaFile(Base):
    __tablename__ = "media_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255))
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    file_type = Column(String(20))  # image, video, audio, document
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)

    uploader = relationship("User", backref="uploaded_files")

class Block(Base):
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True, index=True)
    blocker_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    blocked_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    blocker = relationship("User", foreign_keys=[blocker_id], backref="blocking")
    blocked = relationship("User", foreign_keys=[blocked_id], backref="blocked_by")

class Follow(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    followed_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    follower = relationship("User", foreign_keys=[follower_id], backref="following")
    followed = relationship("User", foreign_keys=[followed_id], backref="followers")

class StoryTag(Base):
    __tablename__ = "story_tags"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False)
    tagged_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    position_x = Column(Integer, default=50)  # Posição X em percentual (0-100)
    position_y = Column(Integer, default=50)  # Posição Y em percentual (0-100)
    created_at = Column(DateTime, default=datetime.utcnow)

    story = relationship("Story", backref="tags")
    tagged_user = relationship("User", backref="story_tags")

class StoryOverlay(Base):
    __tablename__ = "story_overlays"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False)
    overlay_type = Column(String(20), nullable=False)  # text, emoji, sticker, drawing
    content = Column(Text)  # Texto ou dados do overlay
    position_x = Column(Integer, default=50)  # Posição X em percentual
    position_y = Column(Integer, default=50)  # Posição Y em percentual
    rotation = Column(Integer, default=0)  # Rotação em graus
    scale = Column(Integer, default=100)  # Escala em percentual
    color = Column(String(7))  # Cor em hex
    font_family = Column(String(50))  # Família da fonte
    font_size = Column(Integer, default=16)  # Tamanho da fonte
    created_at = Column(DateTime, default=datetime.utcnow)

    story = relationship("Story", backref="overlays")

# Pydantic models
class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    phone: Optional[str] = None
    username: Optional[str] = None
    nickname: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None
    cover_photo: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    relationship_status: Optional[str] = None
    work: Optional[str] = None
    education: Optional[str] = None

class UserCreate(UserBase):
    password: str

        def get_birth_date_as_date(self) -> Optional[date]:
        """Converte birth_date string para objeto date"""
                if self.birth_date:
            try:
                # Assume formato YYYY-MM-DD
                year, month, day = map(int, self.birth_date.split('-'))
                return date(year, month, day)
            except (ValueError, AttributeError):
                return None
        return None

class UserResponse(UserBase):
    id: int
    birth_date: Optional[Union[str, date]] = None
    is_active: bool
    created_at: datetime
    last_seen: datetime
    
        class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat() if v else None
        }

class ReactionCreate(BaseModel):
    post_id: int
    reaction_type: str

class CommentCreate(BaseModel):
    content: str
    post_id: int
    parent_id: Optional[int] = None

class CommentResponse(BaseModel):
    id: int
    content: str
    author: Dict[str, Any]
    created_at: datetime
    reactions_count: int = 0
    replies: List['CommentResponse'] = []
    
    class Config:
        from_attributes = True

class ShareCreate(BaseModel):
    post_id: int

class FriendshipCreate(BaseModel):
    addressee_id: int

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    email: str
    password: str

class PostCreate(BaseModel):
    content: str
    post_type: str = "post"
    media_type: Optional[str] = None
    media_url: Optional[str] = None
    media_metadata: Optional[str] = None
    privacy: str = "public"  # public, friends, private

class PostResponse(BaseModel):
    id: int
    author: Dict[str, Any]
    content: str
    post_type: str
    media_type: Optional[str] = None
    media_url: Optional[str] = None
    created_at: datetime
    reactions_count: int
    comments_count: int
    shares_count: int
    
    class Config:
        from_attributes = True

class StoryCreate(BaseModel):
    content: Optional[str] = None
    media_type: Optional[str] = None
    media_url: Optional[str] = None
    background_color: Optional[str] = None
    duration_hours: int = 24
    max_duration_seconds: int = 25  # Para vídeos
    archived: bool = False

class StoryResponse(BaseModel):
    id: int
    author: Dict[str, Any]
    content: Optional[str] = None
    media_type: Optional[str] = None
    media_url: Optional[str] = None
    background_color: Optional[str] = None
    created_at: datetime
    expires_at: datetime
    views_count: int
    
    class Config:
        from_attributes = True

class NotificationResponse(BaseModel):
    id: int
    notification_type: str
    title: str
    message: str
    data: Optional[str] = None
    is_read: bool
    created_at: datetime
    sender: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# New Pydantic models for enhanced features
class MessageCreate(BaseModel):
    recipient_id: int
    content: Optional[str] = None
    message_type: str = "text"  # text, image, video, audio, file
    media_url: Optional[str] = None
    media_metadata: Optional[str] = None

class MessageResponse(BaseModel):
    id: int
    sender: Dict[str, Any]
    recipient: Dict[str, Any]
    content: Optional[str]
    message_type: str
    media_url: Optional[str]
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    nickname: Optional[str] = None
    bio: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    cover_photo: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    relationship_status: Optional[str] = None
    work: Optional[str] = None
    education: Optional[str] = None

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

class PrivacySettings(BaseModel):
    profile_visibility: Optional[str] = None
    friend_request_privacy: Optional[str] = None
    post_visibility: Optional[str] = None
    story_visibility: Optional[str] = None
    email_visibility: Optional[str] = None
    phone_visibility: Optional[str] = None
    birth_date_visibility: Optional[str] = None

class NotificationSettings(BaseModel):
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    friend_request_notifications: Optional[bool] = None
    comment_notifications: Optional[bool] = None
    reaction_notifications: Optional[bool] = None
    message_notifications: Optional[bool] = None
    story_notifications: Optional[bool] = None

class BlockCreate(BaseModel):
    blocked_id: int

class FollowCreate(BaseModel):
    followed_id: int

class MediaUploadResponse(BaseModel):
    id: int
    filename: str
    file_path: str
    file_type: str
    file_size: int
    mime_type: str
    upload_date: datetime

    class Config:
        from_attributes = True

class StoryTagCreate(BaseModel):
    story_id: int
    tagged_user_id: int
    position_x: int = 50
    position_y: int = 50

class StoryOverlayCreate(BaseModel):
    story_id: int
    overlay_type: str  # text, emoji, sticker, drawing
    content: str
    position_x: int = 50
    position_y: int = 50
    rotation: int = 0
    scale: int = 100
    color: Optional[str] = None
    font_family: Optional[str] = None
    font_size: int = 16

class StoryWithEditor(BaseModel):
    """Story com editor mobile - incluindo tags e overlays"""
    content: Optional[str] = None
    media_type: Optional[str] = None
    media_url: Optional[str] = None
    background_color: Optional[str] = None
    duration_hours: int = 24
    max_duration_seconds: int = 25
    tags: List[StoryTagCreate] = []
    overlays: List[StoryOverlayCreate] = []

# Utility functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Get current user
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
    )
    try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    except JWTError:
    raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
    raise credentials_exception
    return user

# WebSocket Manager
class ConnectionManager:
    def __init__(self):
    self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
    await websocket.accept()
    if user_id not in self.active_connections:
        self.active_connections[user_id] = []
    self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
    if user_id in self.active_connections:
        if websocket in self.active_connections[user_id]:
            self.active_connections[user_id].remove(websocket)
        if not self.active_connections[user_id]:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: int):
    if user_id in self.active_connections:
        for connection in self.active_connections[user_id]:
            try:
                await connection.send_text(message)
            except:
                self.active_connections[user_id].remove(connection)

    async def send_notification(self, user_id: int, notification: dict):
    message = json.dumps({
        "type": "notification",
        **notification
    })
    await self.send_personal_message(message, user_id)

    async def send_message(self, user_id: int, message_data: dict):
    """Enviar mensagem em tempo real"""
    message = json.dumps({
        "type": "message",
        **message_data
    })
    await self.send_personal_message(message, user_id)

    async def send_typing_indicator(self, user_id: int, typing_data: dict):
    """Enviar indicador de digitação"""
    message = json.dumps({
        "type": "typing",
        **typing_data
    })
    await self.send_personal_message(message, user_id)

    async def send_message_read(self, user_id: int, read_data: dict):
    """Notificar que mensagem foi lida"""
    message = json.dumps({
        "type": "message_read",
        **read_data
    })
    await self.send_personal_message(message, user_id)

manager = ConnectionManager()

def verify_websocket_token(token: str):
    try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    email: str = payload.get("sub")
    if email is None:
        return None
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        return user
    finally:
        db.close()
    except JWTError:
    return None

# FastAPI app
app = FastAPI(title="Backend API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth routes
@app.post("/auth/register", response_model=UserResponse)
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
        created_at=datetime.utcnow(),
        last_seen=datetime.utcnow()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user
    except Exception as e:
    print(f"Erro no registro: {e}")
    db.rollback()
    raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@app.post("/auth/login", response_model=Token)
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
    print(f"Erro no login: {e}")
    raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/auth/check-email")
def check_email_exists(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    return {"exists": user is not None}

@app.get("/auth/check-username")
def check_username_exists(username: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(
    User.username == username,
    User.id != current_user.id  # Exclude current user
    ).first()
    return {"exists": user is not None}

@app.get("/auth/check-username-public")
def check_username_exists_public(username: str, db: Session = Depends(get_db)):
    """Public route to check username availability during registration"""
    user = db.query(User).filter(User.username == username).first()
    return {"exists": user is not None}

@app.get("/auth/verify-token")
async def verify_token(current_user: User = Depends(get_current_user)):
    return {"valid": True, "user": current_user}

# Posts routes
@app.post("/posts/", response_model=PostResponse)
async def create_post(post: PostCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Validação e processamento do conteúdo
    content_to_save = post.content
    
    # Se for um depoimento, validamos se é JSON válido
    if post.post_type == "testimonial" and post.content:
    try:
        # Tenta fazer parse para validar se é JSON válido
        parsed_content = json.loads(post.content)
        
        # Verifica se tem a estrutura esperada
        if isinstance(parsed_content, dict) and 'content' in parsed_content and 'styles' in parsed_content:
            content_to_save = post.content
            print(f"✅ Depoimento JSON válido salvo: {parsed_content.get('content', '')[:50]}...")
        else:
            # Se não tem a estrutura esperada, trata como texto simples
            content_to_save = post.content
            print(f"⚠️ Estrutura JSON inválida, salvando como texto: {post.content[:50]}...")
    except (json.JSONDecodeError, TypeError) as e:
        # Se não for JSON válido, salva como texto simples
        content_to_save = post.content
        print(f"⚠️ JSON inválido, salvando como texto: {str(e)}")
    
    db_post = Post(
    author_id=current_user.id,
    content=content_to_save,
    post_type=post.post_type,
    media_type=post.media_type,
    media_url=post.media_url,
    media_metadata=post.media_metadata,
    privacy=post.privacy
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    return PostResponse(
    id=db_post.id,
    author={
        "id": db_post.author.id,
        "first_name": db_post.author.first_name,
        "last_name": db_post.author.last_name,
        "avatar": None
    },
    content=db_post.content,
    post_type=db_post.post_type,
    media_type=db_post.media_type,
    media_url=db_post.media_url,
    created_at=db_post.created_at,
    reactions_count=db_post.reactions_count,
    comments_count=db_post.comments_count,
    shares_count=db_post.shares_count
    )

@app.get("/posts/", response_model=List[PostResponse])
async def get_posts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    posts = db.query(Post).order_by(Post.created_at.desc()).limit(50).all()
    
    return [
    PostResponse(
        id=post.id,
        author={
            "id": post.author.id,
            "first_name": post.author.first_name,
            "last_name": post.author.last_name,
            "avatar": None
        },
        content=post.content,
        post_type=post.post_type,
        media_type=post.media_type,
        media_url=post.media_url,
        created_at=post.created_at,
        reactions_count=post.reactions_count,
        comments_count=post.comments_count,
        shares_count=post.shares_count
    )
    for post in posts
    ]

# User posts routes
@app.get("/users/{user_id}/posts", response_model=List[PostResponse])
async def get_user_posts(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    posts = db.query(Post).filter(
    Post.author_id == user_id,
    Post.post_type == "post"
    ).order_by(Post.created_at.desc()).limit(50).all()
    
    return [
    PostResponse(
        id=post.id,
        author={
            "id": post.author.id,
            "first_name": post.author.first_name,
            "last_name": post.author.last_name,
            "avatar": getattr(post.author, 'avatar', None)
        },
        content=post.content,
        post_type=post.post_type,
        media_type=post.media_type,
        media_url=post.media_url,
        created_at=post.created_at,
        reactions_count=db.query(Reaction).filter(Reaction.post_id == post.id).count(),
        comments_count=db.query(Comment).filter(Comment.post_id == post.id).count(),
        shares_count=db.query(Share).filter(Share.post_id == post.id).count()
    )
    for post in posts
    ]

@app.get("/users/{user_id}/testimonials", response_model=List[PostResponse])
async def get_user_testimonials(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    testimonials = db.query(Post).filter(
    Post.author_id == user_id,
    Post.post_type == "testimonial"
    ).order_by(Post.created_at.desc()).limit(50).all()
    
    return [
    PostResponse(
        id=post.id,
        author={
            "id": post.author.id,
            "first_name": post.author.first_name,
            "last_name": post.author.last_name,
            "avatar": getattr(post.author, 'avatar', None)
        },
        content=post.content,
        post_type=post.post_type,
        media_type=post.media_type,
        media_url=post.media_url,
        created_at=post.created_at,
        reactions_count=db.query(Reaction).filter(Reaction.post_id == post.id).count(),
        comments_count=db.query(Comment).filter(Comment.post_id == post.id).count(),
        shares_count=db.query(Share).filter(Share.post_id == post.id).count()
    )
    for post in testimonials
    ]

# Reactions routes
@app.post("/reactions/")
async def create_reaction(reaction: ReactionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if post exists
    post = db.query(Post).filter(Post.id == reaction.post_id).first()
    if not post:
    raise HTTPException(status_code=404, detail="Post not found")
    
    # Valid reaction types (modern social media reactions)
    valid_reactions = ["like", "love", "haha", "wow", "sad", "angry", "care", "pride", "grateful", "celebrating"]
    if reaction.reaction_type not in valid_reactions:
    raise HTTPException(status_code=400, detail="Invalid reaction type")
    
    # Check if user already reacted to this post
    existing_reaction = db.query(Reaction).filter(
    Reaction.user_id == current_user.id,
    Reaction.post_id == reaction.post_id
    ).first()
    
    if existing_reaction:
    if existing_reaction.reaction_type == reaction.reaction_type:
        # Remove reaction if same type
        db.delete(existing_reaction)
        db.commit()
        return {"message": "Reaction removed"}
    else:
        # Update reaction type
        existing_reaction.reaction_type = reaction.reaction_type
        db.commit()
        return {"message": "Reaction updated"}
    
    # Create new reaction
    db_reaction = Reaction(
    user_id=current_user.id,
    post_id=reaction.post_id,
    reaction_type=reaction.reaction_type
    )
    db.add(db_reaction)
    db.commit()
    
    # Send notification to post author if not self-reaction
    if post.author_id != current_user.id:
    notification = Notification(
        recipient_id=post.author_id,
        sender_id=current_user.id,
        notification_type="reaction",
        title=f"{current_user.first_name} {current_user.last_name}",
        message=f"reagiu ao seu post com {reaction.reaction_type}",
        data=json.dumps({"post_id": reaction.post_id}),
        created_at=datetime.utcnow()
    )
    db.add(notification)
    db.commit()
    
    # Send real-time notification
    await manager.send_notification(post.author_id, {
        "id": notification.id,
        "type": "reaction",
        "title": f"{current_user.first_name} {current_user.last_name}",
        "message": f"reagiu ao seu post com {reaction.reaction_type}",
        "sender": {
            "id": current_user.id,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "avatar": getattr(current_user, 'avatar', None)
        },
        "data": {"post_id": reaction.post_id},
        "created_at": notification.created_at.isoformat()
    })
    
    return {"message": "Reaction created"}

@app.get("/reactions/post/{post_id}")
async def get_post_reactions(post_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    reactions = db.query(Reaction).filter(Reaction.post_id == post_id).all()
    
    # Group reactions by type
    reaction_counts = {}
    user_reaction = None
    
    for reaction in reactions:
    if reaction.reaction_type not in reaction_counts:
        reaction_counts[reaction.reaction_type] = 0
    reaction_counts[reaction.reaction_type] += 1
    
    if reaction.user_id == current_user.id:
        user_reaction = reaction.reaction_type
    
    return {
    "reactions": reaction_counts,
    "user_reaction": user_reaction,
    "total": len(reactions)
    }

@app.get("/reactions/post/{post_id}/detailed")
async def get_post_reactions_detailed(post_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get detailed reactions with user information"""
    reactions = db.query(Reaction).filter(Reaction.post_id == post_id).all()

    # Group reactions by type with user details
    reaction_details = {}
    user_reaction = None

    for reaction in reactions:
    if reaction.reaction_type not in reaction_details:
        reaction_details[reaction.reaction_type] = {
            "count": 0,
            "users": []
        }

    reaction_details[reaction.reaction_type]["count"] += 1
    reaction_details[reaction.reaction_type]["users"].append({
        "id": reaction.user.id,
        "first_name": reaction.user.first_name,
        "last_name": reaction.user.last_name,
        "avatar": reaction.user.avatar,
        "created_at": reaction.created_at.isoformat()
    })

    if reaction.user_id == current_user.id:
        user_reaction = reaction.reaction_type

    return {
    "reactions": reaction_details,
    "user_reaction": user_reaction,
    "total": len(reactions)
    }

# Comments routes
@app.post("/comments/", response_model=CommentResponse)
async def create_comment(comment: CommentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if post exists
    post = db.query(Post).filter(Post.id == comment.post_id).first()
    if not post:
    raise HTTPException(status_code=404, detail="Post not found")
    
    db_comment = Comment(
    content=comment.content,
    post_id=comment.post_id,
    parent_id=comment.parent_id,
    author_id=current_user.id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    # Send notification to post author
    if post.author_id != current_user.id:
    notification = Notification(
        recipient_id=post.author_id,
        sender_id=current_user.id,
        notification_type="comment",
        title=f"{current_user.first_name} {current_user.last_name}",
        message="comentou no seu post",
        data=json.dumps({"post_id": comment.post_id, "comment_id": db_comment.id}),
        created_at=datetime.utcnow()
    )
    db.add(notification)
    db.commit()
    
    # Send real-time notification
    await manager.send_notification(post.author_id, {
        "id": notification.id,
        "type": "comment",
        "title": f"{current_user.first_name} {current_user.last_name}",
        "message": "comentou no seu post",
        "sender": {
            "id": current_user.id,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "avatar": getattr(current_user, 'avatar', None)
        },
        "data": {"post_id": comment.post_id, "comment_id": db_comment.id},
        "created_at": notification.created_at.isoformat()
    })
    
    return CommentResponse(
    id=db_comment.id,
    content=db_comment.content,
    author={
        "id": db_comment.author.id,
        "first_name": db_comment.author.first_name,
        "last_name": db_comment.author.last_name,
        "avatar": getattr(db_comment.author, 'avatar', None)
    },
    created_at=db_comment.created_at,
    reactions_count=0,
    replies=[]
    )

@app.get("/comments/post/{post_id}", response_model=List[CommentResponse])
async def get_post_comments(post_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.post_id == post_id, Comment.parent_id.is_(None)).all()
    
    result = []
    for comment in comments:
    replies = db.query(Comment).filter(Comment.parent_id == comment.id).all()
    result.append(CommentResponse(
        id=comment.id,
        content=comment.content,
        author={
            "id": comment.author.id,
            "first_name": comment.author.first_name,
            "last_name": comment.author.last_name,
            "avatar": getattr(comment.author, 'avatar', None)
        },
        created_at=comment.created_at,
        reactions_count=0,
        replies=[
            CommentResponse(
                id=reply.id,
                content=reply.content,
                author={
                    "id": reply.author.id,
                    "first_name": reply.author.first_name,
                    "last_name": reply.author.last_name,
                    "avatar": getattr(reply.author, 'avatar', None)
                },
                created_at=reply.created_at,
                reactions_count=0,
                replies=[]
            ) for reply in replies
        ]
    ))
    
    return result

# Shares routes
@app.post("/shares/")
async def share_post(share: ShareCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if post exists
    post = db.query(Post).filter(Post.id == share.post_id).first()
    if not post:
    raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if user already shared this post
    existing_share = db.query(Share).filter(
    Share.user_id == current_user.id,
    Share.post_id == share.post_id
    ).first()
    
    if existing_share:
    raise HTTPException(status_code=400, detail="Post already shared")
    
    db_share = Share(
    user_id=current_user.id,
    post_id=share.post_id
    )
    db.add(db_share)
    db.commit()
    
    return {"message": "Post shared successfully"}

# Friendships routes
@app.post("/friendships/")
async def send_friend_request(friendship: FriendshipCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if user exists
    addressee = db.query(User).filter(User.id == friendship.addressee_id, User.is_active == True).first()
    if not addressee:
    raise HTTPException(status_code=404, detail="User not found")
    
    # Can't send request to yourself
    if current_user.id == friendship.addressee_id:
    raise HTTPException(status_code=400, detail="Cannot send friend request to yourself")
    
    # Check if friendship already exists
    existing_friendship = db.query(Friendship).filter(
    ((Friendship.requester_id == current_user.id) & (Friendship.addressee_id == friendship.addressee_id)) |
    ((Friendship.requester_id == friendship.addressee_id) & (Friendship.addressee_id == current_user.id))
    ).first()
    
    if existing_friendship:
    if existing_friendship.status == "pending":
        raise HTTPException(status_code=400, detail="Friend request already sent")
    elif existing_friendship.status == "accepted":
        raise HTTPException(status_code=400, detail="Already friends")
    
    # Create friendship request
    db_friendship = Friendship(
    requester_id=current_user.id,
    addressee_id=friendship.addressee_id,
    status="pending"
    )
    db.add(db_friendship)
    db.commit()
    
    # Send notification
    notification = Notification(
    recipient_id=friendship.addressee_id,
    sender_id=current_user.id,
    notification_type="friend_request",
    title=f"{current_user.first_name} {current_user.last_name}",
    message="enviou uma solicitação de amizade",
    data=json.dumps({"friendship_id": db_friendship.id}),
    created_at=datetime.utcnow()
    )
    db.add(notification)
    db.commit()
    
    # Send real-time notification
    await manager.send_notification(friendship.addressee_id, {
    "id": notification.id,
    "type": "friend_request",
    "title": f"{current_user.first_name} {current_user.last_name}",
    "message": "enviou uma solicitação de amizade",
    "sender": {
        "id": current_user.id,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "avatar": getattr(current_user, 'avatar', None)
    },
    "data": {"friendship_id": db_friendship.id},
    "created_at": notification.created_at.isoformat()
    })
    
    return {"message": "Friend request sent successfully"}

@app.put("/friendships/{friendship_id}/accept")
async def accept_friend_request(friendship_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    friendship = db.query(Friendship).filter(Friendship.id == friendship_id).first()
    if not friendship:
    raise HTTPException(status_code=404, detail="Friend request not found")
    
    if friendship.addressee_id != current_user.id:
    raise HTTPException(status_code=403, detail="Not authorized to accept this request")
    
    if friendship.status != "pending":
    raise HTTPException(status_code=400, detail="Friend request is not pending")
    
    friendship.status = "accepted"
    friendship.updated_at = datetime.utcnow()
    db.commit()
    
    # Send notification to requester
    notification = Notification(
    recipient_id=friendship.requester_id,
    sender_id=current_user.id,
    notification_type="friend_accept",
    title=f"{current_user.first_name} {current_user.last_name}",
    message="aceitou sua solicitação de amizade",
    data=json.dumps({"friendship_id": friendship_id}),
    created_at=datetime.utcnow()
    )
    db.add(notification)
    db.commit()
    
    # Send real-time notification
    await manager.send_notification(friendship.requester_id, {
    "id": notification.id,
    "type": "friend_accept",
    "title": f"{current_user.first_name} {current_user.last_name}",
    "message": "aceitou sua solicitação de amizade",
    "sender": {
        "id": current_user.id,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "avatar": getattr(current_user, 'avatar', None)
    },
    "data": {"friendship_id": friendship_id},
    "created_at": notification.created_at.isoformat()
    })
    
    return {"message": "Friend request accepted"}

@app.put("/friendships/{friendship_id}/reject")
async def reject_friend_request(friendship_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    friendship = db.query(Friendship).filter(Friendship.id == friendship_id).first()
    if not friendship:
    raise HTTPException(status_code=404, detail="Friend request not found")
    
    if friendship.addressee_id != current_user.id:
    raise HTTPException(status_code=403, detail="Not authorized to reject this request")
    
    if friendship.status != "pending":
    raise HTTPException(status_code=400, detail="Friend request is not pending")
    
    friendship.status = "rejected"
    friendship.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Friend request rejected"}

@app.get("/friendships/status/{user_id}")
async def get_friendship_status(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    friendship = db.query(Friendship).filter(
    ((Friendship.requester_id == current_user.id) & (Friendship.addressee_id == user_id)) |
    ((Friendship.requester_id == user_id) & (Friendship.addressee_id == current_user.id))
    ).first()
    
    if not friendship:
    return {"status": "none"}
    
    return {"status": friendship.status}

# User search
@app.get("/users/")
async def search_users(search: str = "", current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not search.strip():
    return []
    
    users = db.query(User).filter(
    User.is_active == True,
    User.id != current_user.id,
    (User.first_name.ilike(f"%{search}%") | User.last_name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%"))
    ).limit(20).all()
    
    return [
    {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "avatar": getattr(user, 'avatar', None)
    }
    for user in users
    ]

# Get user by ID
@app.get("/users/{user_id}")
async def get_user_by_id(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
    raise HTTPException(status_code=404, detail="User not found")
    
    return {
    "id": user.id,
    "first_name": user.first_name,
    "last_name": user.last_name,
    "email": user.email,
    "bio": getattr(user, 'bio', None),
    "avatar": getattr(user, 'avatar', None),
    "birth_date": user.birth_date.isoformat() if user.birth_date else None,
    "created_at": user.created_at.isoformat()
    }

# Get user profile with complete information
@app.get("/users/{user_id}/profile")
async def get_user_profile(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Obter perfil completo do usuário com configurações de privacidade"""
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
    raise HTTPException(status_code=404, detail="User not found")

    # Verificar se são amigos para mostrar informações privadas
    friendship = db.query(Friendship).filter(
    ((Friendship.requester_id == current_user.id) & (Friendship.addressee_id == user_id)) |
    ((Friendship.requester_id == user_id) & (Friendship.addressee_id == current_user.id)),
    Friendship.status == "accepted"
    ).first()

    is_friend = friendship is not None
    is_own_profile = current_user.id == user_id

    # Calcular estatísticas
    friends_count = db.query(Friendship).filter(
    ((Friendship.requester_id == user_id) | (Friendship.addressee_id == user_id)),
    Friendship.status == "accepted"
    ).count()

    posts_count = db.query(Post).filter(Post.author_id == user_id).count()

    # Determinar visibilidade das informações com base nas configurações de privacidade
    def can_see_field(field_visibility):
    if is_own_profile:
        return True
    if field_visibility == "public":
        return True
    if field_visibility == "friends" and is_friend:
        return True
    return False

    response_data = {
    "id": user.id,
    "first_name": user.first_name,
    "last_name": user.last_name,
    "username": user.username,
    "nickname": user.nickname,
    "bio": user.bio,
    "avatar": user.avatar,
    "cover_photo": user.cover_photo,
    "location": user.location,
    "website": user.website,
    "relationship_status": user.relationship_status,
    "work": user.work,
    "education": user.education,
    "is_verified": user.is_verified,
    "created_at": user.created_at.isoformat(),
    "friends_count": friends_count,
    "posts_count": posts_count,
    "is_own_profile": is_own_profile,
    "is_friend": is_friend
    }

    # Adicionar campos sensíveis apenas se permitido pelas configurações de privacidade
    if can_see_field(user.email_visibility):
    response_data["email"] = user.email

    if can_see_field(user.phone_visibility):
    response_data["phone"] = user.phone

    if can_see_field(user.birth_date_visibility):
    response_data["birth_date"] = user.birth_date.isoformat() if user.birth_date else None
    response_data["gender"] = user.gender

    return response_data

# Get user friends list
@app.get("/users/{user_id}/friends")
async def get_user_friends(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Obter lista de amigos do usuário"""
    # Verificar se pode ver a lista de amigos
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
    raise HTTPException(status_code=404, detail="User not found")

    # Verificar privacidade do perfil
    if user.profile_visibility == "private" and current_user.id != user_id:
    # Verificar se são amigos
    friendship = db.query(Friendship).filter(
        ((Friendship.requester_id == current_user.id) & (Friendship.addressee_id == user_id)) |
        ((Friendship.requester_id == user_id) & (Friendship.addressee_id == current_user.id)),
        Friendship.status == "accepted"
    ).first()

    if not friendship:
        raise HTTPException(status_code=403, detail="Cannot view this user's friends list")

    # Buscar amigos
    friendships = db.query(Friendship).filter(
    ((Friendship.requester_id == user_id) | (Friendship.addressee_id == user_id)),
    Friendship.status == "accepted"
    ).all()

    friends_data = []
    for friendship in friendships:
    friend_id = friendship.addressee_id if friendship.requester_id == user_id else friendship.requester_id
    friend = db.query(User).filter(User.id == friend_id).first()

    if friend:
        friends_data.append({
            "id": friend.id,
            "first_name": friend.first_name,
            "last_name": friend.last_name,
            "username": friend.username,
            "avatar": friend.avatar,
            "friends_since": friendship.updated_at.isoformat() if friendship.updated_at else friendship.created_at.isoformat()
        })

    return friends_data

# Remove friend
@app.delete("/friends/{friend_id}")
async def remove_friend(friend_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Remover amigo"""
    friendship = db.query(Friendship).filter(
    ((Friendship.requester_id == current_user.id) & (Friendship.addressee_id == friend_id)) |
    ((Friendship.requester_id == friend_id) & (Friendship.addressee_id == current_user.id)),
    Friendship.status == "accepted"
    ).first()

    if not friendship:
    raise HTTPException(status_code=404, detail="Friendship not found")

    db.delete(friendship)
    db.commit()

    return {"message": "Friend removed successfully"}

# Avatar and cover photo routes
@app.post("/profile/avatar")
async def upload_avatar(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Upload e definir avatar do usuário"""
    import os
    import uuid
    from pathlib import Path

    # Validar se é imagem
    if not file.content_type.startswith("image/"):
    raise HTTPException(status_code=400, detail="File must be an image")

    # Validar tamanho (5MB max para avatar)
    if file.size > 5 * 1024 * 1024:
    raise HTTPException(status_code=400, detail="Image too large (max 5MB)")

    try:
    # Criar diretório se não existe
    upload_dir = Path("uploads") / "image"
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Gerar nome único
    file_extension = Path(file.filename).suffix
    unique_filename = f"avatar_{current_user.id}_{uuid.uuid4()}{file_extension}"
    file_path = upload_dir / unique_filename

    # Salvar arquivo
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Atualizar avatar do usuário
    avatar_url = f"/uploads/image/{unique_filename}"
    current_user.avatar = avatar_url
    current_user.updated_at = datetime.utcnow()
    db.commit()

    return {
        "message": "Avatar updated successfully",
        "avatar_url": avatar_url
    }
    except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to upload avatar: {str(e)}")

@app.post("/profile/cover")
async def upload_cover_photo(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Upload e definir foto de capa do usuário"""
    import os
    import uuid
    from pathlib import Path

    # Validar se é imagem
    if not file.content_type.startswith("image/"):
    raise HTTPException(status_code=400, detail="File must be an image")

    # Validar tamanho (10MB max para capa)
    if file.size > 10 * 1024 * 1024:
    raise HTTPException(status_code=400, detail="Image too large (max 10MB)")

    try:
    # Criar diretório se não existe
    upload_dir = Path("uploads") / "image"
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Gerar nome único
    file_extension = Path(file.filename).suffix
    unique_filename = f"cover_{current_user.id}_{uuid.uuid4()}{file_extension}"
    file_path = upload_dir / unique_filename

    # Salvar arquivo
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Atualizar foto de capa do usuário
    cover_url = f"/uploads/image/{unique_filename}"
    current_user.cover_photo = cover_url
    current_user.updated_at = datetime.utcnow()
    db.commit()

    return {
        "message": "Cover photo updated successfully",
        "cover_photo_url": cover_url
    }
    except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to upload cover photo: {str(e)}")

# Mark all notifications as read
@app.put("/notifications/mark-all-read")
async def mark_all_notifications_as_read(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(Notification).filter(
    Notification.recipient_id == current_user.id,
    Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    
    return {"message": "All notifications marked as read"}

# Delete notification
@app.delete("/notifications/{notification_id}")
async def delete_notification(notification_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notification = db.query(Notification).filter(
    Notification.id == notification_id,
    Notification.recipient_id == current_user.id
    ).first()
    
    if not notification:
    raise HTTPException(status_code=404, detail="Notification not found")
    
    db.delete(notification)
    db.commit()
    
    return {"message": "Notification deleted"}

# Delete post
@app.delete("/posts/{post_id}")
async def delete_post(post_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
    raise HTTPException(status_code=404, detail="Post not found")
    
    if post.author_id != current_user.id:
    raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    # Delete related data
    db.query(Reaction).filter(Reaction.post_id == post_id).delete()
    db.query(Comment).filter(Comment.post_id == post_id).delete()
    db.query(Share).filter(Share.post_id == post_id).delete()
    
    db.delete(post)
    db.commit()
    
    return {"message": "Post deleted successfully"}

# Stories routes
@app.post("/stories/", response_model=StoryResponse)
async def create_story(story: StoryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Validação especial para vídeos - máximo 25 segundos
    if story.media_type == "video" and story.max_duration_seconds > 25:
    raise HTTPException(status_code=400, detail="Video stories cannot exceed 25 seconds")

    expires_at = datetime.utcnow() + timedelta(hours=story.duration_hours)
    
    db_story = Story(
    author_id=current_user.id,
    content=story.content,
    media_type=story.media_type,
    media_url=story.media_url,
    background_color=story.background_color,
    duration_hours=story.duration_hours,
    max_duration_seconds=story.max_duration_seconds,
    archived=story.archived,
    expires_at=expires_at
    )
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    
    return StoryResponse(
    id=db_story.id,
    author={
        "id": db_story.author.id,
        "first_name": db_story.author.first_name,
        "last_name": db_story.author.last_name,
        "avatar": None
    },
    content=db_story.content,
    media_type=db_story.media_type,
    media_url=db_story.media_url,
    background_color=db_story.background_color,
    created_at=db_story.created_at,
    expires_at=db_story.expires_at,
    views_count=0
    )

@app.get("/stories/", response_model=List[StoryResponse])
async def get_stories(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Get stories that haven't expired
    now = datetime.utcnow()
    stories = db.query(Story).filter(Story.expires_at > now).order_by(Story.created_at.desc()).all()
    
    return [
    StoryResponse(
        id=story.id,
        author={
            "id": story.author.id,
            "first_name": story.author.first_name,
            "last_name": story.author.last_name,
            "avatar": None
        },
        content=story.content,
        media_type=story.media_type,
        media_url=story.media_url,
        background_color=story.background_color,
        created_at=story.created_at,
        expires_at=story.expires_at,
        views_count=db.query(StoryView).filter(StoryView.story_id == story.id).count()
    )
    for story in stories
    ]

@app.post("/stories/{story_id}/view")
async def view_story(story_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
    raise HTTPException(status_code=404, detail="Story not found")
    
    if story.expires_at <= datetime.utcnow():
    raise HTTPException(status_code=410, detail="Story has expired")
    
    # Check if already viewed
    existing_view = db.query(StoryView).filter(
    StoryView.story_id == story_id,
    StoryView.viewer_id == current_user.id
    ).first()
    
    if not existing_view:
    db_view = StoryView(
        story_id=story_id,
        viewer_id=current_user.id
    )
    db.add(db_view)
    db.commit()
    
    return {"message": "Story viewed"}

@app.delete("/stories/{story_id}")
async def delete_story(story_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
    raise HTTPException(status_code=404, detail="Story not found")
    
    if story.author_id != current_user.id:
    raise HTTPException(status_code=403, detail="Not authorized to delete this story")
    
    # Delete story views first
    db.query(StoryView).filter(StoryView.story_id == story_id).delete()
    
    # Delete the story
    db.delete(story)
    db.commit()
    
    return {"message": "Story deleted successfully"}

# Advanced Story Editor routes
@app.post("/stories/with-editor", response_model=StoryResponse)
async def create_story_with_editor(story_data: StoryWithEditor, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Criar story com editor mobile completo (tags, overlays, etc.)"""
    # Validação especial para vídeos - máximo 25 segundos
    if story_data.media_type == "video" and story_data.max_duration_seconds > 25:
    raise HTTPException(status_code=400, detail="Video stories cannot exceed 25 seconds")

    expires_at = datetime.utcnow() + timedelta(hours=story_data.duration_hours)

    # Criar story base
    db_story = Story(
    author_id=current_user.id,
    content=story_data.content,
    media_type=story_data.media_type,
    media_url=story_data.media_url,
    background_color=story_data.background_color,
    duration_hours=story_data.duration_hours,
    max_duration_seconds=story_data.max_duration_seconds,
    expires_at=expires_at
    )
    db.add(db_story)
    db.commit()
    db.refresh(db_story)

    # Adicionar tags
    for tag_data in story_data.tags:
    # Verificar se usuário tagueado existe
    tagged_user = db.query(User).filter(User.id == tag_data.tagged_user_id).first()
    if tagged_user:
        story_tag = StoryTag(
            story_id=db_story.id,
            tagged_user_id=tag_data.tagged_user_id,
            position_x=tag_data.position_x,
            position_y=tag_data.position_y
        )
        db.add(story_tag)

        # Notificar usuário tagueado
        if tagged_user.story_notifications:
            notification = Notification(
                recipient_id=tag_data.tagged_user_id,
                sender_id=current_user.id,
                notification_type="story_tag",
                title=f"{current_user.first_name} {current_user.last_name}",
                message="marcou você em um story",
                data=json.dumps({"story_id": db_story.id}),
                created_at=datetime.utcnow()
            )
            db.add(notification)

    # Adicionar overlays
    for overlay_data in story_data.overlays:
    story_overlay = StoryOverlay(
        story_id=db_story.id,
        overlay_type=overlay_data.overlay_type,
        content=overlay_data.content,
        position_x=overlay_data.position_x,
        position_y=overlay_data.position_y,
        rotation=overlay_data.rotation,
        scale=overlay_data.scale,
        color=overlay_data.color,
        font_family=overlay_data.font_family,
        font_size=overlay_data.font_size
    )
    db.add(story_overlay)

    db.commit()

    return StoryResponse(
    id=db_story.id,
    author={
        "id": db_story.author.id,
        "first_name": db_story.author.first_name,
        "last_name": db_story.author.last_name,
        "avatar": db_story.author.avatar
    },
    content=db_story.content,
    media_type=db_story.media_type,
    media_url=db_story.media_url,
    background_color=db_story.background_color,
    created_at=db_story.created_at,
    expires_at=db_story.expires_at,
    views_count=0
    )

@app.post("/stories/{story_id}/tags")
async def add_story_tag(story_id: int, tag_data: StoryTagCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Adicionar tag a um story existente"""
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
    raise HTTPException(status_code=404, detail="Story not found")

    if story.author_id != current_user.id:
    raise HTTPException(status_code=403, detail="Not authorized to tag in this story")

    # Verificar se usuário existe
    tagged_user = db.query(User).filter(User.id == tag_data.tagged_user_id).first()
    if not tagged_user:
    raise HTTPException(status_code=404, detail="Tagged user not found")

    # Verificar se já foi tagueado
    existing_tag = db.query(StoryTag).filter(
    StoryTag.story_id == story_id,
    StoryTag.tagged_user_id == tag_data.tagged_user_id
    ).first()

    if existing_tag:
    raise HTTPException(status_code=400, detail="User already tagged in this story")

    # Criar tag
    story_tag = StoryTag(
    story_id=story_id,
    tagged_user_id=tag_data.tagged_user_id,
    position_x=tag_data.position_x,
    position_y=tag_data.position_y
    )
    db.add(story_tag)
    db.commit()

    return {"message": "User tagged successfully"}

@app.post("/stories/{story_id}/overlays")
async def add_story_overlay(story_id: int, overlay_data: StoryOverlayCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Adicionar overlay a um story existente"""
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
    raise HTTPException(status_code=404, detail="Story not found")

    if story.author_id != current_user.id:
    raise HTTPException(status_code=403, detail="Not authorized to add overlay to this story")

    story_overlay = StoryOverlay(
    story_id=story_id,
    overlay_type=overlay_data.overlay_type,
    content=overlay_data.content,
    position_x=overlay_data.position_x,
    position_y=overlay_data.position_y,
    rotation=overlay_data.rotation,
    scale=overlay_data.scale,
    color=overlay_data.color,
    font_family=overlay_data.font_family,
    font_size=overlay_data.font_size
    )
    db.add(story_overlay)
    db.commit()

    return {"message": "Overlay added successfully"}

@app.get("/stories/{story_id}/details")
async def get_story_details(story_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Obter detalhes completos do story incluindo tags e overlays"""
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
    raise HTTPException(status_code=404, detail="Story not found")

    # Verificar se pode ver o story
    if story.expires_at <= datetime.utcnow() and story.author_id != current_user.id:
    raise HTTPException(status_code=410, detail="Story has expired")

    # Buscar tags
    tags = db.query(StoryTag).filter(StoryTag.story_id == story_id).all()
    tag_data = [
    {
        "id": tag.id,
        "tagged_user": {
            "id": tag.tagged_user.id,
            "first_name": tag.tagged_user.first_name,
            "last_name": tag.tagged_user.last_name,
            "avatar": tag.tagged_user.avatar
        },
        "position_x": tag.position_x,
        "position_y": tag.position_y
    }
    for tag in tags
    ]

    # Buscar overlays
    overlays = db.query(StoryOverlay).filter(StoryOverlay.story_id == story_id).all()
    overlay_data = [
    {
        "id": overlay.id,
        "overlay_type": overlay.overlay_type,
        "content": overlay.content,
        "position_x": overlay.position_x,
        "position_y": overlay.position_y,
        "rotation": overlay.rotation,
        "scale": overlay.scale,
        "color": overlay.color,
        "font_family": overlay.font_family,
        "font_size": overlay.font_size
    }
    for overlay in overlays
    ]

    return {
    "id": story.id,
    "author": {
        "id": story.author.id,
        "first_name": story.author.first_name,
        "last_name": story.author.last_name,
        "avatar": story.author.avatar
    },
    "content": story.content,
    "media_type": story.media_type,
    "media_url": story.media_url,
    "background_color": story.background_color,
    "max_duration_seconds": story.max_duration_seconds,
    "created_at": story.created_at,
    "expires_at": story.expires_at,
    "views_count": db.query(StoryView).filter(StoryView.story_id == story_id).count(),
    "tags": tag_data,
    "overlays": overlay_data
    }

# Notifications routes
@app.get("/notifications/", response_model=List[NotificationResponse])
async def get_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notifications = db.query(Notification).filter(
    Notification.recipient_id == current_user.id
    ).order_by(Notification.created_at.desc()).limit(50).all()
    
    return [
    NotificationResponse(
        id=notification.id,
        notification_type=notification.notification_type,
        title=notification.title,
        message=notification.message,
        data=notification.data,
        is_read=notification.is_read,
        created_at=notification.created_at,
        sender={
            "id": notification.sender.id,
            "name": f"{notification.sender.first_name} {notification.sender.last_name}"
        } if notification.sender else None
    )
    for notification in notifications
    ]

@app.get("/notifications/unread-count")
async def get_unread_notifications_count(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    count = db.query(Notification).filter(
    Notification.recipient_id == current_user.id,
    Notification.is_read == False
    ).count()
    
    return {"count": count}

@app.put("/notifications/{notification_id}/read")
async def mark_notification_as_read(notification_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notification = db.query(Notification).filter(
    Notification.id == notification_id,
    Notification.recipient_id == current_user.id
    ).first()
    
    if not notification:
    raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    db.commit()
    
    return {"message": "Notification marked as read"}

# Friendships routes
@app.get("/friendships/pending-count")
async def get_pending_friendships_count(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    count = db.query(Friendship).filter(
    Friendship.addressee_id == current_user.id,
    Friendship.status == "pending"
    ).count()
    
    return {"count": count}

@app.get("/friendships/pending")
async def get_pending_friendships(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    friendships = db.query(Friendship).filter(
    Friendship.addressee_id == current_user.id,
    Friendship.status == "pending"
    ).all()
    
    return [
    {
        "id": friendship.id,
        "requester": {
            "id": friendship.requester.id,
            "first_name": friendship.requester.first_name,
            "last_name": friendship.requester.last_name,
            "avatar": None
        },
        "created_at": friendship.created_at
    }
    for friendship in friendships
    ]

# Settings and Profile routes
@app.put("/profile/")
async def update_profile(profile_data: UserProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Atualizar perfil do usuário"""
    update_data = profile_data.dict(exclude_unset=True)

    # Verificar se username é único (se fornecido)
    if "username" in update_data and update_data["username"]:
    existing_user = db.query(User).filter(
        User.username == update_data["username"],
        User.id != current_user.id
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    # Atualizar campos
    for field, value in update_data.items():
    setattr(current_user, field, value)

    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)

    return {"message": "Profile updated successfully"}

@app.put("/settings/password")
async def update_password(password_data: PasswordUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Alterar senha do usuário"""
    if not verify_password(password_data.current_password, current_user.password_hash):
    raise HTTPException(status_code=400, detail="Current password is incorrect")

    # Verificar se nova senha é diferente
    if verify_password(password_data.new_password, current_user.password_hash):
    raise HTTPException(status_code=400, detail="New password must be different from current password")

    current_user.password_hash = hash_password(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)

    return {"message": "Password updated successfully"}

@app.get("/settings/privacy")
async def get_privacy_settings(current_user: User = Depends(get_current_user)):
    """Obter configurações de privacidade"""
    return {
    "profile_visibility": current_user.profile_visibility,
    "friend_request_privacy": current_user.friend_request_privacy,
    "post_visibility": current_user.post_visibility,
    "story_visibility": current_user.story_visibility,
    "email_visibility": current_user.email_visibility,
    "phone_visibility": current_user.phone_visibility,
    "birth_date_visibility": current_user.birth_date_visibility
    }

@app.put("/settings/privacy")
async def update_privacy_settings(privacy_data: PrivacySettings, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Atualizar configurações de privacidade"""
    update_data = privacy_data.dict(exclude_unset=True)

    # Validar valores de privacidade
    valid_visibility = ["public", "friends", "private"]
    valid_friend_request = ["everyone", "friends_of_friends", "none"]

    for field, value in update_data.items():
    if "visibility" in field and value not in valid_visibility:
        raise HTTPException(status_code=400, detail=f"Invalid {field} value")
    if field == "friend_request_privacy" and value not in valid_friend_request:
        raise HTTPException(status_code=400, detail="Invalid friend_request_privacy value")

    setattr(current_user, field, value)

    current_user.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Privacy settings updated successfully"}

@app.get("/settings/notifications")
async def get_notification_settings(current_user: User = Depends(get_current_user)):
    """Obter configurações de notificação"""
    return {
    "email_notifications": current_user.email_notifications,
    "push_notifications": current_user.push_notifications,
    "friend_request_notifications": current_user.friend_request_notifications,
    "comment_notifications": current_user.comment_notifications,
    "reaction_notifications": current_user.reaction_notifications,
    "message_notifications": current_user.message_notifications,
    "story_notifications": current_user.story_notifications
    }

@app.put("/settings/notifications")
async def update_notification_settings(notification_data: NotificationSettings, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Atualizar configurações de notificação"""
    update_data = notification_data.dict(exclude_unset=True)

    for field, value in update_data.items():
    setattr(current_user, field, value)

    current_user.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Notification settings updated successfully"}

@app.delete("/account/deactivate")
async def deactivate_account(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Desativar conta do usuário"""
    current_user.account_deactivated = True
    current_user.deactivated_at = datetime.utcnow()
    current_user.is_active = False
    current_user.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Account deactivated successfully"}

@app.delete("/account/delete")
async def delete_account(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Deletar conta permanentemente (soft delete)"""
    # Soft delete - manter dados mas marcar como deletado
    current_user.account_deactivated = True
    current_user.deactivated_at = datetime.utcnow()
    current_user.is_active = False
    current_user.email = f"deleted_{current_user.id}_{current_user.email}"  # Permitir reuso do email
    current_user.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Account deleted successfully"}

# Messages routes
@app.post("/messages/", response_model=MessageResponse)
async def send_message(message_data: MessageCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Enviar mensagem"""
    # Verificar se destinatário existe
    recipient = db.query(User).filter(User.id == message_data.recipient_id, User.is_active == True).first()
    if not recipient:
    raise HTTPException(status_code=404, detail="Recipient not found")

    # Verificar se não está bloqueado
    blocked = db.query(Block).filter(
    ((Block.blocker_id == current_user.id) & (Block.blocked_id == message_data.recipient_id)) |
    ((Block.blocker_id == message_data.recipient_id) & (Block.blocked_id == current_user.id))
    ).first()

    if blocked:
    raise HTTPException(status_code=403, detail="Cannot send message to this user")

    db_message = Message(
    sender_id=current_user.id,
    recipient_id=message_data.recipient_id,
    content=message_data.content,
    message_type=message_data.message_type,
    media_url=message_data.media_url,
    media_metadata=message_data.media_metadata
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    # Enviar notificação em tempo real se o usuário quiser receber
    if recipient.message_notifications:
    notification = Notification(
        recipient_id=message_data.recipient_id,
        sender_id=current_user.id,
        notification_type="message",
        title=f"{current_user.first_name} {current_user.last_name}",
        message="enviou uma mensagem",
        data=json.dumps({"message_id": db_message.id}),
        created_at=datetime.utcnow()
    )
    db.add(notification)
    db.commit()

    # Enviar via WebSocket
    await manager.send_notification(message_data.recipient_id, {
        "id": notification.id,
        "type": "message",
        "title": f"{current_user.first_name} {current_user.last_name}",
        "message": "enviou uma mensagem",
        "sender": {
            "id": current_user.id,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "avatar": current_user.avatar
        },
        "data": {"message_id": db_message.id},
        "created_at": notification.created_at.isoformat()
    })

    # Enviar mensagem em tempo real via WebSocket (independente das configurações de notificação)
    await manager.send_message(message_data.recipient_id, {
    "id": db_message.id,
    "sender": {
        "id": current_user.id,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "avatar": current_user.avatar
    },
    "content": db_message.content,
    "message_type": db_message.message_type,
    "media_url": db_message.media_url,
    "created_at": db_message.created_at.isoformat(),
    "is_read": False
    })

    return MessageResponse(
    id=db_message.id,
    sender={
        "id": current_user.id,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "avatar": current_user.avatar
    },
    recipient={
        "id": recipient.id,
        "first_name": recipient.first_name,
        "last_name": recipient.last_name,
        "avatar": recipient.avatar
    },
    content=db_message.content,
    message_type=db_message.message_type,
    media_url=db_message.media_url,
    is_read=db_message.is_read,
    created_at=db_message.created_at
    )

@app.get("/messages/conversation/{user_id}")
async def get_conversation(user_id: int, limit: int = 50, offset: int = 0, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Obter conversação com um usuário específico"""
    messages = db.query(Message).filter(
    ((Message.sender_id == current_user.id) & (Message.recipient_id == user_id)) |
    ((Message.sender_id == user_id) & (Message.recipient_id == current_user.id))
    ).order_by(Message.created_at.desc()).offset(offset).limit(limit).all()

    return [
    {
        "id": msg.id,
        "sender": {
            "id": msg.sender.id,
            "first_name": msg.sender.first_name,
            "last_name": msg.sender.last_name,
            "avatar": msg.sender.avatar
        },
        "content": msg.content,
        "message_type": msg.message_type,
        "media_url": msg.media_url,
        "is_read": msg.is_read,
        "created_at": msg.created_at,
        "is_own": msg.sender_id == current_user.id
    }
    for msg in reversed(messages)
    ]

@app.get("/messages/conversations")
async def get_conversations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Obter lista de conversações"""
    # Buscar últimas mensagens de cada conversação
    subquery = db.query(
    Message.id,
    Message.sender_id,
    Message.recipient_id,
    Message.content,
    Message.message_type,
    Message.is_read,
    Message.created_at
    ).filter(
    (Message.sender_id == current_user.id) | (Message.recipient_id == current_user.id)
    ).order_by(Message.created_at.desc()).subquery()

    # Agrupar por conversa e pegar a mais recente
    conversations = db.query(subquery).all()

    conversation_dict = {}
    for msg in conversations:
    other_user_id = msg.recipient_id if msg.sender_id == current_user.id else msg.sender_id

    if other_user_id not in conversation_dict:
        other_user = db.query(User).filter(User.id == other_user_id).first()
        conversation_dict[other_user_id] = {
            "user": {
                "id": other_user.id,
                "first_name": other_user.first_name,
                "last_name": other_user.last_name,
                "avatar": other_user.avatar
            },
            "last_message": {
                "content": msg.content,
                "message_type": msg.message_type,
                "created_at": msg.created_at,
                "is_read": msg.is_read,
                "is_own": msg.sender_id == current_user.id
            },
            "unread_count": 0
        }

    # Contar mensagens não lidas
    for conv_id in conversation_dict:
    unread_count = db.query(Message).filter(
        Message.sender_id == conv_id,
        Message.recipient_id == current_user.id,
        Message.is_read == False
    ).count()
    conversation_dict[conv_id]["unread_count"] = unread_count

    return list(conversation_dict.values())

@app.put("/messages/{message_id}/read")
async def mark_message_as_read(message_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Marcar mensagem como lida"""
    message = db.query(Message).filter(
    Message.id == message_id,
    Message.recipient_id == current_user.id
    ).first()

    if not message:
    raise HTTPException(status_code=404, detail="Message not found")

    message.is_read = True
    message.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Message marked as read"}

# Block and Follow routes
@app.post("/blocks/")
async def block_user(block_data: BlockCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Bloquear usuário"""
    if current_user.id == block_data.blocked_id:
    raise HTTPException(status_code=400, detail="Cannot block yourself")

    # Verificar se usuário existe
    blocked_user = db.query(User).filter(User.id == block_data.blocked_id).first()
    if not blocked_user:
    raise HTTPException(status_code=404, detail="User not found")

    # Verificar se já está bloqueado
    existing_block = db.query(Block).filter(
    Block.blocker_id == current_user.id,
    Block.blocked_id == block_data.blocked_id
    ).first()

    if existing_block:
    raise HTTPException(status_code=400, detail="User already blocked")

    # Criar bloqueio
    db_block = Block(
    blocker_id=current_user.id,
    blocked_id=block_data.blocked_id
    )
    db.add(db_block)

    # Remover amizade se existir
    friendship = db.query(Friendship).filter(
    ((Friendship.requester_id == current_user.id) & (Friendship.addressee_id == block_data.blocked_id)) |
    ((Friendship.requester_id == block_data.blocked_id) & (Friendship.addressee_id == current_user.id))
    ).first()

    if friendship:
    db.delete(friendship)

    # Remover follow se existir
    follow = db.query(Follow).filter(
    Follow.follower_id == current_user.id,
    Follow.followed_id == block_data.blocked_id
    ).first()

    if follow:
    db.delete(follow)

    db.commit()

    return {"message": "User blocked successfully"}

@app.delete("/blocks/{block_id}")
async def unblock_user(block_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Desbloquear usuário"""
    block = db.query(Block).filter(
    Block.id == block_id,
    Block.blocker_id == current_user.id
    ).first()

    if not block:
    raise HTTPException(status_code=404, detail="Block not found")

    db.delete(block)
    db.commit()

    return {"message": "User unblocked successfully"}

@app.get("/blocks/")
async def get_blocked_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Obter lista de usuários bloqueados"""
    blocks = db.query(Block).filter(Block.blocker_id == current_user.id).all()

    return [
    {
        "id": block.id,
        "blocked_user": {
            "id": block.blocked.id,
            "first_name": block.blocked.first_name,
            "last_name": block.blocked.last_name,
            "avatar": block.blocked.avatar
        },
        "created_at": block.created_at
    }
    for block in blocks
    ]

# Stories archive routes
@app.put("/stories/{story_id}/archive")
async def archive_story(story_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Arquivar story"""
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
    raise HTTPException(status_code=404, detail="Story not found")

    if story.author_id != current_user.id:
    raise HTTPException(status_code=403, detail="Not authorized to archive this story")

    story.archived = True
    story.archived_at = datetime.utcnow()
    db.commit()

    return {"message": "Story archived successfully"}

@app.get("/stories/archived")
async def get_archived_stories(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Obter stories arquivados"""
    stories = db.query(Story).filter(
    Story.author_id == current_user.id,
    Story.archived == True
    ).order_by(Story.archived_at.desc()).all()

    return [
    {
        "id": story.id,
        "content": story.content,
        "media_type": story.media_type,
        "media_url": story.media_url,
        "background_color": story.background_color,
        "created_at": story.created_at,
        "archived_at": story.archived_at,
        "views_count": db.query(StoryView).filter(StoryView.story_id == story.id).count()
    }
    for story in stories
    ]

# WebSocket endpoint
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    # Get token from query parameters
    query_params = dict(websocket.query_params)
    token = query_params.get('token')
    
    if not token:
    await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    return
    
    # Verify token
    user = verify_websocket_token(token)
    if not user or user.id != user_id:
    await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    return
    
    await manager.connect(websocket, user_id)
    try:
    while True:
        data = await websocket.receive_text()

        try:
            message_data = json.loads(data)
            message_type = message_data.get('type')

            if message_type == 'typing':
                # Indicador de digitação
                recipient_id = message_data.get('recipient_id')
                if recipient_id:
                    await manager.send_typing_indicator(recipient_id, {
                        "sender_id": user_id,
                        "sender_name": f"{user.first_name} {user.last_name}",
                        "is_typing": message_data.get('is_typing', True)
                    })

            elif message_type == 'message_read':
                # Marcar mensagem como lida
                message_id = message_data.get('message_id')
                if message_id:
                    db = SessionLocal()
                    try:
                        msg = db.query(Message).filter(
                            Message.id == message_id,
                            Message.recipient_id == user_id
                        ).first()

                        if msg and not msg.is_read:
                            msg.is_read = True
                            msg.updated_at = datetime.utcnow()
                            db.commit()

                            # Notificar remetente
                            await manager.send_message_read(msg.sender_id, {
                                "message_id": message_id,
                                "read_by": user_id,
                                "read_at": msg.updated_at.isoformat()
                            })
                    finally:
                        db.close()

            elif message_type == 'heartbeat':
                # Manter conexão viva
                await websocket.send_text(json.dumps({"type": "pong"}))

        except json.JSONDecodeError:
            # Se não for JSON válido, tratar como texto simples
            await manager.send_personal_message(f"Echo: {data}", user_id)

    except WebSocketDisconnect:
    manager.disconnect(websocket, user_id)

# Media upload routes
@app.post("/upload/media", response_model=MediaUploadResponse)
async def upload_media(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Upload de arquivos de mídia"""
    import os
    import uuid
    from pathlib import Path

    # Validar tipo de arquivo
    allowed_types = {
    "image": ["image/jpeg", "image/png", "image/gif", "image/webp"],
    "video": ["video/mp4", "video/webm", "video/avi", "video/mov"],
    "audio": ["audio/mp3", "audio/wav", "audio/ogg", "audio/m4a"],
    "document": ["application/pdf", "text/plain", "application/msword"]
    }

    file_type = None
    for ftype, mimes in allowed_types.items():
    if file.content_type in mimes:
        file_type = ftype
        break

    if not file_type:
    raise HTTPException(status_code=400, detail="File type not supported")

    # Validar tamanho (100MB max)
    if file.size > 100 * 1024 * 1024:
    raise HTTPException(status_code=400, detail="File too large (max 100MB)")

    # Criar diretório se não existe
    upload_dir = Path("uploads") / file_type
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Gerar nome único
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = upload_dir / unique_filename

    # Salvar arquivo
    try:
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Salvar no banco
    db_media = MediaFile(
    filename=unique_filename,
    original_filename=file.filename,
    file_path=str(file_path),
    file_size=file.size,
    mime_type=file.content_type,
    file_type=file_type,
    uploaded_by=current_user.id
    )
    db.add(db_media)
    db.commit()
    db.refresh(db_media)

    return MediaUploadResponse(
    id=db_media.id,
    filename=db_media.filename,
    file_path=f"/uploads/{file_type}/{unique_filename}",
    file_type=db_media.file_type,
    file_size=db_media.file_size,
    mime_type=db_media.mime_type,
    upload_date=db_media.upload_date
    )

@app.get("/uploads/{file_type}/{filename}")
async def serve_media(file_type: str, filename: str):
    """Servir arquivos de mídia"""
    from fastapi.responses import FileResponse
    import os

    file_path = Path("uploads") / file_type / filename

    if not file_path.exists():
    raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path)

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Create tables
Base.metadata.create_all(bind=engine)

# Include enhanced routes
try:
    from enhanced_routes import router as enhanced_router
    app.include_router(enhanced_router, prefix="/api", tags=["enhanced"])
except ImportError:
    print("⚠️ Enhanced routes not loaded (enhanced_routes.py not found)")

# Função para inicializar o banco com dados de exemplo
def init_sample_data():
    db = SessionLocal()
    try:
    # Verifica se já existem usuários
    if db.query(User).count() == 0:
        # Cria usuário de exemplo
        sample_user = User(
            first_name="João",
            last_name="Silva",
            email="joao@exemplo.com",
            password_hash=hash_password("123456"),
            gender="M",
            is_active=True,
            created_at=datetime.utcnow(),
            last_seen=datetime.utcnow()
        )
        db.add(sample_user)
        db.commit()
        db.refresh(sample_user)
        
        # Cria post de exemplo
        sample_post = Post(
            author_id=sample_user.id,
            content="Bem-vindos à nossa rede social! 🎉",
            post_type="post",
            created_at=datetime.utcnow()
        )
        db.add(sample_post)
        db.commit()
        
        print("✅ Dados de exemplo criados com sucesso!")
        print(f"📧 Email: {sample_user.email}")
        print("🔑 Senha: 123456")
    except Exception as e:
    print(f"❌ Erro ao criar dados de exemplo: {e}")
    db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Inicializa dados de exemplo na primeira execução
    init_sample_data()
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

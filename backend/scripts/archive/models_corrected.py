# Corrected Models Section for main.py
# This contains the properly indented models to replace in main.py

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

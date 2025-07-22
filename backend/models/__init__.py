"""
Models initialization - versão limpa e funcional
"""
from .base import Base
from .album import Album, AlbumPhoto
from .block import Block
from .follow import Follow
from .friendship import Friendship
from .media import MediaFile
from .message import Message
from .notification import Notification
from .reaction import Reaction
from .share import Share
from .story import Story

__all__ = [
    "Base",
    "Album", "AlbumPhoto",
    "Block",
    "Follow", 
    "Friendship",
    "MediaFile",
    "Message",
    "Notification",
    "Reaction",
    "Share",
    "Story"
]

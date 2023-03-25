from dataclasses import dataclass
from typing import Optional


@dataclass
class Author:
    id: int
    first_name: str
    last_name: Optional[str]
    username: Optional[str]


@dataclass
class Chat:
    id: int
    type: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    title: Optional[str] = None


@dataclass
class Message:
    mess_id: int
    author: Author
    chat: Chat
    date: int
    text: Optional[str] = "Empty"


@dataclass
class Update:
    update_id: int
    message: Optional[Message] = None

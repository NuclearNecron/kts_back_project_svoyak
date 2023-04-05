from dataclasses import dataclass
from hashlib import sha256
from typing import Optional

from aiohttp_session import Session
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from kts_backend.store.database.database import db


@dataclass
class AdminforRequest:
    id: int
    login: str


@dataclass
class Admin:
    id: int
    login: str
    password: Optional[str] = None

    def is_password_valid(self, password: str) -> bool:
        return self.password == sha256(password.encode()).hexdigest()

    @staticmethod
    def from_session(session: Session | None) -> AdminforRequest | None:
        if session and session["admin"]:
            return AdminforRequest(
                id=session["admin"]["id"], login=session["admin"]["login"]
            )
        return None


class AdminModel(db):
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=True)

    pack = relationship("QuestionPackModel", back_populates="author")

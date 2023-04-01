from dataclasses import dataclass
from hashlib import sha256
from typing import Optional

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from kts_backend.store.database.database import db


@dataclass
class Admin:
    id: int
    email: str
    password: Optional[str] = None

    def is_password_valid(self, password: str) -> bool:
        return self.password == sha256(password.encode()).hexdigest()

    @classmethod
    def from_session(cls, session: Optional[dict]) -> Optional["Admin"]:
        if session:
            return cls(
                id=session["admin"]["id"], email=session["admin"]["email"]
            )
        return None


class AdminModel(db):
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=True)

    pack = relationship("QuestionPackModel", back_populates="author")

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class QuestionPackDC:
    id: int
    name: str
    description: Optional[str]
    user: int


@dataclass
class RoundDC:
    id: int
    pack: int
    number: int


@dataclass
class ThemeDC:
    id: int
    round: int
    name: str


@dataclass
class QuestionDC:
    id: int
    name: str
    description: Optional[str]
    theme: int
    cost: int


@dataclass
class AnswersDC:
    id: int
    question: int
    text: str


@dataclass
class PlayerDC:
    tg_id: int
    name: str
    username: Optional[str]


@dataclass
class GameDC:
    id: int
    state: int
    created_at: datetime
    ended_at: Optional[datetime]
    chat_id: int
    round: int
    winner: Optional[int]
    RemainingQuestions: Optional[list[QuestionDC]]


@dataclass
class GameScoreDC:
    id: int
    player: int
    game: int
    score: int
    right_answers: int
    wrong_answers: int
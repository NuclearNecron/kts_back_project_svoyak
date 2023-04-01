from dataclasses import dataclass
from enum import Enum
from typing import Optional
from datetime import datetime


@dataclass
class QuestionPackDC:
    id: int
    name: str
    admin_id: int
    description: str | None


@dataclass
class RoundDC:
    id: int
    pack_id: int
    number: int


@dataclass
class ThemeDC:
    id: int
    round_id: int
    name: str
    description: str | None


@dataclass
class QuestionDC:
    id: int
    name: str
    theme_id: int
    cost: int


@dataclass
class AnswersDC:
    id: int
    question_id: int
    text: str


@dataclass
class PlayerDC:
    tg_id: int
    name: str
    games_count: int
    win_count: int
    username: str | None


@dataclass
class GameDC:
    id: int
    state: str
    created_at: datetime
    chat_id: int
    round: int
    answer_time: int
    pack: int | None
    winner_id: int | None
    ended_at: datetime | None
    remaining_questions: list[int] | None
    answering_player_tg_id: int | None
    creator: int | None


@dataclass
class GameScoreDC:
    id: int
    player_id: int
    game_id: int
    score: int
    right_answers: int
    wrong_answers: int


class GameState(Enum):
    GAME_INITIALZATION = "GAME_INITIALZATION"
    PLAYER_REGISTRATION = "PLAYER_REGISTRATION"
    START = "START"
    QUESTION_SELECT = "QUESTION_SELECT"
    QUESTION_ANSWERING = "QUESTION_ANSWERING"
    FINISH = "FINISH"


@dataclass
class GameTheme:
    theme: ThemeDC
    questions: list[QuestionDC] | None

from kts_backend.game.dataclasses import *
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    BigInteger,
    Enum,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship


from kts_backend.store.database.database import db


class GameScoreModel(db):
    __tablename__ = "gamescore"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(
        BigInteger,
        ForeignKey("player.tg_id", ondelete="cascade"),
        nullable=False,
    )
    game_id = Column(
        Integer, ForeignKey("game.id", ondelete="cascade"), nullable=False
    )
    score = Column(Integer, nullable=False)
    right_answers = Column(Integer, nullable=False)
    wrong_answers = Column(Integer, nullable=False)

    def to_dc(self) -> GameScoreDC:
        return GameScoreDC(
            id=self.id,
            player_id=self.player_id,
            game_id=self.game_id,
            score=self.score,
            right_answers=self.right_answers,
            wrong_answers=self.wrong_answers,
        )


class PlayerModel(db):
    __tablename__ = "player"

    tg_id = Column(BigInteger, primary_key=True, unique=True)
    name = Column(String, nullable=False)
    username = Column(String, nullable=True)
    scores = relationship(GameScoreModel, backref="player")
    games_count = Column(Integer, nullable=False)
    win_count = Column(Integer, nullable=False)

    def to_dc(self) -> PlayerDC:
        return PlayerDC(
            tg_id=self.tg_id,
            name=self.name,
            username=self.username,
            games_count = self.games_count,
            win_count= self.win_count,
        )


class AnswersModel(db):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(
        Integer, ForeignKey("question.id", ondelete="cascade"), nullable=False
    )
    text = Column(String, nullable=False)

    def to_dc(self) -> AnswersDC:
        return AnswersDC(
            id=self.id,
            question_id=self.question_id,
            text=self.text,
        )


class QuestionModel(db):
    __tablename__ = "question"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    theme_id = Column(
        Integer, ForeignKey("theme.id", ondelete="cascade"), nullable=False
    )
    cost = Column(Integer, nullable=False)
    answers = relationship(AnswersModel, backref="question")

    def to_dc(self) -> QuestionDC:
        return QuestionDC(
            id=self.id,
            name=self.name,
            description=self.description,
            theme_id=self.theme_id,
            cost=self.cost,
        )


class ThemeModel(db):
    __tablename__ = "theme"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    round_id = Column(
        Integer, ForeignKey("round.id", ondelete="cascade"), nullable=False
    )
    questions = relationship(QuestionModel, backref="theme")

    def to_dc(self) -> ThemeDC:
        return ThemeDC(
            id=self.id,
            round_id=self.round_id,
            name=self.name,
        )


class RoundModel(db):
    __tablename__ = "round"

    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(Integer, nullable=False)
    pack_id = Column(
        Integer,
        ForeignKey("questionpack.id", ondelete="cascade"),
        nullable=False,
    )
    themes = relationship(ThemeModel, backref="round")

    def to_dc(self) -> RoundDC:
        return RoundDC(
            id=self.id,
            pack_id=self.pack_id,
            number=self.number,
        )


class QuestionPackModel(db):
    __tablename__ = "questionpack"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    admin_id = Column(
        Integer, ForeignKey("admin.id", ondelete="cascade"), nullable=False
    )
    rounds = relationship(RoundModel, backref="questionpack")

    def to_dc(self) -> QuestionPackDC:
        return QuestionPackDC(
            id=self.id,
            name=self.name,
            description=self.description,
            admin_id=self.admin_id,
        )


class GameModel(db):
    __tablename__ = "game"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False)
    state = Column(String, nullable=False)
    round = Column(Integer, nullable=False)
    winner_id = Column(
        Integer, ForeignKey("player.tg_id", ondelete="cascade"), nullable=True
    )
    created_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    remaining_questions = Column(ARRAY(Integer))
    playerscores = relationship(GameScoreModel, backref="game")

    def to_dc(self) -> GameDC:
        return GameDC(
            id=self.id,
            state=self.state,
            created_at=self.created_at,
            ended_at=self.ended_at,
            chat_id=self.chat_id,
            round=self.round,
            winner_id=self.winner_id,
        )

from kts_backend.game.dataclasses import *
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship


from kts_backend.store.database.database import db








class GameScoreModel(db):
    __tablename__ = "gamescore"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player = Column(
        Integer, ForeignKey("player.tg_id", ondelete="cascade"), nullable=False
    )
    game = Column(
        Integer, ForeignKey("game.id", ondelete="cascade"), nullable=False
    )
    score = Column(Integer, nullable=False)
    right_answers = Column(Integer, nullable=False)
    wrong_answers = Column(Integer, nullable=False)


    def to_dc(self) -> GameScoreDC:
        return GameScoreDC(
            id=self.id,
            player=self.player,
            game=self.game,
            score=self.score,
            right_answers=self.right_answers,
            wrong_answers=self.wrong_answers,
        )


class PlayerModel(db):
    __tablename__ = "player"

    tg_id = Column(Integer, primary_key=True, unique=True)
    name = Column(String, nullable=False)
    username = Column(String, nullable=True)
    scores = relationship(GameScoreModel, backref="player")

    def to_dc(self) -> PlayerDC:
        return PlayerDC(
            tg_id=self.tg_id,
            name=self.name,
            username=self.username,
        )





class AnswersModel(db):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(
        Integer, ForeignKey("question.id", ondelete="cascade"), nullable=False
    )
    text = Column(String, nullable=False)

    def to_dc(self) -> AnswersDC:
        return AnswersDC(
            id=self.id,
            question=self.question,
            text=self.text,
        )


class QuestionModel(db):
    __tablename__ = "question"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    theme = Column(
        Integer, ForeignKey("theme.id", ondelete="cascade"), nullable=False
    )
    cost = Column(Integer, nullable=False)
    answers = relationship(AnswersModel, backref = "question")

    def to_dc(self) -> QuestionDC:
        return QuestionDC(
            id=self.id,
            name=self.name,
            description=self.description,
            theme=self.theme,
            cost=self.cost,
        )


class ThemeModel(db):
    __tablename__ = "theme"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    round = Column(
        Integer, ForeignKey("round.id", ondelete="cascade"), nullable=False
    )
    questions = relationship(QuestionModel, backref= "theme")

    def to_dc(self) -> ThemeDC:
        return ThemeDC(
            id=self.id,
            round=self.round,
            name=self.name,
        )


class RoundModel(db):
    __tablename__ = "round"

    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(Integer, nullable=False)
    pack = Column(
        Integer, ForeignKey("questionpack.id", ondelete="cascade"), nullable=False
    )
    themes = relationship(ThemeModel, backref="round")

    def to_dc(self) -> RoundDC:
        return RoundDC(
            id=self.id,
            pack=self.pack,
            number=self.number,
        )


class QuestionPackModel(db):
    __tablename__ = "questionpack"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    admin = Column(
        Integer, ForeignKey("admin.id", ondelete="cascade"), nullable=False
    )
    rounds = relationship(RoundModel, backref="questionpack")

    def to_dc(self) -> QuestionPackDC:
        return QuestionPackDC(
            id=self.id,
            name=self.name,
            description=self.description,
            user=self.user,
        )


class GameModel(db):
    __tablename__ = "game"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, nullable=False)
    state = Column(Integer, nullable=False)
    round = Column(Integer, nullable=False)
    winner = Column(
        Integer, ForeignKey("admin.id", ondelete="cascade"), nullable=True
    )
    created_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    RemainingQuestions = Column(ARRAY(Integer))
    playerscores = relationship(GameScoreModel, backref="game")

    def to_dc(self) -> GameDC:
        return GameDC(
            id=self.id,
            state=self.state,
            created_at=self.created_at,
            ended_at=self.ended_at,
            chat_id=self.chat_id,
            round=self.round,
            winner=self.winner,
            RemainingQuestions=self.RemainingQuestions,
        )
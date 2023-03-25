# from dataclasses import dataclass
# from datetime import datetime
# from typing import Optional
#
# from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
# from sqlalchemy.orm import relationship
#
# from kts_backend.store.database.database import db
#
#
# @dataclass
# class GameScoreDC:
#     id: int
#     points: int
#     player_id: int
#     game_id: int
#
#
# @dataclass
# class PlayerDC:
#     tg_id: int
#     name: str
#     last_name: Optional[str]
#     username: Optional[str]
#
#
# @dataclass
# class GameDC:
#     id: int
#     state: int
#     created_at: datetime
#     chat_id: int
#
#
# class GameScoreModel(db):
#     __tablename__ = "gamescore"
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     points = Column(Integer, nullable=False)
#     player_id = Column(
#         Integer, ForeignKey("player.tg_id", ondelete="cascade"), nullable=False
#     )
#     game_id = Column(
#         Integer, ForeignKey("game.id", ondelete="cascade"), nullable=False
#     )
#
#     def to_dc(self) -> GameScoreDC:
#         return GameScoreDC(
#             id=self.id,
#             player_id=self.player_id,
#             game_id=self.game_id,
#             points=self.points,
#         )
#
#
# class PlayerModel(db):
#     __tablename__ = "player"
#
#     tg_id = Column(Integer, primary_key=True, unique=True)
#     name = Column(String, nullable=False)
#     last_name = Column(String, nullable=True)
#     username = Column(String, nullable=True)
#     scores = relationship(GameScoreModel, backref="player")
#
#     def to_dc(self) -> PlayerDC:
#         return PlayerDC(
#             tg_id=self.tg_id,
#             name=self.name,
#             last_name=self.last_name,
#             username=self.username,
#         )
#
#
# class GameModel(db):
#     __tablename__ = "game"
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     state = Column(Integer, nullable=False)
#     created_at = Column(DateTime, nullable=False)
#     chat_id = Column(Integer, nullable=False)
#     players = relationship(GameScoreModel, backref="game")
#
#     def to_dc(self) -> GameDC:
#         return GameDC(
#             id=self.id,
#             chat_id=self.chat_id,
#             created_at=self.created_at,
#             state=self.state,
#         )

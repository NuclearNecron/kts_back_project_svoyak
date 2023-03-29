from dataclasses import asdict
from datetime import datetime
from typing import Dict, Optional

import sqlalchemy.exc
from sqlalchemy import select, desc, update
from sqlalchemy.orm import selectinload

from kts_backend.base.base_accessor import BaseAccessor
from kts_backend.game.dataclasses import QuestionPackDC, PlayerDC, RoundDC

from kts_backend.game.models import (
    PlayerModel,
    GameScoreModel,
    GameModel, QuestionPackModel
)


class GameAccessor(BaseAccessor):
    async def create_pack(self,name:str, admin:int,description:Optional[str]=None)->QuestionPackDC | None:
        try:
            async with self.app.database.session() as session:
                new_pack = QuestionPackModel(name=name, admin_id=admin, description=description)
                session.add(new_pack)
                await session.commit()
                return new_pack.to_dc()
        except sqlalchemy.exc.IntegrityError:
            return None

    async def create_player(self, player: PlayerDC) -> PlayerDC | None:
        try:
            async with self.app.database.session() as session:
                new_player = PlayerModel(**asdict(player))
                session.add(new_player)
                await session.commit()
                return new_player.to_dc()
        except sqlalchemy.exc.IntegrityError:
            return None

    async def create_round(self, number: str, pack: int) -> RoundDC | None:
        try:
            async with self.app.database.session() as session:
                new_pack = QuestionPackModel(name=name, admin_id=admin, description=description)
                session.add(new_pack)
                await session.commit()
                return new_pack.to_dc()
        except sqlalchemy.exc.IntegrityError:
            return None

#     async def create_game(
#         self, chat_id: int, created_at: datetime
#     ) -> GameDC | None:
#
#         try:
#             async with self.app.database.session() as session:
#                 new_game = GameModel(
#                     chat_id=chat_id, created_at=created_at, state=1
#                 )
#                 session.add(new_game)
#                 await session.commit()
#                 return new_game.to_dc()
#         except sqlalchemy.exc.IntegrityError:
#             return None
#
#     async def init_player_score(
#         self, player_id: int, game_id: int, points: int = 0
#     ) -> GameScoreDC | None:
#
#         try:
#             async with self.app.database.session() as session:
#                 new_player_score = GameScoreModel(
#                     player_id=player_id, points=points, game_id=game_id
#                 )
#                 session.add(new_player_score)
#                 await session.commit()
#                 return new_player_score.to_dc()
#         except sqlalchemy.exc.IntegrityError:
#             return None
#
#     async def update_player_score(
#         self, player_id: int, game_id: int, new_score: int = 0
#     ) -> None:
#         async with self.app.database.session() as session:
#             query = (
#                 update(GameScoreModel)
#                 .where(
#                     (GameScoreModel.player == player_id)
#                     & (GameModel.game_id == game_id)
#                 )
#                 .values(points=new_score)
#             )
#             await session.execute(query)
#             await session.commit()
#
#     async def assign_player_to_game(
#         self, player: PlayerDC, game_id: int
#     ) -> GameScoreDC | None:
#         await self.create_player(player=player)
#         return await self.init_player_score(
#             player_id=player.tg_id, game_id=game_id
#         )
#
#     async def get_last_game_in_chat(self, chat_id: int | str) -> None | Dict:
#         async with self.app.database.session() as session:
#             query = (
#                 select(GameModel)
#                 .where(GameModel.chat_id == chat_id)
#                 .order_by(desc(GameModel.started_at))
#                 .limit(1)
#             )
#             res = await session.scalars(query)
#             game: GameModel | None = res.one_or_none()
#             if game:
#                 scores_query = (
#                     select(GameScoreModel)
#                     .where(GameScoreModel.game_id == game.id)
#                     .options(selectinload(GameScoreModel.player))
#                 )
#                 res = await session.scalars(scores_query)
#                 players_scores = res.all()
#                 return {
#                     "game": game.to_dc(),
#                     "game_scores": [
#                         {
#                             "player": player_score.players.to_dc(),
#                             "score": player_score.score,
#                         }
#                         for player_score in players_scores
#                     ],
#                 }
#             return None

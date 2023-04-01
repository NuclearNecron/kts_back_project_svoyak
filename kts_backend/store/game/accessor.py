from dataclasses import asdict
from datetime import datetime
from enum import Enum
from typing import Dict, Optional

import sqlalchemy.exc
from sqlalchemy import select, desc, update, delete, func
from sqlalchemy.orm import selectinload

from kts_backend.base.base_accessor import BaseAccessor
from kts_backend.game.dataclasses import (
    QuestionPackDC,
    PlayerDC,
    RoundDC,
    ThemeDC,
    QuestionDC,
    AnswersDC,
    GameDC,
    GameState,
    GameScoreDC,
    GameTheme,
)

from kts_backend.game.models import (
    PlayerModel,
    GameScoreModel,
    GameModel,
    QuestionPackModel,
    RoundModel,
    ThemeModel,
    QuestionModel,
    AnswersModel,
)


class GameAccessor(BaseAccessor):
    async def create_pack(
        self, name: str, admin: int, description: str | None
    ) -> QuestionPackDC | None:
        try:
            async with self.app.database.session() as session:
                new_pack = QuestionPackModel(
                    name=name, admin_id=admin, description=description
                )
                session.add(new_pack)
                await session.commit()
                return new_pack.to_dc()
        except sqlalchemy.exc.IntegrityError:
            return None

    async def create_round(self, number: int, pack: int) -> RoundDC | None:
        try:
            async with self.app.database.session() as session:
                new_round = RoundModel(number=number, pack_id=pack)
                session.add(new_round)
                await session.commit()
                return new_round.to_dc()
        except sqlalchemy.exc.IntegrityError:
            return None

    async def create_theme(
        self, round: int, name: str, description: str | None
    ) -> ThemeDC | None:
        try:
            async with self.app.database.session() as session:
                new_theme = ThemeModel(
                    round_id=round, name=name, description=description
                )
                session.add(new_theme)
                await session.commit()
                return new_theme.to_dc()
        except sqlalchemy.exc.IntegrityError:
            return None

    async def create_question(
        self, theme: int, name: str, cost: int
    ) -> QuestionDC | None:
        try:
            async with self.app.database.session() as session:
                new_question = QuestionModel(
                    theme_id=theme, name=name, cost=cost
                )
                session.add(new_question)
                await session.commit()
                return new_question.to_dc()
        except sqlalchemy.exc.IntegrityError:
            return None

    async def create_answer(self, question: int, text: str) -> AnswersDC | None:
        try:
            async with self.app.database.session() as session:
                new_answer = AnswersModel(question_id=question, text=text)
                session.add(new_answer)
                await session.commit()
                return new_answer.to_dc()
        except sqlalchemy.exc.IntegrityError:
            return None

    async def return_current_game(self, chat_id: int) -> GameDC | None:
        try:
            async with self.app.database.session() as session:
                query = (
                    select(GameModel)
                    .where(
                        (GameModel.chat_id == chat_id)
                        & (GameModel.state != GameState.FINISH.value)
                    )
                    .order_by(GameModel.created_at)
                    .limit(1)
                )
                res = await session.scalars(query)
                if res.one_or_none():
                    return res.one_or_none().to_dc()
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def create_game(
        self,
        chat_id: int,
        player_id: int,
        created_at: datetime = datetime.now(),
    ) -> GameDC | None:
        current_game = await self.return_current_game(chat_id=chat_id)
        if current_game is None:
            try:
                async with self.app.database.session() as session:
                    new_game = GameModel(
                        chat_id=chat_id,
                        created_at=created_at,
                        state=str(GameState.GAME_INITIALZATION.value),
                        round=1,
                        creator=player_id,
                    )
                    session.add(new_game)
                    await session.commit()
                    return new_game.to_dc()
            except sqlalchemy.exc.IntegrityError:
                return None

    async def create_player(
        self, tg_id: int, name: str, username: str | None
    ) -> PlayerDC | None:
        try:
            async with self.app.database.session() as session:
                new_player = PlayerModel(
                    tg_id=tg_id, name=name, username=username
                )
                session.add(new_player)
                await session.commit()
                return new_player.to_dc()
        except sqlalchemy.exc.IntegrityError:
            return None

    async def get_player_by_id(self, tg_id: int) -> PlayerDC | None:
        async with self.app.database.session() as session:
            query = select(PlayerModel).where(PlayerModel.tg_id == tg_id)
            res = await session.scalars(query)
            if res.one_or_none():
                return res.one_or_none().to_dc()
            else:
                return None

    async def add_player_to_game(
        self, player_id: int, game_id: int, points: int = 0
    ) -> GameScoreDC | None:
        try:
            async with self.app.database.session() as session:
                new_player_score = GameScoreModel(
                    player_id=player_id, game_id=game_id
                )
                session.add(new_player_score)
                await session.commit()
                return new_player_score.to_dc()
        except sqlalchemy.exc.IntegrityError:
            return None

    async def update_player_score(
        self, player_id: int, game_id: int, is_correct: bool, add_score: int = 0
    ) -> None:
        try:
            async with self.app.database.session() as session:
                get_query = select(GameScoreModel).where(
                    (GameScoreModel.player_id == player_id)
                    & (GameScoreModel.game_id == game_id)
                )
                get_res = await session.scalars(get_query)
                if get_res.one_or_none():
                    res = get_res.one_or_none().to_dc()
                    if is_correct:
                        upd_query = (
                            update(GameScoreModel)
                            .where(
                                (GameScoreModel.player_id == player_id)
                                & (GameScoreModel.game_id == game_id)
                            )
                            .values(
                                score=res.score + add_score,
                                right_answers=res.right_answers + 1,
                            )
                        )
                    else:
                        upd_query = (
                            update(GameScoreModel)
                            .where(
                                (GameScoreModel.player_id == player_id)
                                & (GameScoreModel.game_id == game_id)
                            )
                            .values(
                                score=res.score - add_score,
                                wrong_answers=res.wrong_answers + 1,
                            )
                        )
                    await session.execute(upd_query)
                    await session.commit()
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def delete_player_from_game(
        self, game_id: int, player_id: int
    ) -> None:
        try:
            async with self.app.database.session() as session:
                query = delete(GameScoreModel).where(
                    (GameScoreModel.player_id == player_id)
                    & (GameScoreModel.game_id == game_id)
                )
                await session.execute(query)
                await session.commit()
                return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def get_game_scores(self, game_id: int) -> list[GameScoreDC] | None:
        try:
            async with self.app.database.session() as session:
                query = (
                    select(GameScoreModel)
                    .where(GameScoreModel.game_id == game_id)
                    .order_by(desc(GameScoreModel.score))
                )
                res = await session.scalars(query)
                if res.all():
                    return [score.to_dc() for score in res.all()]
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def get_player_score(self, game_id: int,player_id:int) -> list[GameScoreDC] | None:
        try:
            async with self.app.database.session() as session:
                query = (
                    select(GameScoreModel)
                    .where((GameScoreModel.game_id == game_id)&(GameScoreModel.player_id==player_id))
                )
                res = await session.scalars(query)
                if res.one_or_none():
                    return res.one_or_none().to_dc()
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def get_amount_of_players(self, game_id: int) -> int | None:
        try:
            async with self.app.database.session() as session:
                query = (
                    select(func.count)
                    .select_from(GameScoreModel)
                    .where(GameScoreModel.game_id == game_id)
                )
                res = await session.scalars(query)
                return res.one_or_none()
        except sqlalchemy.exc.IntegrityError:
            return None

    async def get_random_pack(self, game_id: int) -> QuestionPackDC | None:
        try:
            async with self.app.database.session() as session:
                query = (
                    select(QuestionPackModel)
                    .where(QuestionPackModel.id == func.random())
                    .limit(1)
                )
                res = await session.scalars(query)
                selected_pack = res.one_or_none()
                upd_query = (
                    update(GameModel)
                    .where(GameModel.id == game_id)
                    .values(pack=selected_pack.id)
                )
                await session.execute(upd_query)
                await session.commit()
                return selected_pack.to_dc()
        except sqlalchemy.exc.IntegrityError:
            return None

    async def change_game_status(
        self, game_id: int, status: str
    ) -> bool | None:
        try:
            async with self.app.database.session() as session:
                sq = select(GameModel).where(GameModel.id == game_id)
                res = await session.scalars(sq)
                game = res.one_or_none()
                if game:
                    upd_query = (
                        update(GameModel)
                        .where(GameModel.id == game_id)
                        .values(state=status)
                    )
                    await session.execute(upd_query)
                    await session.commit()
                    return True
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def set_next_round(self, game_id: int) -> bool | None:
        try:
            async with self.app.database.session() as session:
                sq = select(GameModel).where(GameModel.id == game_id)
                res = await session.scalars(sq)
                game = res.one_or_none()
                if game:
                    upd_query = (
                        update(GameModel)
                        .where(GameModel.id == game_id)
                        .values(round=game.round + 1)
                    )
                    await session.execute(upd_query)
                    await session.commit()
                    return True
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def set_answering(
        self, game_id: int, player_id: int | None
    ) -> PlayerDC | None:
        try:
            async with self.app.database.session() as session:
                sq = select(GameModel).where(GameModel.id == game_id)
                res = await session.scalars(sq)
                game = res.one_or_none()
                if game:
                    upd_query = (
                        update(GameModel)
                        .where(GameModel.id == game_id)
                        .values(answering_player_tg_id=player_id)
                    )
                    await session.execute(upd_query)
                    await session.commit()
                    return await self.get_player_by_id(player_id)
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def get_question(self, question_id: int) -> QuestionDC | None:
        try:
            async with self.app.database.session() as session:
                query = select(QuestionModel).where(
                    QuestionModel.id == question_id
                )
                res = await session.scalars(query)
                if res.one_or_none():
                    return res.one_or_none().to_dc()
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def get_round(
        self,
        game_id: int,
    ) -> list[GameTheme] | None:
        try:
            async with self.app.database.session() as session:
                query = select(GameModel).where(GameModel.id == game_id)
                res = await session.scalars(query)
                game = res.one_or_none()
                if game:
                    round_query = select(RoundModel).where(
                        (RoundModel.pack_id == game.pack)
                        & (RoundModel.number == game.round)
                    )
                    roundr = await session.scalars(round_query)
                    roundres = roundr.one_or_none()
                    if roundres:
                        question_query = (
                            select(ThemeModel)
                            .where(ThemeModel.round_id == roundres.id)
                            .options(
                                selectinload(ThemeModel.questions).order_by(
                                    ThemeModel.questions.cost
                                )
                            )
                        )
                        result = await session.scalars(question_query)
                        questions_res = result.all()
                        if questions_res:
                            ret_result = [
                                GameTheme(
                                    theme=theme.to_dc(),
                                    questions=[
                                        question.to_dc()
                                        for question in theme.questions
                                    ],
                                )
                                for theme in questions_res
                            ]
                            return ret_result
                        else:
                            return None
                    else:
                        return None
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def dump_question(
        self, game_id: int, questions: list[int] | None
    ) -> bool | None:
        try:
            async with self.app.database.session() as session:
                sq = select(GameModel).where(GameModel.id == game_id)
                res = await session.scalars(sq)
                game = res.one_or_none()
                if game:
                    upd_query = (
                        update(GameModel)
                        .where(GameModel.id == game_id)
                        .values(remaining_questions=questions)
                    )
                    await session.execute(upd_query)
                    await session.commit()
                    return True
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def delete_game(self, game_id: int) -> None:
        try:
            async with self.app.database.session() as session:
                query = delete(GameModel).where(GameModel.id == game_id)
                await session.execute(query)
                await session.commit()
                return None
        except sqlalchemy.exc.IntegrityError:
            return None

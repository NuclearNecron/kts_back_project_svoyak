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
    PlayerScore,
    RoundComplex,
    FullQuestion,
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
        self, name: str, admin: int, description: str | None = None
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

    async def create_round(self, pack: int) -> RoundDC | None:
        try:
            async with self.app.database.session() as session:
                query = (
                    select(func.count())
                    .select_from(RoundModel)
                    .where(RoundModel.pack_id == pack)
                )
                res = await session.scalars(query)
                amount = res.one_or_none()
                new_round = RoundModel(number=amount + 1, pack_id=pack)
                session.add(new_round)
                await session.commit()
                return new_round.to_dc()
        except sqlalchemy.exc.IntegrityError:
            return None

    async def create_theme(
        self, round: int, name: str, description: str | None = None
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
                result = res.one_or_none()
                if result:
                    return result.to_dc()
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def return_last_game(self, chat_id: int) -> GameDC | None:
        try:
            async with self.app.database.session() as session:
                query = (
                    select(GameModel)
                    .where(GameModel.chat_id == chat_id)
                    .order_by(desc(GameModel.created_at))
                    .limit(1)
                )
                res = await session.scalars(query)
                result = res.one_or_none()
                if result:
                    return result.to_dc()
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
                except Exception as inst:
                    print(type(inst))  # the exception instance
                    print(inst.args)  # arguments stored in .args
                    print(inst)
            except sqlalchemy.exc.IntegrityError:
                return None

    async def create_player(
        self, tg_id: int, name: str, username: str | None = None
    ) -> PlayerDC | None:
        try:
            async with self.app.database.session() as session:
                new_player = PlayerModel(
                    tg_id=tg_id, name=name, username=username
                )
                session.add(new_player)
                await session.commit()
                print(new_player.to_dc())
                return new_player.to_dc()
        except sqlalchemy.exc.IntegrityError:
            return None

    async def get_player_by_id(self, tg_id: int) -> PlayerDC | None:
        async with self.app.database.session() as session:
            query = select(PlayerModel).where(PlayerModel.tg_id == tg_id)
            res = await session.scalars(query)
            answer = res.one_or_none()
            if answer:
                return answer.to_dc()
            else:
                return None

    async def change_player_games(
        self, player_id: int, added: bool
    ) -> bool | None:
        try:
            async with self.app.database.session() as session:
                player = await self.get_player_by_id(player_id)
                if player:
                    if added:
                        upd_query = (
                            update(PlayerModel)
                            .where(PlayerModel.tg_id == player_id)
                            .values(games_count=player.games_count + 1)
                        )
                    else:
                        upd_query = (
                            update(PlayerModel)
                            .where(PlayerModel.tg_id == player_id)
                            .values(games_count=player.games_count - 1)
                        )
                    await session.execute(upd_query)
                    await session.commit()
                    return None
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def make_player_winner(self, player_id: int) -> bool | None:
        try:
            async with self.app.database.session() as session:
                player = await self.get_player_by_id(player_id)
                if player:
                    upd_query = (
                        update(PlayerModel)
                        .where(PlayerModel.tg_id == player_id)
                        .values(win_count=player.win_count + 1)
                    )
                    await session.execute(upd_query)
                    await session.commit()
                    return True
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def set_winner(self, game_id: int, player_id: int) -> PlayerDC | None:
        try:
            async with self.app.database.session() as session:
                sq = select(GameModel).where(GameModel.id == game_id)
                res = await session.scalars(sq)
                game = res.one_or_none()
                if game:
                    upd_query = (
                        update(GameModel)
                        .where(GameModel.id == game_id)
                        .values(winner_id=player_id)
                    )
                    await session.execute(upd_query)
                    await session.commit()
                    await self.make_player_winner(player_id)
                    return await self.get_player_by_id(player_id)
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def add_player_to_game(
        self, player_id: int, game_id: int
    ) -> GameScoreDC | None:
        try:
            async with self.app.database.session() as session:
                new_player_score = GameScoreModel(
                    player_id=player_id, game_id=game_id
                )
                session.add(new_player_score)
                await session.commit()
                await self.change_player_games(player_id, True)
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
                answer1 = get_res.one_or_none()
                if answer1:
                    res = answer1.to_dc()
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
                await self.change_player_games(player_id, False)
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
                results = res.all()
                if results:
                    return [score.to_dc() for score in results]
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def get_player_score(
        self, game_id: int, player_id: int
    ) -> GameScoreDC | None:
        try:
            async with self.app.database.session() as session:
                query = select(GameScoreModel).where(
                    (GameScoreModel.game_id == game_id)
                    & (GameScoreModel.player_id == player_id)
                )
                res = await session.scalars(query)
                result = res.one_or_none()
                if result:
                    return result.to_dc()
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def get_amount_of_players(self, game_id: int) -> int | None:
        try:
            async with self.app.database.session() as session:
                query = (
                    select(func.count())
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
                    select(QuestionPackModel).order_by(func.random()).limit(1)
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
        self, game_id: int, player_id: int | None = None
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
                result = res.one_or_none()
                if result:
                    return result.to_dc()
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
                            .options(selectinload(ThemeModel.questions))
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

    async def get_game_scores_with_players(
        self, game_id: int
    ) -> list[PlayerScore] | None:
        try:
            async with self.app.database.session() as session:
                query = (
                    select(GameScoreModel)
                    .where(GameScoreModel.game_id == game_id)
                    .options(selectinload(GameScoreModel.player))
                    .order_by(desc(GameScoreModel.score))
                )
                res = await session.scalars(query)
                results = res.all()
                if results:
                    ret_result = [
                        PlayerScore(
                            score=score.to_dc(), player=score.player.to_dc()
                        )
                        for score in results
                    ]
                    print("''''''")
                    print(ret_result)
                    print("''''''")
                    return ret_result
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def dump_question(
        self, game_id: int, questions: list[int] | None = None
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

    async def check_answer(
        self, question_id: int, requested_answer: str
    ) -> bool | None:
        try:
            async with self.app.database.session() as session:
                query = select(AnswersModel).where(
                    AnswersModel.question_id == question_id
                )
                res = await session.scalars(query)
                result = res.all()
                list_of_answers = [
                    answer.to_dc().text.lower() for answer in result
                ]
                if requested_answer.lower() in list_of_answers:
                    return True
                else:
                    return False
        except sqlalchemy.exc.IntegrityError:
            return None

    async def remove_from_remaining(
        self, game_id: int, question_id: int
    ) -> bool | None:
        try:
            async with self.app.database.session() as session:
                question_list = await self.get_remaining_questions(game_id)
                if question_list:
                    question_list.remove(question_id)
                    res = await self.dump_question(
                        game_id=game_id, questions=question_list
                    )
                    if res:
                        return True
                    else:
                        return None
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def get_questions_from_remaining(
        self, game_id
    ) -> list[GameTheme] | None:
        try:
            async with self.app.database.session() as session:
                question_list = await self.get_remaining_questions(game_id)
                if question_list:
                    query1 = (
                        (
                            select(ThemeModel).join(
                                QuestionModel,
                                ThemeModel.id == QuestionModel.theme_id,
                            )
                        )
                        .filter(QuestionModel.id.in_(question_list))
                        .group_by(ThemeModel.id)
                    )
                    query2 = (
                        select(QuestionModel)
                        .where(QuestionModel.id.in_(question_list))
                        .order_by(QuestionModel.cost)
                    )
                    resulttheme = await session.scalars(query1)
                    theme_res = resulttheme.all()
                    resultquest = await session.scalars(query2)
                    quest_res = resultquest.all()
                    print(theme_res, quest_res)
                    if theme_res and quest_res:
                        ret_result = [
                            GameTheme(
                                theme=ThemeDC(
                                    id=theme.id,
                                    round_id=theme.round_id,
                                    name=theme.name,
                                    description=theme.description,
                                ),
                                questions=[
                                    QuestionDC(
                                        id=question.id,
                                        name=question.name,
                                        theme_id=question.theme_id,
                                        cost=question.cost,
                                    )
                                    for question in quest_res
                                    if question.theme_id == theme.id
                                ],
                            )
                            for theme in theme_res
                        ]
                        print(ret_result)
                        return ret_result
                    else:
                        return None
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def get_remaining_questions(self, game_id: int) -> list[int] | None:
        try:
            async with self.app.database.session() as session:
                query = select(GameModel).where(GameModel.id == game_id)
                res = await session.scalars(query)
                result = res.one_or_none()
                if result:
                    remaining_questions = result.to_dc().remaining_questions
                    if remaining_questions:
                        return remaining_questions
                    else:
                        return None
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def check_player_in_game(
        self, game_id: int, player_id: int
    ) -> PlayerDC | None:
        try:
            async with self.app.database.session() as session:
                query = select(GameScoreModel).where(
                    (GameScoreModel.game_id == game_id)
                    & (GameScoreModel.player_id == player_id)
                )
                res = await session.scalars(query)
                result = res.one_or_none()
                if result:
                    return result.to_dc()
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def set_current_question(
        self, game_id: int, question: int | None = None
    ) -> bool | None:
        try:
            async with self.app.database.session() as session:
                upd_query = (
                    update(GameModel)
                    .where(GameModel.id == game_id)
                    .values(current_question=question)
                )
                await session.execute(upd_query)
                await session.commit()
                return True
        except sqlalchemy.exc.IntegrityError:
            return None

    async def get_pack(self) -> list[QuestionPackDC] | None:
        try:
            async with self.app.database.session() as session:
                query = select(QuestionPackModel)
                res = await session.scalars(query)
                result = res.all()
                if result:
                    return [pack.to_dc() for pack in result]
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def get_rounds(self, pack: int) -> list[RoundComplex] | None:
        try:
            async with self.app.database.session() as session:
                query = (
                    select(RoundModel)
                    .where(RoundModel.pack_id == pack)
                    .options(selectinload(RoundModel.themes))
                )
                res = await session.scalars(query)
                result = res.all()
                if result:
                    return [
                        RoundComplex(
                            round=round.to_dc(),
                            themes=[theme.to_dc() for theme in round.themes],
                        )
                        for round in result
                    ]
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def get_themes(self, round_id: int) -> list[GameTheme] | None:
        try:
            async with self.app.database.session() as session:
                query = (
                    select(ThemeModel)
                    .where(ThemeModel.round_id == round_id)
                    .options(selectinload(ThemeModel.questions))
                )
                res = await session.scalars(query)
                result = res.all()
                if result:
                    return [
                        GameTheme(
                            theme=theme.to_dc(),
                            questions=[
                                question.to_dc() for question in theme.questions
                            ],
                        )
                        for theme in result
                    ]
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def get_questions(self, theme_id: int) -> list[FullQuestion] | None:
        try:
            async with self.app.database.session() as session:
                query = (
                    select(QuestionModel)
                    .where(QuestionModel.theme_id == theme_id)
                    .options(selectinload(QuestionModel.answers))
                )
                res = await session.scalars(query)
                result = res.all()
                if result:
                    return [
                        FullQuestion(
                            question=question.to_dc(),
                            answer=[
                                answer.to_dc() for answer in question.answers
                            ],
                        )
                        for question in result
                    ]
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def check_pack(self, admin_id: int, pack: int) -> bool | None:
        try:
            async with self.app.database.session() as session:
                query = select(QuestionPackModel).where(
                    (QuestionPackModel.admin_id == admin_id)
                    & (QuestionPackModel.id == pack)
                )
                res = await session.scalars(query)
                result = res.one_or_none()
                if result:
                    return True
                else:
                    return False
        except sqlalchemy.exc.IntegrityError:
            return None

    async def get_single_pack(self, pack_id: int) -> QuestionPackDC | None:
        try:
            async with self.app.database.session() as session:
                query = select(QuestionPackModel).where(
                    QuestionPackModel.id == pack_id
                )
                res = await session.scalars(query)
                result = res.one_or_none()
                if result:
                    return result.to_dc()
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def get_single_round(self, round_id: int) -> bool | None:
        try:
            async with self.app.database.session() as session:
                query = select(RoundModel).where(RoundModel.id == int(round_id))
                res = await session.scalars(query)
                result = res.one_or_none()
                if result:
                    return True
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def check_round(self, admin_id: int, round_id: int) -> bool | None:
        try:
            async with self.app.database.session() as session:
                query = (
                    select(RoundModel)
                    .options(selectinload(RoundModel.pack))
                    .where(
                        (QuestionPackModel.admin_id == admin_id)
                        & (RoundModel.id == round_id)
                    )
                )
                res = await session.scalars(query)
                result = res.one_or_none()
                if result:
                    return True
                else:
                    return False
        except sqlalchemy.exc.IntegrityError:
            return None

    async def get_single_theme(self, theme_id: int) -> bool | None:
        try:
            async with self.app.database.session() as session:
                query = select(ThemeModel).where(ThemeModel.id == int(theme_id))
                res = await session.scalars(query)
                result = res.one_or_none()
                if result:
                    return True
                else:
                    return None
        except sqlalchemy.exc.IntegrityError:
            return None

    async def check_theme(self, admin_id: int, theme_id: int) -> bool | None:
        try:
            async with self.app.database.session() as session:
                query = (
                    select(ThemeModel)
                    .options(selectinload(ThemeModel.round).subqueryload(RoundModel.pack))
                    .where(
                        (QuestionPackModel.admin_id == admin_id)
                        & (ThemeModel.id == theme_id)
                    )
                )
                res = await session.scalars(query)
                result = res.one_or_none()
                if result:
                    return True
                else:
                    return False
        except sqlalchemy.exc.IntegrityError:
            return None

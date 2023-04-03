from asyncio import Task
from enum import Enum
from typing import Optional

import typing
import asyncio

from kts_backend.game.dataclasses import GameState, GameDC
from kts_backend.store.bot.api.dataclasses import (
    CallbackQueryUpdate,
    MessageUpdate,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    MessageEntity,
    MessageToSend,
    answerCallbackQuery,
    CallbackQuery,
)

if typing.TYPE_CHECKING:
    from kts_backend.web.app import Application


class Updater:
    def __init__(self, app: "Application"):
        self.app = app
        self.is_running = False
        self.handle_task: Optional[Task] = None

    async def start(self):
        print("manager init")
        self.is_running = True
        self.handle_task = asyncio.create_task(self.handle_update())

    async def stop(self):
        self.is_running = False
        self.handle_task.cancel()

    class Commands(Enum):
        STARTGAME = "/startgame"
        PARTICIPATE = "/participate"
        FINISHGAME = "/finishgame"
        GAMESTATS = "/gamestats"
        LEFTGAME = "/leftgame"
        PLAYERSTAT = "/playerstat"

    async def handle_update(self):
        while self.is_running:
            message = await self.app.store.work_queue.get()
            try:
                self.app.logger.info(f"Manager: Новое сообщение {message}")
                if type(message) is CallbackQueryUpdate:
                    await self.handle_callbackquery(message)
                elif type(message) is MessageUpdate:
                    await self.handle_message(message)
            except Exception as inst:
                self.app.logger.error(
                    "Manager: Была получена ошибка:", exc_info=inst
                )
            finally:
                self.app.store.work_queue.task_done()

    async def handle_message(self, message: MessageUpdate):
        if message.message.text.startswith("/"):
            command = message.message.text.split("@")
            if len(command) == 1 or command[1] == "necron_alex_game_bot":
                await self.handle_command(message)
        else:
            await self.handle_text_message(message)

    async def handle_command(self,message:MessageUpdate):
        match message.message.text.split('@')[0]:
            case self.Commands.STARTGAME.value:
                await self.handle_start_game(message)
            case self.Commands.PARTICIPATE.value:
                await self.handle_participate(message)
            case self.Commands.GAMESTATS.value:
                await self.handle_game_stat(message)
            case self.Commands.FINISHGAME.value:
                await self.handle_manual_finish_game(message)
            case self.Commands.LEFTGAME.value:
                await self.handle_leave(message)
            case self.Commands.PLAYERSTAT.value:
                await self.handle_playerstat(message)
            case _:
                await self.handle_wrong_command(message)

    async def handle_start_game(self, message: MessageUpdate):
        player = await self.app.store.game.get_player_by_id(
            message.message.from_user.id
        )
        if player == None:
            await self.app.store.game.create_player(
                tg_id=message.message.from_user.id,
                name=message.message.from_user.first_name,
                username=message.message.from_user.username,
            )
        new_game = await self.app.store.game.create_game(
            chat_id=message.message.chat.id,
            player_id=message.message.from_user.id,
        )
        self.app.logger.info(f"Manager: Текущая игра:{new_game} ")
        if new_game:
            await self.handle_to_queue(
                chat_id=message.message.chat.id,
                message_thread_id=message.message.message_thread_id,
                text=f"Игра №{new_game.id} была создана. Для участия в ней напишите /participate",
            )
            await self.app.store.game.change_game_status(
                new_game.id, GameState.PLAYER_REGISTRATION.value
            )
            await self.handle_participate(message)
            asyncio.create_task(
                self.handle_start_initialization(
                    game_id=new_game.id,
                    chat_id=message.message.chat.id,
                    owner_id=message.message.from_user.id,
                    message_thread_id=message.message.message_thread_id,
                )
            )
        else:
            await self.handle_to_queue(
                chat_id=message.message.chat.id,
                message_thread_id=message.message.message_thread_id,
                text=f"Новая игра не была создана, так как предыдущая игра не была закончена.",
            )

    async def handle_participate(self, message: MessageUpdate):
        game = await self.app.store.game.return_current_game(
            message.message.chat.id
        )
        if game:
            if GameState(game.state) == GameState.PLAYER_REGISTRATION:
                player = await self.app.store.game.get_player_by_id(
                    message.message.from_user.id
                )
                if player == None:
                    await self.app.store.game.create_player(
                        tg_id=message.message.from_user.id,
                        name=message.message.from_user.first_name,
                        username=message.message.from_user.username,
                    )
                new_player_score = await self.app.store.game.add_player_to_game(
                    player_id=message.message.from_user.id, game_id=game.id
                )
                if new_player_score:
                    await self.handle_to_queue(
                        chat_id=message.message.chat.id,
                        message_thread_id=message.message.message_thread_id,
                        reply_to_message_id=message.message.message_id,
                        text=f"Игрок {message.message.from_user.username if message.message.from_user.username else message.message.from_user.first_name} вступил в игру.",
                    )
                else:
                    await self.handle_to_queue(
                        chat_id=message.message.chat.id,
                        message_thread_id=message.message.message_thread_id,
                        reply_to_message_id=message.message.message_id,
                        text=f"Игрок {message.message.from_user.username if message.message.from_user.username else message.message.from_user.first_name} уже вступил в игру ранее.",
                    )
            else:
                await self.handle_to_queue(
                    chat_id=message.message.chat.id,
                    message_thread_id=message.message.message_thread_id,
                    reply_to_message_id=message.message.message_id,
                    text=f"Игра идет в данный момент, невозможно присоедениться!",
                )
        else:
            await self.handle_to_queue(
                chat_id=message.message.chat.id,
                message_thread_id=message.message.message_thread_id,
                reply_to_message_id=message.message.message_id,
                text=f"В данный момент в чате не проходит ни одной игры!",
            )

    async def handle_start_initialization(
        self,
        game_id: int,
        chat_id: int,
        owner_id: int,
        message_thread_id: int | None = None,
        time_to_start: int = 30,
        min_number_of_players: int = 1,
    ) -> None:
        await asyncio.sleep(time_to_start)
        current_amount_of_players = (
            await self.app.store.game.get_amount_of_players(game_id)
        )
        if current_amount_of_players < min_number_of_players:
            await self.app.store.game.delete_game(game_id)
            await self.handle_to_queue(
                chat_id=chat_id,
                message_thread_id=message_thread_id,
                text=f"Игра была отменена из-за нехватки участникв.",
            )
        else:
            await self.app.store.game.change_game_status(
                game_id, GameState.START.value
            )
            await self.app.store.game.get_random_pack(game_id)
            questionres = await self.app.store.game.get_round(game_id)
            question_list = []
            for theme in questionres:
                for question in theme.questions:
                    question_list.append(question.id)
            inline_keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=theme.theme.name,
                            callback_data=f"""Описание темы: {theme.theme.description if theme.theme.description else "Нет описания"}.""",
                        )
                    ]
                    + [
                        InlineKeyboardButton(
                            text=question.cost,
                            callback_data=f"{question.id};{len(question_list)}",
                        )
                        for question in theme.questions
                    ]
                    for theme in questionres
                ]
            )
            await self.app.store.game.dump_question(
                game_id=game_id, questions=question_list
            )
            data = await self.app.store.tgapi.send_inline_keyboard(
                inline_keyboard=inline_keyboard,
                chat_id=chat_id,
                message_thread_id=message_thread_id,
                text="Вопросы для выбора",
            )
            await self.app.store.game.change_game_status(
                game_id, GameState.QUESTION_SELECT.value
            )
            answering = await self.app.store.game.set_answering(
                game_id=game_id, player_id=owner_id
            )
            if answering:
                await self.handle_to_queue(
                    chat_id=chat_id,
                    message_thread_id=message_thread_id,
                    text=f"Игру начинает {answering.username if answering.username else answering.name}",
                )
            else:
                await self.handle_to_queue(
                    chat_id=chat_id,
                    message_thread_id=message_thread_id,
                    text=f"Не удалось выбрать отвечающего игрока. УВЫ. Перезапустите игру.",
                )

    async def handle_leave(self, message: MessageUpdate):
        game = await self.app.store.game.return_current_game(
            message.message.chat.id
        )
        if game:
            player = await self.app.store.game.get_player_by_id(
                message.message.from_user.id
            )
            if player:
                player_score = await self.app.store.game.get_player_score(
                    player_id=message.message.from_user.id, game_id=game.id
                )
                if player_score:
                    await self.app.store.game.delete_player_from_game(
                        game_id=game.id, player_id=message.message.from_user.id
                    )
                    await self.handle_to_queue(
                        chat_id=message.message.chat.id,
                        message_thread_id=message.message.message_thread_id,
                        reply_to_message_id=message.message.message_id,
                        text=f"Игрок {message.message.from_user.username if message.message.from_user.username else message.message.from_user.first_name} покинул игру.",
                    )
                else:
                    await self.handle_to_queue(
                        chat_id=message.message.chat.id,
                        message_thread_id=message.message.message_thread_id,
                        reply_to_message_id=message.message.message_id,
                        text=f"Вы не можете покинуть игру, так как не учавтсвуете в ней",
                    )
            else:
                await self.handle_to_queue(
                    chat_id=message.message.chat.id,
                    message_thread_id=message.message.message_thread_id,
                    reply_to_message_id=message.message.message_id,
                    text=f"Вы не можете покинуть игру так как объект вашего пользователля не был создан, для его получения, поучавствуйте в игре хотя бы раз.",
                )
        else:
            await self.handle_to_queue(
                chat_id=message.message.chat.id,
                message_thread_id=message.message.message_thread_id,
                reply_to_message_id=message.message.message_id,
                text=f"В данный момент в чате не проходит ни одной игры!",
            )

    async def handle_manual_finish_game(self, message: MessageUpdate):
        game = await self.app.store.game.return_current_game(
            message.message.chat.id
        )
        if game:
            if game.creator == message.message.from_user.id:
                await self.handle_to_queue(
                    chat_id=message.message.chat.id,
                    message_thread_id=message.message.message_thread_id,
                    reply_to_message_id=message.message.message_id,
                    text=f"Вы завершили игру вручную",
                )
                await self.handle_finish_game(game_id=game.id)
            else:
                await self.handle_to_queue(
                    chat_id=message.message.chat.id,
                    message_thread_id=message.message.message_thread_id,
                    reply_to_message_id=message.message.message_id,
                    text=f"Вы не можете завершить игру, так как не являетесь её создателем",
                )
        else:
            await self.handle_to_queue(
                chat_id=message.message.chat.id,
                message_thread_id=message.message.message_thread_id,
                reply_to_message_id=message.message.message_id,
                text=f"В данный момент в чате не проходит ни одной игры!",
            )

    async def handle_wrong_command(self, message: MessageUpdate):
        await self.handle_to_queue(
            chat_id=message.message.chat.id,
            message_thread_id=message.message.message_thread_id,
            reply_to_message_id=message.message.message_id,
            text=f"Такой команды не существует",
        )

    async def handle_finish_game(self, game_id: int):
        await self.app.store.game.dump_question(game_id=game_id, questions=[])
        await self.app.store.game.change_game_status(
            game_id=game_id, status=GameState.FINISH.value
        )
        # TO DO Сделать постановку победителя и вызов статистики

    async def handle_playerstat(self, message: MessageUpdate):
        await self.handle_to_queue(
            chat_id=message.message.chat.id,
            message_thread_id=message.message.message_thread_id,
            text=f"Метод не имплементирован в проект еще.",
        )

    async def handle_text_message(self, message: MessageUpdate):
        await self.handle_to_queue(
            chat_id=message.message.chat.id,
            message_thread_id=message.message.message_thread_id,
            text=f"Метод не имплементирован в проект еще.",
        )

    async def handle_game_stat(self, message: MessageUpdate):
        # todo сделать таблицу лидеров.
        await self.handle_to_queue(
            chat_id=message.message.chat.id,
            message_thread_id=message.message.message_thread_id,
            text=f"Метод не имплементирован в проект еще.",
        )

    async def handle_callbackquery(self, callback: CallbackQueryUpdate):
        callback_query = callback.callback_query
        game = await self.app.store.game.return_current_game(
            callback_query.message.chat.id
        )
        if game:
            callback_data = callback_query.data
            if "Описание" in callback_data:
                await self.handle_to_queue(
                    chat_id=callback_query.message.chat.id,
                    message_thread_id=callback_query.message.message_thread_id,
                    text=callback_data,
                )
                await self.app.store.tgapi.answerCallbackQuery(
                    answerCallbackQuery(
                        callback_query_id=callback_query.id,
                        text=callback_data,
                        show_alert=True,
                    )
                )
            elif "join" in callback_data:
                await self.handle_set_answering(game, callback_query)
            else:
                await self.handle_choosing_question(game, callback_query)

    async def handle_set_answering(self, game: GameDC, callback: CallbackQuery):
        if (
            game.answering_player_tg_id is None
            and game.state == GameState.QUESTION_ANSWERING.value
        ):
            await self.app.store.game.set_answering(
                game_id=game.id, player_id=callback.from_user.id
            )
            await asyncio.sleep(game.answer_time)
            current_game_state = await self.app.store.game.return_current_game(
                callback.message.chat.id
            )
            if current_game_state.state == GameState.QUESTION_ANSWERING.value:
                if (
                    current_game_state.current_question == game.current_question
                    and current_game_state.answering_player_tg_id
                    == game.answering_player_tg_id
                ):
                    question = await self.app.store.game.get_question(
                        current_game_state.current_question
                    )
                    await self.app.store.game.update_player_score(
                        player_id=callback.from_user.id,
                        game_id=game.id,
                        is_correct=False,
                        add_score=question.cost,
                    )
                    await self.app.store.game.set_answering(game_id=game.id)
                    await self.app.store.tgapi.answerCallbackQuery(
                        answerCallbackQuery(
                            callback_query_id=callback.id,
                            text="Истекло время ответа на вопрос.",
                            show_alert=True,
                        )
                    )
                    await self.handle_to_queue(
                        chat_id=callback.message.chat.id,
                        message_thread_id=callback.message.message_thread_id,
                        text=f"Истекло время ответа на вопрос. Вы получаете -{question.cost} очков",
                    )
            await self.app.store.tgapi.answerCallbackQuery(
                answerCallbackQuery(
                    callback_query_id=callback.id,
                    text="Игрок перестал отвечать до конца ожидания",
                    show_alert=False,
                )
            )
        else:
            await self.app.store.tgapi.answerCallbackQuery(
                answerCallbackQuery(
                    callback_query_id=callback.id,
                    text="Нельзя стать отвечающим в данный момент",
                    show_alert=False,
                )
            )

    async def handle_choosing_question(self, game:GameDC, callback:CallbackQuery):
        if (
            game.answering_player_tg_id == callback.from_user.id
            and game.state == GameState.QUESTION_SELECT.value
        ):
            callback_data = callback.data.split(";")
            if len(game.remaining_questions) == int(callback_data[1]):
                await self.app.store.game.change_game_status(game.id, GameState.QUESTION_ANSWERING.value)
                await self.app.store.game.set_current_question(game_id=game.id,question=int(callback_data[0]))
                await self.app.store.game.set_answering(game_id=game.id)
                while True:
                    await asyncio.sleep(game.answer_time)
                    current_game_state = await self.app.store.game.return_current_game(
                        callback.message.chat.id
                    )
                    if (current_game_state.state==GameState.QUESTION_ANSWERING.value
                            and current_game_state.answering_player_tg_id is None
                            and current_game_state.current_question == int(callback_data[0])):
                        await self.app.store.game.change_game_status(game.id, GameState.QUESTION_SELECT.value)
                        await self.app.store.game.set_current_question(game_id=game.id)
                        await self.app.store.game.remove_from_remaining(game_id=game.id, question_id=int(callback_data[0]))
                        await self.app.store.game.set_answering(game_id=game.id,player_id=callback.from_user.id)
                        if len(current_game_state.remaining_questions)!=1:
                            questions = await self.app.store.game.get_questions_from_remaining(game_id=game.id)
                            inline_keyboard = InlineKeyboardMarkup(
                                inline_keyboard=[
                                    [
                                        InlineKeyboardButton(
                                            text=theme.theme.name,
                                            callback_data=f"""Описание темы: {theme.theme.description if theme.theme.description else "Нет описания"}.""",
                                        )
                                    ]
                                    + [
                                        InlineKeyboardButton(
                                            text=question.cost,
                                            callback_data=f"{question.id};{len(current_game_state.remaining_questions)-1}",
                                        )
                                        for question in theme.questions
                                    ]
                                    for theme in questions
                                ]
                            )
                            data = await self.app.store.tgapi.send_inline_keyboard(
                                inline_keyboard=inline_keyboard,
                                chat_id=callback.message.chat.id,
                                message_thread_id=callback.message.message_thread_id,
                                text="Вопросы для выбора",
                            )
                            await self.handle_to_queue(
                                chat_id=callback.message.chat.id,
                                message_thread_id=callback.message.message_thread_id,
                                text=f"Выбирайте вопрос, {callback.from_user.username if callback.from_user.username else callback.from_user.first_name}",
                            )
                            await self.app.store.tgapi.answerCallbackQuery(
                                answerCallbackQuery(
                                    callback_query_id=callback.id,
                                    text="Вопрос не был отвечен",
                                    show_alert=False,
                                )
                            )
                            break
                        else:
                            await self.app.store.tgapi.answerCallbackQuery(
                                answerCallbackQuery(
                                    callback_query_id=callback.id,
                                    text="Вопрос был отвечен",
                                    show_alert=False,
                                )
                            )
                            break
                    else:
                        await self.app.store.tgapi.answerCallbackQuery(
                            answerCallbackQuery(
                                callback_query_id=callback.id,
                                text="Вопрос был отвечен",
                                show_alert=False,
                            )
                        )
                        break
            else:
                await self.app.store.tgapi.answerCallbackQuery(
                    answerCallbackQuery(
                        callback_query_id=callback.id,
                        text="Нельзя выбрать вопрос в данный момент",
                        show_alert=False,
                    )
                )
        else:
            await self.app.store.tgapi.answerCallbackQuery(
                answerCallbackQuery(
                    callback_query_id=callback.id,
                    text="Нельзя выбрать вопрос в данный момент",
                    show_alert=False,
                )
            )

    async def handle_to_queue(
        self,
        chat_id: int,
        text: str,
        message_thread_id: int | None = None,
        parse_mode: str | None = None,
        entities: typing.List[MessageEntity] | None = None,
        disable_notification: bool | None = None,
        reply_to_message_id: int | None = None,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> None:
        new_message = MessageToSend(
            chat_id=chat_id,
            message_thread_id=message_thread_id,
            text=text,
            parse_mode=parse_mode,
            entities=entities,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
        )
        print(new_message)
        await self.app.store.send_queue.put(
            MessageToSend(
                chat_id=chat_id,
                message_thread_id=message_thread_id,
                text=text,
                parse_mode=parse_mode,
                entities=entities,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id,
                reply_markup=reply_markup,
            )
        )

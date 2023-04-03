from dataclasses import dataclass
from typing import List


@dataclass
class User:
    id: int
    is_bot: bool
    first_name: str
    last_name: str | None
    username: str | None


@dataclass
class Chat:
    id: int
    type: str
    title: str | None


@dataclass
class Message:
    message_id: int
    from_user: User | None
    chat: Chat
    date: int
    text: str | None
    message_thread_id: int | None


@dataclass
class MessageUpdate:
    update_id: int
    message: Message


@dataclass
class InlineKeyboardButton:
    text: str
    callback_data: str


@dataclass
class InlineKeyboardMarkup:
    inline_keyboard: List[List[InlineKeyboardButton]]


@dataclass
class CallbackQuery:
    id: str
    from_user: User
    message: Message
    chat_instance: str
    data: str


@dataclass
class answerCallbackQuery:
    callback_query_id: str
    text: str | None
    show_alert: bool | None


@dataclass
class MessageEntity:
    type: str
    offset: int
    length: int
    url: str | None
    user: User | None
    language: str | None
    custom_emoji_id: str | None


@dataclass
class MessageToSend:
    chat_id: int
    message_thread_id: int | None
    text: str
    parse_mode: str | None
    entities: List[MessageEntity] | None
    disable_notification: bool | None
    reply_to_message_id: int | None
    reply_markup: InlineKeyboardMarkup | None


@dataclass
class CallbackQueryUpdate:
    update_id: int
    callback_query: CallbackQuery

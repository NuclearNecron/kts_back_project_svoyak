from marshmallow import Schema, fields, EXCLUDE, post_load

from kts_backend.store.bot.api.dataclasses import (
    MessageUpdate,
    Message,
    Chat,
    User,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    answerCallbackQuery,
    CallbackQuery,
    CallbackQueryUpdate,
    MessageEntity,
    MessageToSend,
)


class UserSchema(Schema):
    id = fields.Integer(required=True)
    is_bot = fields.Boolean(required=True)
    first_name = fields.String(required=True)
    last_name = fields.String(load_default=None)
    username = fields.String(load_default=None)

    @post_load
    def dump_User(self, data, **kwargs):
        return User(**data)


class ChatSchema(Schema):
    id = fields.Integer(required=True)
    type = fields.String(required=True)
    title = fields.String(load_default=None)

    @post_load
    def dump_Chat(self, data, **kwargs):
        return Chat(**data)


class MessageSchema(Schema):
    message_id = fields.Integer(required=True)
    message_thread_id = fields.Integer(load_default=None)
    from_user = fields.Nested(
        UserSchema, data_key="from", unknown=EXCLUDE, load_default=None
    )
    chat = fields.Nested(ChatSchema, required=True, unknown=EXCLUDE)
    date = fields.Integer(required=True)
    text = fields.String(load_default=None)

    @post_load
    def dump_Message(self, data, **kwargs):
        return Message(**data)


class MessageUpdateSchema(Schema):
    update_id = fields.Integer(required=True)
    message = fields.Nested(MessageSchema, required=True, unknown=EXCLUDE)

    @post_load
    def dump_MessageUpdate(self, data, **kwargs):
        return MessageUpdate(**data)


class InlineKeyboardButtonSchema(Schema):
    text = fields.String(required=True)
    callback_data = fields.String(required=True)

    @post_load
    def dump_InlineKeyboardButton(self, data, **kwargs):
        return InlineKeyboardButton(**data)


class InlineKeyboardMarkupSchema(Schema):
    inline_keyboard = fields.List(
        fields.List(
            fields.Nested(
                InlineKeyboardButtonSchema, required=True, unknown=EXCLUDE
            ),
            required=True,
        ),
        required=True,
    )

    @post_load
    def dump_InlineKeyboardMarkup(self, data, **kwargs):
        return InlineKeyboardMarkup(**data)


class CallbackQuerySchema(Schema):
    id = fields.String(required=True)
    from_user = fields.Nested(UserSchema, data_key="from", unknown=EXCLUDE)
    message = fields.Nested(MessageSchema, required=True, unknown=EXCLUDE)
    chat_instance = fields.String(required=True)
    data = fields.String(required=True)

    @post_load
    def dump_CallbackQuery(self, data, **kwargs):
        return CallbackQuery(**data)


class answerCallbackQuerySchema(Schema):
    callback_query_id = fields.Integer(required=True)
    text = fields.String(required=False, load_default=None)
    show_alert = fields.Bool(required=False, load_default=None)

    @post_load
    def dump_answerCallbackQuery(self, data, **kwargs):
        return answerCallbackQuery(**data)


class MessageEntitySchema(Schema):
    type = fields.String(required=True)
    offset = fields.Integer(required=True)
    length = fields.Integer(required=True)
    url = fields.String(required=False, load_default=None)
    user = fields.Nested(
        UserSchema, required=False, load_default=None, unknown=EXCLUDE
    )
    language = fields.String(required=False, load_default=None)
    custom_emoji_id = fields.String(required=False, load_default=None)

    @post_load
    def dump_MessageEntity(self, data, **kwargs):
        return MessageEntity(**data)


class MessageToSendSchema(Schema):
    chat_id = fields.Integer(required=True)
    message_thread_id = fields.Integer(load_default=None)
    text = fields.String(required=True)
    parse_mode = fields.String(load_default=None)
    entities = fields.List(
        fields.Nested(MessageEntitySchema), required=False, load_default=None
    )
    disable_notification = fields.Boolean(load_default=None)
    reply_to_message_id = fields.Integer(load_default=None)
    reply_markup = fields.Nested(InlineKeyboardMarkupSchema, load_default=None)


class CallbackQueryUpdateSchema(Schema):
    update_id = fields.Integer(required=True)
    callback_query = fields.Nested(
        CallbackQuerySchema, required=True, unknown=EXCLUDE
    )

    @post_load
    def dump_CallbackQueryUpdate(self, data, **kwargs):
        return CallbackQueryUpdate(**data)

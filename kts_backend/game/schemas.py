from marshmallow import Schema, fields


class PackSchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str(required=False)


class RoundSchema(Schema):
    pack_id = fields.Int(required=True)


class ThemeSchema(Schema):
    name = fields.Str(required=True)
    round_id = fields.Int(required=True)
    description = fields.Str(required=False)


class AnswerSchema(Schema):
    text = fields.Str(required=True)


class QuestionSchema(Schema):
    name = fields.Str(required=True)
    theme_id = fields.Int(required=True)
    cost = fields.Int(required=True)
    answers = fields.List(
        fields.Nested(AnswerSchema, required=True), required=True
    )

class ListGamesRequestSchema(Schema):
    games_on_page = fields.Int(required=False, load_default=5)
    page = fields.Int(required=False, load_default=1)


class GameResponseSchema(Schema):
    id = fields.Int(required=True)
    state = fields.Str(required=True)
    created_at = fields.DateTime(required=True, format="iso")
    ended_at = fields.DateTime(required=False, format="iso")
    chat_id = fields.Int(required=True)
    round=fields.Int(required=True)
    answer_time = fields.Int(required=True)
    pack = fields.Int(required=True)
    winner_id = fields.Int(required=False)
    remaining_questions = fields.List(fields.Int(),required=False)
    answering_player_tg_id = fields.Int(required=False)
    creator = fields.Int(required=False)
    current_question = fields.Int(required=False)

from marshmallow import Schema, fields


class PackSchema(Schema):
    name = fields.Int(required=True)
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
    answers = fields.List(fields.Nested(AnswerSchema,required=True),required=True)

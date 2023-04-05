from aiohttp.web_exceptions import (
    HTTPUnauthorized,
    HTTPConflict,
    HTTPBadRequest,
    HTTPForbidden, HTTPNotFound,
)

from kts_backend.game.schemas import PackSchema, RoundSchema, ThemeSchema, QuestionSchema
from kts_backend.web.app import View
from aiohttp_apispec import (
    request_schema,
    response_schema,
    docs,
    cookies_schema,
)

from kts_backend.web.mixin import AuthRequiredMixin
from kts_backend.web.schemas import OkResponseSchema
from kts_backend.web.utils import json_response


class PackCreate(AuthRequiredMixin, View):
    @docs(
        tags=["game"],
        summary="create pack",
        description="create new pack with name and description",
    )
    @request_schema(PackSchema)
    @response_schema(OkResponseSchema)
    async def post(self):

        if self.request.admin is None:
            raise HTTPUnauthorized
        if self.data["name"] is None:
            raise HTTPBadRequest
        admin = self.request.admin
        new_pack = await self.request.app.store.game.create_pack(
            name=self.data["name"],
            description=self.data["description"],
            admin=admin.id,
        )
        if new_pack is None:
            raise HTTPConflict
        return json_response(
            data={
                "id": new_pack.id,
                "name": new_pack.name,
                "description": new_pack.description,
                "admin_id": new_pack.admin_id,
            }
        )


class GetPacks(AuthRequiredMixin, View):
    @docs(
        tags=["game"],
        summary="check all packs",
        description="add admin into system using ",
    )
    @response_schema(OkResponseSchema)
    async def get(self):
        if self.request.admin is None:
            raise HTTPUnauthorized
        packs = await self.request.app.store.game.get_pack()
        return json_response(
            data={
                "packs": [
                    {
                        "id": pack.id,
                        "name": pack.name,
                        "description": pack.description,
                        "admin_id": pack.admin_id,
                    }
                    for pack in packs
                ]
            }
        )


class RoundCreate(AuthRequiredMixin, View):
    @docs(
        tags=["game"],
        summary="create round",
        description="create new round with autonumber",
    )
    @request_schema(RoundSchema)
    @response_schema(OkResponseSchema)
    async def post(self):
        if self.request.admin is None:
            raise HTTPUnauthorized
        if self.data["pack_id"] is None:
            raise HTTPBadRequest
        admin = self.request.admin
        existence = await self.request.app.store.game.get_single_pack(
            pack_id=int(self.data["pack_id"])
        )
        if existence is None:
            raise HTTPNotFound
        ownership = await self.request.app.store.game.check_pack(
            admin_id=admin.id, pack=int(self.data["pack_id"])
        )
        if not ownership:
            raise HTTPForbidden
        else:
            new_round = await self.request.app.store.game.create_round(
                pack=int(self.data["pack_id"])
            )
            if new_round is None:
                raise HTTPConflict
            return json_response(
                data={
                    "id": new_round.id,
                    "number": new_round.number,
                    "pack_id": new_round.pack_id,
                }
            )
class RoundGet(AuthRequiredMixin, View):
    @docs(
        tags=["game"],
        summary="view rounds",
        description="returns rounds of pack",
    )
    @response_schema(OkResponseSchema)
    async def get(self):
        if self.request.admin is None:
            raise HTTPUnauthorized
        try:
            if self.request.query["pack_id"] is None:
                raise HTTPBadRequest
        except KeyError:
            raise HTTPBadRequest
        admin = self.request.admin
        pack_id = self.request.query["pack_id"]
        existence = await self.request.app.store.game.get_single_pack(
            pack_id=int(pack_id)
        )
        if existence is None:
            raise HTTPNotFound
        rounds = await self.request.app.store.game.get_rounds(pack=int(pack_id))
        return json_response(
                data={"rounds":[
                    {
                        "id":round.round.id,
                        "number":round.round.number,
                        "pack_id":round.round.pack_id,
                        "themes":[{
                            "id":theme.id,
                            "name":theme.name,
                            "round_id":theme.round_id,
                            "description":theme.description,
                        }for theme in round.themes]
                    }for round in rounds]}
            )


class ThemeCreate(AuthRequiredMixin, View):
    @docs(
        tags=["game"],
        summary="create theme",
        description="create new theme with name and description",
    )
    @request_schema(ThemeSchema)
    @response_schema(OkResponseSchema)
    async def post(self):
        if self.request.admin is None:
            raise HTTPUnauthorized
        if self.data["round_id"] is None or self.data["name"] is None:
            raise HTTPBadRequest
        admin = self.request.admin
        existence = await self.request.app.store.game.get_single_round(
            pack_id=self.data["round_id"]
        )
        if existence is None:
            raise HTTPNotFound
        ownership = await self.request.app.store.game.check_round(
            admin_id=admin.id, round_id=int(self.data["round_id"])
        )
        if not ownership:
            raise HTTPForbidden
        else:
            new_theme = await self.request.app.store.game.create_theme(
                round=int(self.data["pack_id"]),
                name = self.data["name"],
                description=self.data["description"]
            )
            if new_theme is None:
                raise HTTPConflict
            return json_response(
                data={
                    "id": new_theme.id,
                    "name": new_theme.name,
                    "description": new_theme.description,
                    "round_id": new_theme.round_id
                }
            )

class ThemeGet(AuthRequiredMixin, View):
    @docs(
        tags=["game"],
        summary="view themes",
        description="returns themes of round",
    )
    @response_schema(OkResponseSchema)
    async def get(self):
        if self.request.admin is None:
            raise HTTPUnauthorized
        try:
            round_id = int(self.request.query["round_id"])
        except KeyError:
            raise HTTPBadRequest
        existence = await self.request.app.store.game.get_single_round(
            round_id=round_id
        )
        if existence is None:
            raise HTTPNotFound
        themes = await self.request.app.store.game.get_themes(round_id=round_id)
        return json_response(
                data={"themes":[
                    {
                        "id":theme.theme.id,
                        "name":theme.theme.name,
                        "rounds_id":theme.theme.round_id,
                        "description":theme.theme.description,
                        "questions":[{
                            "id":question.id,
                            "name":question.name,
                            "cost":question.cost,
                        }for question in theme.questions]
                    }for theme in themes]}
            )

class QuestionCreate(AuthRequiredMixin, View):
    @docs(
        tags=["game"],
        summary="create question and answers",
        description="create new question with respectful answers",
    )
    @request_schema(QuestionSchema)
    @response_schema(OkResponseSchema)
    async def post(self):
        if self.request.admin is None:
            raise HTTPUnauthorized
        try:
            admin = self.request.admin
            existence = await self.request.app.store.game.get_single_theme(
                theme_id=self.data["theme_id"]
            )
            if existence is None:
                raise HTTPNotFound
            ownership = await self.request.app.store.game.check_theme(
                admin_id=admin.id, theme_id=int(self.data["theme_id"])
            )
            if not ownership:
                raise HTTPForbidden
            else:
                answers = self.data["answers"]
                new_question = await self.request.app.store.game.create_question(
                    theme=int(self.data["theme_id"]),
                    name=self.data["name"],
                    cost=self.data["cost"]
                )
                if new_question is None:
                    raise HTTPConflict
        except KeyError:
            raise HTTPBadRequest
        else:
            new_answers = []
            for answer in answers:
                new_answer = await self.request.app.store.game.create_answer(question=new_question.id, text=answer["text"])
                new_answers.append(new_answer)
        return json_response(
            data={
                "id": new_question.id,
                "name": new_question.name,
                "cost": new_question.description,
                "theme_id": new_question.theme_id,
                "answers":[{"text":answer.text}for answer in new_answers]
            }
        )



class QuestionGet(AuthRequiredMixin, View):
    @docs(
        tags=["game"],
        summary="view question",
        description="returns question with answers",
    )
    @response_schema(OkResponseSchema)
    async def get(self):
        if self.request.admin is None:
            raise HTTPUnauthorized
        try:
            theme_id = int(self.request.query["theme_id"])
        except KeyError:
            raise HTTPBadRequest
        existence = await self.request.app.store.game.get_single_theme(
            theme_id=theme_id
        )
        if existence is None:
            raise HTTPNotFound
        questions = await self.request.app.store.game.get_questions(theme_id=theme_id)
        return json_response(
                data={"questions":[
                    {
                        "id":question.question.id,
                        "name":question.question.name,
                        "theme_id":question.question.theme_id,
                        "cost":question.question.cost,
                        "answers":[{
                            "id":answer.id,
                            "text":answer.text,
                        }for answer in question.answer]
                    }for question in questions]}
            )
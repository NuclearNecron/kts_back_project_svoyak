from aiohttp.web_exceptions import HTTPForbidden, HTTPUnauthorized
from aiohttp_apispec import (
    request_schema,
    response_schema,
    docs,
    cookies_schema,
)
from aiohttp_session import new_session

from kts_backend.admin.schema import AdminSchema
from kts_backend.web.app import View
from kts_backend.web.mixin import AuthRequiredMixin
from kts_backend.web.schemas import OkResponseSchema, CookieSchema
from kts_backend.web.utils import json_response


class AdminLoginView(View):
    @docs(
        tags=["admin"],
        summary="login as admin",
        description="login as admin into system",
    )
    @request_schema(AdminSchema)
    @cookies_schema(CookieSchema)
    @response_schema(OkResponseSchema)
    async def post(self):
        logindata = await self.request.app.store.admin.get_by_login(
            self.data["login"]
        )
        if logindata is None:
            raise HTTPForbidden
        admin_data = {"id": logindata.id, "login": logindata.login}
        if "password" in self.data and logindata.is_password_valid(
            self.data["password"]
        ):
            session = await new_session(request=self.request)
            session["admin"] = admin_data
            return json_response(data=admin_data)
        elif logindata.password is None:
            session = await new_session(request=self.request)
            session["admin"] = admin_data
            return json_response(data=admin_data)
        raise HTTPForbidden


class AdminCurrentView(AuthRequiredMixin, View):
    @docs(
        tags=["admin"],
        summary="Get admin data",
        description="Return info about current admin",
    )
    @cookies_schema(CookieSchema)
    @response_schema(OkResponseSchema)
    async def get(self):
        if self.request.admin is not None:
            return json_response(
                data={
                    "id": self.request.admin.id,
                    "login": self.request.admin.login,
                }
            )
        raise HTTPUnauthorized


class AdminCreate(View):
    @docs(
        tags=["admin"],
        summary="create admin",
        description="add admin into system using ",
    )
    @request_schema(AdminSchema)
    @response_schema(OkResponseSchema)
    async def post(self):
        admin = await self.request.app.store.admin.create_admin(
            login=self.data["login"],
            password=self.data["password"],
        )
        return json_response(data={"id": admin.id, "login": admin.login})

from typing import Sequence, Callable, Optional

from aiohttp.web import (
    Application as AiohttpApplication,
    View as AiohttpView,
    Request as AiohttpRequest,
)


from kts_backend import __appname__

# __version__
from .config import Config, setup_config
from .urls import register_urls


__all__ = ("Application",)

from kts_backend.store import Store, setup_store
from kts_backend.store.database.database import Database


class Application(AiohttpApplication):
    config: Optional[Config] = None
    store: Optional[Store] = None
    database: Optional[Database] = None


class Request(AiohttpRequest):
    # user: Optional[User] = None

    @property
    def app(self) -> Application:
        return super().app()


class View(AiohttpView):
    @property
    def request(self) -> Request:
        return super().request

    @property
    def database(self):
        return self.request.app.database

    @property
    def store(self) -> Store:
        return self.request.app.store

    @property
    def data(self) -> dict:
        return self.request.get("data", {})


app = Application()


def setup_app(config_path: str) -> Application:
    setup_config(app, config_path)
    # setup_logging(app)
    # session_setup(app, EncryptedCookieStorage(app.config.session.key))
    # setup_routes(app)
    # setup_aiohttp_apispec(
    #     app, title="Vk Quiz Bot", url="/docs/json", swagger_path="/docs"
    # )
    # setup_middlewares(app)
    setup_store(app)
    return app

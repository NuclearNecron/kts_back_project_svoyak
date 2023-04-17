from aiohttp.web_app import Application
from aiohttp_cors import CorsConfig


__all__ = ("register_urls",)

from kts_backend.game.views import ListGames


def register_urls(application: Application):
    from kts_backend.game.views import GetPacks
    from kts_backend.game.views import PackCreate

    application.router.add_view("/pack.create", PackCreate)
    application.router.add_view("/pack.view", GetPacks)
    from kts_backend.game.views import RoundCreate

    application.router.add_view("/round.create", RoundCreate)
    from kts_backend.game.views import RoundGet

    application.router.add_view("/round.view", RoundGet)
    from kts_backend.game.views import ThemeCreate

    application.router.add_view("/theme.create", ThemeCreate)
    from kts_backend.game.views import ThemeGet

    application.router.add_view("/theme.view", ThemeGet)
    from kts_backend.game.views import QuestionCreate

    application.router.add_view("/question.create", QuestionCreate)
    from kts_backend.game.views import QuestionGet

    application.router.add_view("/question.view", QuestionGet)

    application.router.add_view("/games.list", ListGames)

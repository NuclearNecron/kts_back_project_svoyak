from aiohttp.web_app import Application
from aiohttp_cors import CorsConfig

__all__ = ("register_urls",)


def register_urls(application: Application):
    import kts_backend.admin.urls
    import kts_backend.game.urls

    kts_backend.admin.urls.register_urls(application)
    # kts_backend.game.urls.register_urls(application)

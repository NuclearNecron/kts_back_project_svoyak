from aiohttp.web_app import Application
from aiohttp_cors import CorsConfig


__all__ = ("register_urls",)


def register_urls(application: Application):
    from kts_backend.admin.views import AdminLoginView
    from kts_backend.admin.views import AdminCreate
    from kts_backend.admin.views import AdminCurrentView

    application.router.add_view("/admin.login", AdminLoginView)
    application.router.add_view("/admin.current", AdminCurrentView)
    application.router.add_view("/admin.create", AdminCreate)

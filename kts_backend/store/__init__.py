import typing
from asyncio.queues import Queue

from kts_backend.store.bot.api.accessor import TGApi
from kts_backend.store.bot.bot.manager import BotApi
from kts_backend.store.database.database import Database

if typing.TYPE_CHECKING:
    from kts_backend.web.app import Application


class Store:
    def __init__(self, app: "Application"):
        from kts_backend.store.admin.accessor import AdminAccessor

        self.admin = AdminAccessor(app)
        self.work_queue = Queue()
        self.send_queue = Queue()
        self.tgapi = TGApi(app, app.config.tgbot.token)
        self.tgbot = BotApi(app)


def setup_store(app: "Application"):
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)
    app.store = Store(app)

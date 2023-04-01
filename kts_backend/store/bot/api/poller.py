from asyncio import Task
from typing import Optional

import typing
import asyncio

from marshmallow import EXCLUDE

from kts_backend.store.bot.api.schemes import (
    MessageUpdateSchema,
    CallbackQueryUpdateSchema,
)

if typing.TYPE_CHECKING:
    from kts_backend.web.app import Application


class Poller:
    def __init__(self, app: "Application"):
        self.app = app
        self.is_running = False
        self.poll_task: Optional[Task] = None

    async def start(self):
        self.app.logger.info("Starting Poller")
        self.is_running = True
        self.poll_task = asyncio.create_task(self.poll())

    async def stop(self):
        self.is_running = False
        self.poll_task.cancel()

    async def poll(self):
        offset = 0
        while self.is_running:
            results = await self.app.store.tgapi.poll(offset, timeout=20)
            updates = results["updates"]
            offset = results["new_offset"]
            for upd in updates:
                self.app.logger.info(
                    f"Poller. Было получено новое сообщение:{upd}"
                )
                if "message" in upd:
                    update = MessageUpdateSchema().load(upd, unknown=EXCLUDE)
                    await self.app.store.work_queue.put(update)
                elif "callback_query" in upd:
                    update = CallbackQueryUpdateSchema().load(
                        upd, unknown=EXCLUDE
                    )
                    await self.app.store.work_queue.put(update)

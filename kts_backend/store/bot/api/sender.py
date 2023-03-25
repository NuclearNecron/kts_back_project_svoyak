from asyncio import Task
from typing import Optional

import typing
import asyncio

if typing.TYPE_CHECKING:
    from kts_backend.store import Store


class Sender:
    def __init__(self, store: "Store"):
        self.store = store
        self.is_running = False
        self.send_task: Optional[Task] = None

    async def start(self):
        self.is_running = True
        self.send_task = asyncio.create_task(self.send())

    async def stop(self):
        self.is_running = False
        await self.store.send_queue.join()
        self.send_task.cancel()

    async def send(self):
        while self.is_running:
            message = await self.store.send_queue.get()
            try:
                print("sending messgae")
                await self.store.tgapi.send_message(
                    message.message.chat.id, message.message.text
                )
            finally:
                self.store.send_queue.task_done()

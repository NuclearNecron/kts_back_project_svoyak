from asyncio import Task
from typing import Optional

import typing
import asyncio

if typing.TYPE_CHECKING:
    from kts_backend.store import Store


class Updater:
    def __init__(self, store: "Store"):
        self.store = store
        self.is_running = False
        self.handle_task: Optional[Task] = None

    async def start(self):
        print("manager init")
        self.is_running = True
        self.handle_task = asyncio.create_task(self.handle_update())

    async def stop(self):
        self.is_running = False
        self.handle_task.cancel()

    async def handle_update(self):
        while self.is_running:
            message = await self.store.work_queue.get()
            print("message", message)
            try:
                await self.store.send_queue.put(message)
            finally:
                print("moved to send")
                self.store.work_queue.task_done()

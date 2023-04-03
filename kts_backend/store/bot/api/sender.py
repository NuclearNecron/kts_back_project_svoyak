from asyncio import Task
from typing import Optional

import typing
import asyncio

if typing.TYPE_CHECKING:
    from kts_backend.web.app import Application


class Sender:
    def __init__(self, app: "Application"):
        self.app = app
        self.is_running = False
        self.send_task: Optional[Task] = None

    async def start(self):
        self.is_running = True
        self.app.logger.info(f"SENDER. Инициализация отправщика")
        self.send_task = asyncio.create_task(self.send())

    async def stop(self):
        self.is_running = False
        await self.app.store.send_queue.join()
        self.send_task.cancel()

    async def send(self):
        while self.is_running:
            message = await self.app.store.send_queue.get()
            try:
                self.app.logger.info(f"SENDER. Отправляю сообщение {message}")
                await self.app.store.tgapi.send_message(message)
            except Exception as inst:
                self.app.logger.error(
                    "Sender: Была получена ошибка:", exc_info=inst
                )
            finally:
                self.app.store.send_queue.task_done()

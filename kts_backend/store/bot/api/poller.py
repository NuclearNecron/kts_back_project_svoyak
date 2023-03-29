from asyncio import Task
from typing import Optional

import typing
import asyncio

if typing.TYPE_CHECKING:
    from kts_backend.web.app import Application


class Poller:
    def __init__(self, app: "Application"):
        self.app = app
        self.is_running = False
        self.poll_task: Optional[Task] = None

    async def start(self):
        self.is_running = True
        self.poll_task = asyncio.create_task(self.poll())

    async def stop(self):
        self.is_running = False
        self.poll_task.cancel()

    async def poll(self):
        offset = 0
        while self.is_running:
            print("poll")
            results = await self.app.store.tgapi.poll(offset, timeout=20)
            for result in results:
                print(type(result))
                offset = result.update_id + 1
                try:
                    print("added ", result.update_id)
                    await self.app.store.work_queue.put(result)
                except Exception as inst:
                    self(type(inst))  # the exception instance
                    print(inst.args)  # arguments stored in .args
                    print(inst)
                finally:
                    print("added to Queue")

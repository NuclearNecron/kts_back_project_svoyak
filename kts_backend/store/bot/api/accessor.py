from typing import Optional, TYPE_CHECKING
from aiohttp import ClientSession

from kts_backend.base.base_accessor import BaseAccessor
from kts_backend.store.bot.api.dataclasses import (
    Update,
    Message,
    Author,
    Chat,
)
from kts_backend.store.bot.api.poller import Poller
from kts_backend.store.bot.api.sender import Sender

TELEGRAM_HOST = "https://api.telegram.org"

if TYPE_CHECKING:
    from kts_backend.web.app import Application


class TGApi(BaseAccessor):
    def __int__(self, app: "Application", token: str = "", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.token = Optional[str] = ""
        self.client: Optional[ClientSession] = None
        self.poller: Optional[Poller] = None
        self.sender: Optional[Sender] = None

    async def connect(self, app: "Application"):
        self.client = ClientSession()
        self.poller = Poller(self.app.store)
        self.token = self.app.config.tgbot.token
        await self.poller.start()
        self.sender = Sender(self.app.store)
        await self.sender.start()

    async def disconnect(self, app: "Application"):
        await self.client.close()
        await self.poller.stop()
        await self.sender.stop()
        self.client = None

    def build_url(self, method: str, params: Optional[dict] = None):
        url = TELEGRAM_HOST + "/bot" + self.token + "/" + method + "?"
        url += "&".join([f"{param}={value}" for param, value in params.items()])
        return url

    async def poll(self, offset: Optional[int] = None, timeout: int = 0):
        params = {}
        if offset:
            params["offset"] = offset
        if timeout:
            params["timeout"] = timeout
        url = self.build_url("getUpdates", params=params)
        print("start listening")
        async with self.client.get(url) as response:
            print("receive update")
            data = await response.json()
            updatedata = data["result"]
            print("start format")
            try:
                res = [
                    Update(
                        update_id=update["update_id"],
                        message=Message(
                            mess_id=update["message"]["message_id"],
                            author=Author(
                                id=update["message"]["from"]["id"],
                                first_name=update["message"]["from"][
                                    "first_name"
                                ],
                                last_name=update["message"]["from"]["last_name"]
                                if "key" in update["message"]["from"]
                                else None,
                                username=update["message"]["from"]["username"],
                            ),
                            chat=Chat(
                                id=update["message"]["chat"]["id"],
                                type=update["message"]["chat"]["type"],
                                first_name=update["message"]["chat"][
                                    "first_name"
                                ],
                                last_name=update["message"]["chat"]["last_name"]
                                if "key" in update["message"]["chat"]
                                else None,
                                username=update["message"]["chat"]["username"],
                                title=update["message"]["chat"]["title"]
                                if "key" in update["message"]["chat"]
                                else None,
                            ),
                            date=update["message"]["date"],
                            text=update["message"]["text"],
                        ),
                    )
                    for update in updatedata
                ]
            except Exception as inst:
                print(type(inst))  # the exception instance
                print(inst.args)  # arguments stored in .args
                print(inst)
            print(res)
            return res

    async def send_message(self, chat_id: int, text: str):
        params = {
            "chat_id": chat_id,
            "text": text,
        }
        print(params)
        url = self.build_url("sendMessage", params)
        async with self.client.get(url) as response:
            data = await response.json()

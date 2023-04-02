import json
from typing import Optional, TYPE_CHECKING
from aiohttp import ClientSession

from kts_backend.base.base_accessor import BaseAccessor
from kts_backend.store.bot.api.dataclasses import (
    MessageToSend,
    InlineKeyboardMarkup,
    answerCallbackQuery,
)
from kts_backend.store.bot.api.poller import Poller
from kts_backend.store.bot.api.schemes import (
    MessageToSendSchema,
    answerCallbackQuerySchema,
)
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
        self.poller = Poller(self.app)
        self.token = self.app.config.tgbot.token
        await self.poller.start()
        self.sender = Sender(self.app)
        await self.sender.start()

    async def disconnect(self, app: "Application"):
        await self.client.close()
        await self.poller.stop()
        await self.sender.stop()
        self.client = None

    def build_url(self, method: str, params: Optional[dict] = None):
        url = TELEGRAM_HOST + "/bot" + self.token + "/" + method + "?"
        url += "&".join(
            [
                f"{param}={value}"
                for param, value in params.items()
                if value
                and param != "allowed_updates"
                and param != "reply_markup"
            ]
        )
        if "reply_markup" in params and params["reply_markup"]:
            url += "&reply_markup=" + json.dumps(params["reply_markup"])
        if "allowed_updates" in params and len(params["allowed_updates"]) > 0:
            url += "&allowed_updates=" + ",".join(params["allowed_updates"])
        print(url)
        return url

    async def poll(self, offset: Optional[int] = None, timeout: int = 0):
        params = {"limit": 50, "allowed_updates": []}
        if offset:
            params["offset"] = offset
        if timeout:
            params["timeout"] = timeout
        url = self.build_url("getUpdates", params=params)
        async with self.client.get(url) as response:
            data = await response.json()
            try:
                updatedata = data["result"]
                return {
                    "updates": updatedata,
                    "new_offset": updatedata[-1]["update_id"] + 1,
                }
            except IndexError:
                self.logger.info("Poller: Новых сообщений не было получено")
                return {"updates": [], "new_offset": offset}
            except Exception as inst:
                self.logger.error(
                    "Poller: Была получена ошибка:", exc_info=inst
                )

    async def send_message(self, message: MessageToSend):
        params = MessageToSendSchema().dump(message)
        self.app.logger.info(
            f"Sender: Отправляю сообщение с содержимым {params}"
        )
        url = self.build_url("sendMessage", params)
        async with self.client.get(url) as response:
            data = await response.json()
            self.app.logger.info(f"Sender: Получил ответ в виде {data}")
            return data

    async def send_inline_keyboard(
        self,
        inline_keyboard: InlineKeyboardMarkup,
        text: str,
        chat_id: str | int,
        message_thread_id: int | None = None,
    ):
        self.app.logger.info(
            "Sender: Получено сообщение с экранной клавиатурой"
        )
        message = MessageToSend(
            chat_id=chat_id,
            message_thread_id=message_thread_id,
            text=text,
            parse_mode=None,
            entities=None,
            disable_notification=False,
            reply_to_message_id=None,
            reply_markup=inline_keyboard,
        )
        data = await self.send_message(message)
        return data

    async def answerCallbackQuery(self, answer: answerCallbackQuery):
        url = self.build_url(
            method="answerCallbackQuery",
            params=answerCallbackQuerySchema().dump(answer),
        )
        async with self.client.get(url) as response:
            return None

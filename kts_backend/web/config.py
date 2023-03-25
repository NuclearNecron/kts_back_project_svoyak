import typing
from dataclasses import dataclass
import yaml


if typing.TYPE_CHECKING:
    from .app import Application

__all__ = ("Config", "setup_config")


@dataclass
class VKBotConfig:
    token: str
    group_id: int


@dataclass
class TGBotConfig:
    token: str


@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    user: str = "gameadmin"
    password: str = "123"
    database: str = "gamedatabase"


@dataclass
class Config:
    vkbot: VKBotConfig = None
    tgbot: TGBotConfig = None
    database: DatabaseConfig = None


def setup_config(app: "Application", config_path: str):
    with open(config_path, "r") as f:
        raw_config = yaml.safe_load(f)

    app.config = Config(
        vkbot=VKBotConfig(
            token=raw_config["bot"]["vk"]["token"],
            group_id=raw_config["bot"]["vk"]["group_id"],
        ),
        tgbot=TGBotConfig(
            token=raw_config["bot"]["tg"]["token"],
        ),
        database=DatabaseConfig(**raw_config["database"]),
    )

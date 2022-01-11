from hikari import Intents
from lightbulb import BotApp
from lavasnek_rs import Lavalink

from os import environ
from src.db import Database
from dotenv import load_dotenv


class Bot(BotApp):
    def __init__(self, debug: bool = False):
        load_dotenv()
        super().__init__(
            intents=Intents.ALL,
            token=environ["DEBUG_TOKEN"] if debug else environ["BOT_TOKEN"],
            default_enabled_guilds=(930077129411018793,) if debug else (),
            logs="ERROR",
        )

        self.data = Data()
        self.db = Database()
        self.owner_id = 201674460393242624


class Data:
    def __init__(self) -> None:
        self.lavalink: Lavalink = None
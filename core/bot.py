from hikari import Intents
from lightbulb import BotApp

from os import environ
from core.db import Database
from dotenv import load_dotenv


class Bot(BotApp):
    def __init__(self):
        load_dotenv()

        guilds = (752921557214429316, 634339847108165632, 339045627478540288, 930077129411018793)

        super().__init__(
            intents=Intents.ALL,
            token=environ["BOT_TOKEN"],
            default_enabled_guilds=guilds,
            logs="ERROR",
        )

        self.twitch = {}
        self.db = Database()
from hikari import Intents
from lightbulb import BotApp

from abc import ABC
from os import environ


class ExtendedBot(BotApp, ABC):
    def __init__(self):
        guilds = (752921557214429316, 634339847108165632, 339045627478540288)

        super().__init__(
            intents=Intents.ALL,
            token=environ["BOT_TOKEN"],
            default_enabled_guilds=guilds,
            logs="ERROR",
        )

        self.twitch = {}

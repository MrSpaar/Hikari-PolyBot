from hikari import Intents, Member, GatewayBot
from lightbulb import Bot as BaseBot, Command as BaseCommand, Group as BaseGroup

from os import environ
from typing import Union
from dotenv import load_dotenv
from lavasnek_rs import Lavalink
from datetime import timedelta, datetime
from motor.motor_asyncio import AsyncIOMotorClient
from logging import Logger, LogRecord, setLoggerClass

class Bot(BaseBot):
    def __init__(self, plugins=[], debug=False):
        load_dotenv()
        super().__init__(prefix='-' if debug else '!', insensitive_commands=True, intents=Intents.ALL,
                         token=environ['DEBUG_TOKEN'] if debug else environ['BOT_TOKEN'])

        setLoggerClass(LoggingHandler)
        self.remove_command('help')

        self.debug = debug
        self.data = Data()
        self.db = Database()
        self.cprefix = '-' if debug else '!'
        self.owner_id = 201674460393242624


class LoggingHandler(Logger):
    def handle(self, record: LogRecord):
        if record.levelname in ['CRITICAL', 'INFO', 'ERROR']:
            print(record.getMessage())


class Data:
    def __init__(self) -> None:
        self.lavalink: Lavalink = None

class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)

        self.brief = kwargs.get('brief', '')
        self.usage = kwargs.get('usage', '')
        self.description = kwargs.get('description', '')


class Group(BaseGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)

        self.brief = kwargs.get('brief', '')
        self.usage = kwargs.get('usage', '')
        self.description = kwargs.get('description', '')

    def command(self, **kwargs):
        def decorate(func):
            name = kwargs.get('name', func.__name__)
            self._subcommands[name] = Command(
                func,
                kwargs.get('name', func.__name__),
                kwargs.get('allow_extra_arguments', True),
                kwargs.get('aliases', []),
                kwargs.get('hidden', False),
                parent=self,
                **kwargs
            )

            if self.inherit_checks:
                self._subcommands[name]._checks.extend(self._checks)
            self.subcommands.add(self._subcommands[name])
            for alias in kwargs.get("aliases", []):
                self._subcommands[alias] = self._subcommands[name]
            return self._subcommands[name]

        return decorate

class Cooldown:
    def __init__(self, usages: int, seconds: int):
        self.cooldowns = {}
        self.usages = usages
        self.seconds = seconds

    @property
    def now(self) -> datetime:
        return datetime.utcnow() + timedelta(hours=2)

    def update_cooldown(self, member: Member, guild: GatewayBot):
        if member.id not in self.cooldowns:
            self.cooldowns[member.id] = {
                guild.id: {
                    'usages': 0,
                    'cool': self.now + timedelta(seconds=self.seconds)
                }
            }
            return True

        if guild.id not in self.cooldowns[member.id]:
            self.cooldowns[member.id][guild.id] = {
                'usages': 0,
                'cool': self.now + timedelta(seconds=self.seconds)
            }
            return True

        if self.now > self.cooldowns[member.id][guild.id]['cool']:
            self.cooldowns[member.id][guild.id]['usages'] = 0
            self.cooldowns[member.id][guild.id]['cool'] += timedelta(seconds=self.seconds)
            return True

        self.cooldowns[member.id][guild.id]['usages'] += 1

        if self.cooldowns[member.id][guild.id]['usages'] <= self.usages-1:
            return True

        return False


class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(environ['DATABASE_URL'])

        self.setup = Collection(self.client['data']['setup'])
        self.pending = Collection(self.client['data']['pending'])
        self.members = Collection(self.client['data']['members'])


class Collection:
    def __init__(self, collection):
        self.collection = collection

    async def find(self, query: dict = {}, sub: dict = {}) -> Union[list, dict, None]:
        if sub:
            data = await self.collection.find(query, sub).to_list(length=None)
        else:
            data = await self.collection.find(query).to_list(length=None)

        if len(data) > 1:
            return data
        elif data:
            return data[0]

        return

    async def update(self, query: dict, data: dict, upsert: bool = False) -> None:
        await self.collection.update_one(query, data, upsert)

    async def insert(self, data: dict) -> None:
        await self.collection.insert_one(data)

    async def delete(self, query: dict) -> None:
        await self.collection.delete_one(query)

    async def sort(self, query: dict, sub: dict, field: str, order: int) -> list:
        data = self.collection.find(query, sub).sort(field, order)
        return await data.to_list(length=None)

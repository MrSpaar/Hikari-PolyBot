from hikari import GatewayGuild

from os import environ
from random import randint
from motor.motor_asyncio import AsyncIOMotorClient


class Database:
    def __init__(self) -> None:
        self.client = AsyncIOMotorClient(environ["DATABASE_URL"])
        self.cluster = self.client["data"]

    async def fetch_settings(self, guild_id: int):
        data = await self.cluster["setup"].find({"_id": guild_id}).to_list(length=None)

        return None if not data else data[0]

    async def change_setting(self, guild_id, key: str, value: int) -> None:
        query = {'_id': guild_id}
        update = {"$set": {key: value}}

        await self.cluster["setup"].update_one(query, update)

    async def delete_server(self, guild: GatewayGuild) -> None:
        await self.cluster["setup"].delete_one({'_id': guild.id})

        filt = {"_id": {"$in": [member.id for member in guild.get_members()]}}
        query = {"$pull": {"guilds": {"id": guild.id}}}

        await self.cluster["members"].update_many(filt, query)

    async def add_server(self, guild: GatewayGuild) -> None:
        await self.cluster["setup"].insert_one({
            "_id": guild.id,
            "logs": None,
            "channel": None,
            "new": None,
            "welcome": None,
        })

        members = filter(lambda m: not m.is_bot, guild.get_members())

        for member in members:
            await self.add_member_guild(guild.id, member.id)

    async def add_member_guild(self, guild_id: int, member_id: int) -> None:
        query = {"_id": member_id}
        update = {"$addToSet": {"guilds": {"id": guild_id, "level": 0, "xp": 0}}}

        await self.cluster["members"].update_one(query, update, True)

    async def remove_member_guild(self, guild_id: int, member_id: int) -> None:
        query = {"_id": member_id}
        update = {"$pull": {"guilds": {"id": guild_id}}}

        await self.cluster["members"].update_one(query, update)

    async def fetch_temp_channel(self, guild_id: int, voc_id: int = None, member_id: int = None) -> dict:
        if member_id:
            query = {"guild_id": guild_id, "_id": member_id}
        else:
            query = {"guild_id": guild_id, "voc_id": voc_id}

        data = await self.cluster["pending"].find(query).to_list(length=None)
        return None if not data else data[0]

    async def insert_temp_channel(self, guild_id: int, member_id: int, voc_id: int, txt_id: int) -> None:
        await self.cluster["pending"].insert_one({
            "_id": member_id,
            "guild_id": guild_id,
            "voc_id": voc_id,
            "txt_id": txt_id,
        })

    async def delete_temp_channel(self, entry: dict) -> None:
        await self.cluster["pending"].delete_one(entry)

    async def fetch_leaderboard(self, guild_id: int) -> list:
        data = self.cluster["members"].find({"guilds.id": guild_id}, {"guilds.$": 1})

        return await data.to_list(length=None)

    async def fetch_member(self, guild_id: int, member_id: int) -> list:
        data = await self.cluster["members"].find(
            {"_id": member_id, "guilds.id": guild_id}, {"guilds.$": 1}
        ).to_list(length=None)

        return None if not data else data[0]

    async def update_member_xp(self, guild_id: int, member_id: int, xp: int, next_lvl: int) -> None:
        query = {"_id": member_id, "guilds.id": guild_id}
        update = {
            "$inc": {
                "guilds.$.xp": randint(15, 25),
                "guilds.$.level": 1 if xp >= next_lvl else 0}
        }

        await self.cluster["members"].update_one(query, update)

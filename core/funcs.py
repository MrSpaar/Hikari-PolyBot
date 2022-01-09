from hikari import Permissions
from lightbulb import Context, Check, errors

from datetime import datetime, timedelta
from unicodedata import normalize
from aiohttp import ClientSession
from typing import Union


async def api_call(link: str, headers: dict = None, json: bool = True) -> Union[dict, str]:
    async with ClientSession() as s:
        async with s.get(link, headers=headers) as resp:
            return await resp.json() if json else await resp.text()


def normalize_string(s: str) -> str:
    return normalize(u"NFKD", s).encode("ascii", "ignore").decode("utf8")


def now(utc: bool = False) -> datetime:
    if utc:
        return datetime.utcnow()
    return datetime.utcnow() + timedelta(hours=2)


def _is_higher(ctx: Context):
    args = ctx.message.content.split()
    guild = ctx.get_guild()
    member = guild.get_member(int(args[1].strip("<@!>")))

    if not member:
        raise errors.ConverterFailure("member")

    author_top = ctx.member.get_top_role()
    member_top = member.get_top_role()

    if author_top.position > member_top.position:
        return True
    raise errors.MissingRequiredPermission(Permissions.ADMINISTRATOR)


async def _vc_check(ctx: Context):
    guild = ctx.get_guild()
    voice = guild.get_voice_state(ctx.author)

    if not voice:
        raise errors.CommandInvocationError("channel")

    entry = await ctx.bot.db.pending.find(
        {"guild_id": guild.id, "voc_id": guild.get_channel(voice.channel_id).id}
    )
    if not entry:
        raise errors.CommandInvocationError("Not Temp")

    owner = guild.get_member(entry["owner"])
    if ctx.author != owner:
        raise errors.CommandInvocationError("Not owner")

    return True


vc_check = Check(_vc_check)
is_higher = Check(_is_higher)

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


def _is_higher(ctx: Context) -> Union[bool, Exception]:
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


is_higher = Check(_is_higher)

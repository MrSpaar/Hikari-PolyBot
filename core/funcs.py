from hikari import Permissions
from lightbulb import Context, Check, errors

from core.cls import Command, Group
from datetime import datetime, timedelta
from unicodedata import normalize
from aiohttp import ClientSession
from typing import Union

def command(**kwargs):
    def decorate(func):
        return Command(
            func,
            kwargs.get('name', func.__name__),
            kwargs.get('allow_extra_arguments', True),
            kwargs.get('aliases', []),
            kwargs.get('hidden', False),
            **kwargs
        )
    return decorate

def group(**kwargs):
    def decorate(func):
        return Group(
            func,
            kwargs.get('name', func.__name__),
            kwargs.get('allow_extra_arguments', True),
            kwargs.get('aliases', []),
            kwargs.get('hidden', False),
            insensitive_commands=kwargs.get('insensitive_commands', False),
            inherit_checks=kwargs.get('inherit_checks', True),
            **kwargs
        )

    return decorate

async def get_json(link: str, headers: dict = None, json: bool = True) -> Union[dict, str]:
    async with ClientSession() as s:
        async with s.get(link, headers=headers) as resp:
            return await resp.json() if json else await resp.text()

def normalize_string(s: str) -> str:
    return normalize(u'NFKD', s).encode('ascii', 'ignore').decode('utf8')

def now(utc: bool = False) -> datetime:
    if utc:
        return datetime.utcnow()
    return datetime.utcnow() + timedelta(hours=2)

def is_higher(ctx: Context) -> Check:
    async def extended_check() -> bool:
        args = ctx.message.content.split()
        guild = ctx.get_guild()
        member = guild.get_member(int(args[1].strip('<@!>')))

        if not member:
            raise errors.ConverterFailure('member')

        author_top = ctx.member.get_top_role()
        member_top = member.get_top_role()

        if author_top.position > member_top.position:
            return True
        raise errors.MissingRequiredPermission(Permissions.ADMINISTRATOR)
    return Check(extended_check)

def vc_check(ctx: Context) -> Check:
    async def extended_check() -> bool:
        guild = ctx.get_guild()
        voice = guild.get_voice_state(ctx.author)

        if not voice:
            raise errors.CommandInvocationError('channel')

        entry = await ctx.bot.db.pending.find({'guild_id': guild.id, 'voc_id': guild.get_channel(voice.channel_id).id})
        if not entry:
            raise errors.CommandInvocationError('Not Temp')

        owner = guild.get_member(entry['owner'])
        if ctx.author != owner:
            raise errors.CommandInvocationError('Not owner')

        return True
    return Check(extended_check)

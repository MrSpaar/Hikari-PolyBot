from hikari import Role, TextableChannel, Embed, Permissions
from hikari.events import GuildJoinEvent, GuildLeaveEvent, MemberCreateEvent, MemberDeleteEvent
from lightbulb import Plugin, Context, listener, check, guild_only, has_guild_permissions

from typing import Union
from core.cls import Bot
from core.funcs import command


class Configuration(Plugin):
    def __init__(self, bot, name=None):
        super().__init__(name=name)
        self.bot: Bot = bot

    @check(guild_only)
    @check(has_guild_permissions(Permissions.ADMINISTRATOR))
    @command(name='set', brief='channel #🧙-polybot',
             usage='<mute, logs ou channel> <@role ou #channel>',
             description='Modifier les paramètres du bot')
    async def _set(self, ctx: Context, key: str, value: Union[Role, TextableChannel]):
        settings = {
            'mute': 'Rôle des muets',
            'logs': 'Channel de logs',
            'channel': 'Channel du bot'
        }

        if key not in settings:
            embed = Embed(color=0xe74c3c, description=f"❌ Clé invalide : {', '.join(settings.keys())}")
            return await ctx.respond(embed=embed)

        await ctx.bot.db.setup.update({'_id': ctx.guild_id}, {'$set': {key: value.id}})

        embed = Embed(color=0x2ecc71, description=f"{settings[key]} modifié ({value.mention})")
        await ctx.respond(embed=embed)

    @check(guild_only)
    @check(has_guild_permissions(Permissions.ADMINISTRATOR))
    @command(description='Afficher les paramètres du bot')
    async def settings(self, ctx: Context):
        guild = ctx.get_guild()
        settings = await ctx.bot.db.setup.find({'_id': guild.id})

        
        channel = getattr(guild.get_channel(settings['channel']), 'mention', 'pas défini')
        logs = getattr(guild.get_channel(settings['logs']), 'mention', 'pas défini')
        mute = getattr(guild.get_role(settings['mute']), 'mention', 'pas défini')

        embed = Embed(color=0x3498db, description=f"💬 Bot : {channel}\n📟 Logs : {logs}\n🔇 Mute : {mute}")
        await ctx.respond(embed=embed)

    @listener(GuildJoinEvent)
    async def on_guild_join(self, event):
        guild = event.get_guild()

        await self.bot.db.setup.insert({'_id': guild.id, 'mute': None, 'logs': None, 'channel': None, 'new': None, 'welcome': None})
        for member in filter(lambda m: not m.bot, guild.members):
            await self.bot.db.members.update({'_id': member.id}, {'$addToSet': {'guilds': {'id': guild.id, 'level': 0, 'xp':0}}}, True)

    @listener(GuildLeaveEvent)
    async def on_guild_remove(self, event):
        try:
            guild = event.get_guild()
            await self.bot.db.setup.delete({'_id': guild.id})
            await self.bot.db.members.collection.update_many({'_id': {'$in': [member.id for member in guild.members]}}, {'$pull': {'guilds': {'id': guild.id}}})
        except:
            return

    @listener(MemberCreateEvent)
    async def on_member_join(self, event):
        user, guild = event.user, event.get_guild()
        await self.bot.db.members.update({'_id': user.id}, {'$addToSet': {'guilds': {'id': guild.id, 'level': 0, 'xp': 0}}}, True)

    @listener(MemberDeleteEvent)
    async def on_member_remove(self, event):
        user, guild = event.user, event.get_guild()
        await self.bot.db.members.update({'_id': user.id}, {'$pull': {'guilds': {'id': guild.id}}})


def load(bot):
    bot.add_plugin(Configuration(bot))

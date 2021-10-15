from hikari import Member, Embed, Permissions, GatewayGuild, StartedEvent
from lightbulb import Plugin, Context, check, guild_only, has_guild_permissions, listener

from core.funcs import is_higher, now
from datetime import timedelta
from core.funcs import command
from core.cls import Bot
from asyncio import sleep


class Moderation(Plugin):
    def __init__(self, bot, name=None):
        super().__init__(name=name)
        self.bot: Bot = bot

    async def fetch_settings(self, guild: GatewayGuild):
        settings = await self.bot.db.setup.find({'_id': guild.id})
        role = guild.get_role(settings['mute'])
        logs = guild.get_channel(settings['logs'])

        return role, logs

    @listener(StartedEvent)
    async def unmute_loop(self, event):
        if self.bot.debug:
            return

        while True:
            await sleep(60)

            entries = await self.bot.db.pending.find({'end': {'$lt': now()}})
            if not entries:
                continue

            entries = entries if isinstance(entries, list) else [entries]
            for entry in entries:
                guild = self.bot.cache.get_guild(entry['guild_id'])
                settings = await self.bot.db.setup.find({'_id': entry['guild_id']})

                member = guild.get_member(entry['id'])
                role = guild.get_role(settings['mute'])

                await member.remove_role(role)
                await self.bot.db.pending.delete(entry)

    @check(guild_only)
    @check(is_higher)
    @check(has_guild_permissions(Permissions.MANAGE_MESSAGES))
    @command(brief='@Antoine Grégoire 10m mdrr', usage='<membre> <durée> <raison (optionnel)>',
             description='Rendre un membre muet')
    async def mute(self, ctx: Context, member: Member, time: str = None):
        guild = ctx.get_guild()
        role, _ = await self.fetch_settings(guild)

        if not role:
            embed = Embed(color=0xe74c3c, description=f'❌ Aucun rôle mute spécifié (`!set mute @role`)')
            return await ctx.respond(embed=embed)

        if role in member.get_roles():
            embed = Embed(color=0xe74c3c, description=f'❌ {member.mention} est déjà mute')
            return await ctx.send(embed=embed)

        try:
            units = {"s": [1, 'secondes'], "m": [60, 'minutes'], "h": [3600, 'heures']}
            date = now() + timedelta(seconds=(int(time[:-1])*units[time[-1]][0]))
            time = f"{time[:-1]} {units[time[-1]][1]}"
        except:
            date = now() + timedelta(days=1000)
            time = 'indéfiniment'

        try:
            embed = Embed(color=0x2ecc71, description=f'✅ {member.mention} a été mute {time}')

            await member.add_role(role)
            await self.bot.db.pending.insert({'guild_id': guild.id, 'id': member.id, 'end': date})
        except:
            embed = Embed(color=0xe74c3c, description='❌ La cible a plus de permissions que moi')

        await ctx.respond(embed=embed)

    @check(guild_only)
    @check(is_higher)
    @check(has_guild_permissions(Permissions.MANAGE_MESSAGES))
    @command(brief='@Antoine Grégoire', usage='<membre>',
             description='Redonner la parole à un membre')
    async def unmute(self, ctx: Context, member: Member):
        guild = ctx.get_guild()
        role, _ = await self.fetch_settings(guild)

        if role not in member.get_roles():
            return await ctx.send(f"❌ {member.mention} n'est pas mute")

        await member.remove_role(role)
        await self.bot.db.pending.delete({'guild_id': guild.id, 'id': member.id})

        embed = Embed(color=0x2ecc71, description=f'✅ {member.mention} a été unmute')
        await ctx.respond(embed=embed)

    @check(guild_only)
    @check(has_guild_permissions(Permissions.MANAGE_MESSAGES))
    @command(aliases=['prout'], brief='20', usage='<nombre de messages>',
             description='Supprimer plusieurs messages en même temps')
    async def clear(self, ctx: Context, x: int):
        channel, messages = ctx.get_channel(), []
        async for message in channel.fetch_history():
            if len(messages) > x:
                break

            messages += [message]

        await channel.delete_messages(messages)

    @check(guild_only)
    @check(is_higher)
    @check(has_guild_permissions(Permissions.KICK_MEMBERS))
    @command(brief='@Mee6 Obselète', usage='<membre> <raison (optionnel)>',
             description='Exclure un membre du serveur')
    async def kick(self, ctx: Context, member: Member, *, reason: str = 'Pas de raison'):
        embed = Embed(color=0x2ecc71, description=f'✅ {member.mention} a été kick')

        await member.kick(reason=reason)
        await ctx.respond(embed=embed)

    @check(guild_only)
    @check(is_higher)
    @check(has_guild_permissions(Permissions.BAN_MEMBERS))
    @command(brief='@Mee6 Obselète', usage='<membre> <raison (optionnel)>',
             description='Bannir un membre du serveur')
    async def ban(self, ctx: Context, member: Member, *, reason='Pas de raison'):
        embed = Embed(color=0x2ecc71, description=f'✅ {member.mention} a été ban')

        await member.ban(reason=reason)
        await ctx.respond(embed=embed)

    @check(guild_only)
    @check(has_guild_permissions(Permissions.BAN_MEMBERS))
    @command(brief='@Pierre Karr', usage='<membre> <raison (optionnel)>',
             description='Révoquer un bannissement')
    async def unban(self, ctx: Context, user_id: int, *, reason='Pas de raison'):
        try:
            guild = ctx.get_guild()
            user = self.bot.rest.fetch_user(user_id)

            await guild.unban(user, reason=reason)

            embed = Embed(color=0x2ecc71, description=f'✅ `{user.mention}` a été unban')
            await ctx.respond(embed=embed)
        except:
            embed = Embed(color=0xe74c3c, description="❌ L'utilisateur n'est pas banni de ce serveur")
            await ctx.send(embed=embed)


def load(bot):
    bot.add_plugin(Moderation(bot))

def unload(bot):
    bot.remove_plugin('Moderation')

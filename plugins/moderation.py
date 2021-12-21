from hikari import Member, Embed, Permissions, GatewayGuild
from lightbulb import Plugin, Context, check, guild_only, has_guild_permissions

from core.funcs import is_higher
from core.funcs import command
from core.cls import Bot


class Moderation(Plugin):
    def __init__(self, bot, name=None):
        super().__init__(name=name)
        self.bot: Bot = bot

    async def fetch_settings(self, guild: GatewayGuild):
        settings = await self.bot.db.setup.find({'_id': guild.id})
        role = guild.get_role(settings['mute'])
        logs = guild.get_channel(settings['logs'])

        return role, logs

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

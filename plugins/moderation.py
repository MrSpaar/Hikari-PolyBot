from hikari import Member, Embed, Permissions, GatewayGuild, MessageFlag
from lightbulb import (
    Plugin,
    Context,
    SlashCommand,
    OptionModifier,
    command,
    option,
    implements,
    add_checks,
    guild_only,
    has_guild_permissions,
)

from core.funcs import is_higher

plugin = Plugin("Moderation")
plugin.add_checks(guild_only)


async def fetch_settings(guild: GatewayGuild):
    settings = await plugin.bot.db.setup.find({"_id": guild.id})
    role = guild.get_role(settings["mute"])
    logs = guild.get_channel(settings["logs"])

    return role, logs


@plugin.command()
@add_checks(has_guild_permissions(Permissions.MANAGE_MESSAGES))
@option("x", "Le nombre de messages à supprimer", int)
@command("clear", "Supprimer plusieurs messages en même temps")
@implements(SlashCommand)
async def clear(ctx: Context):
    channel, messages = ctx.get_channel(), []
    async for message in channel.fetch_history():
        if len(messages) >= ctx.options.x:
            break

        messages += [message]

    await channel.delete_messages(messages)
    await ctx.respond(f'{ctx.options.x} message supprimés', flags=MessageFlag.EPHEMERAL)


@plugin.command()
@add_checks(is_higher | has_guild_permissions(Permissions.KICK_MEMBERS))
@option("membre", "Le membre à exclure du serveur", Member)
@option("raison", "La raison de l'exclusion", modifier=OptionModifier.CONSUME_REST, default="Pas de raison")
@command("kick", "Exclure un membre du serveur")
@implements(SlashCommand)
async def kick(ctx: Context):
    embed = Embed(color=0x2ECC71, description=f"✅ {ctx.options.membre.mention} a été kick")

    await ctx.options.membre.kick(reason=ctx.options.raison)
    await ctx.respond(embed=embed)


@plugin.command()
@add_checks(is_higher | has_guild_permissions(Permissions.BAN_MEMBERS))
@option("membre", "Le membre à bannir", Member)
@option("raison", "La raison du bannissement", modifier=OptionModifier.CONSUME_REST, default="Pas de raison")
@command("ban", "Bannir un membre du serveur")
@implements(SlashCommand)
async def ban(ctx: Context):
    embed = Embed(color=0x2ECC71, description=f"✅ {ctx.options.membre.mention} a été ban")

    await ctx.options.membre.ban(reason=ctx.options.raison)
    await ctx.respond(embed=embed)


@plugin.command()
@add_checks(has_guild_permissions(Permissions.BAN_MEMBERS))
@option("id", "L'ID du membre à débannir", int)
@option("raison", "La raison du débannissement", modifier=OptionModifier.CONSUME_REST, default="Pas de raison")
@command("unban", "Débannir un membre du serveur")
@command("unban", "Révoquer un bannissement")
@implements(SlashCommand)
async def unban(ctx: Context):
    try:
        guild = ctx.get_guild()
        user = plugin.bot.rest.fetch_user(ctx.options.id)

        await guild.unban(user, reason=ctx.options.raison)

        embed = Embed(color=0x2ECC71, description=f"✅ `{user.mention}` a été unban")
        await ctx.respond(embed=embed)
    except:
        embed = Embed(color=0xE74C3C, description="❌ L'utilisateur n'est pas banni de ce serveur")
        await ctx.send(embed=embed)


def load(bot):
    bot.add_plugin(plugin)

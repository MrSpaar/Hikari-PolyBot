from hikari import Member, Embed, Permissions, MessageFlag
from lightbulb import (
    Plugin,
    Context,
    SlashCommandGroup,
    SlashSubCommand,
    OptionModifier,
    command,
    option,
    implements,
    add_checks,
    guild_only,
    has_guild_permissions,
)

from src.funcs import is_higher

plugin = Plugin("Moderation")
plugin.add_checks(guild_only)


@plugin.command()
@command("mod", "Groupe de commandes en rapport avec la modération")
@implements(SlashCommandGroup)
async def mod(ctx: Context):
    pass


@mod.child
@add_checks(has_guild_permissions(Permissions.MANAGE_MESSAGES))
@option("x", "Le nombre de messages à supprimer", int)
@command("clear", "Supprimer plusieurs messages en même temps")
@implements(SlashSubCommand)
async def clear(ctx: Context):
    channel, messages = ctx.get_channel(), []
    async for message in channel.fetch_history():
        if len(messages) >= ctx.options.x:
            break

        messages.append(message)

    await channel.delete_messages(messages)
    await ctx.respond(f'{ctx.options.x} message supprimés', flags=MessageFlag.EPHEMERAL)


@mod.child
@add_checks(is_higher | has_guild_permissions(Permissions.KICK_MEMBERS))
@option("membre", "Le membre à exclure du serveur", Member)
@option("raison", "La raison de l'exclusion", modifier=OptionModifier.CONSUME_REST, default="Pas de raison")
@command("kick", "Exclure un membre du serveur")
@implements(SlashSubCommand)
async def kick(ctx: Context):
    embed = Embed(color=0x2ECC71, description=f"✅ {ctx.options.membre.mention} a été kick")

    await ctx.options.membre.kick(reason=ctx.options.raison)
    await ctx.respond(embed=embed)


@mod.child
@add_checks(is_higher | has_guild_permissions(Permissions.BAN_MEMBERS))
@option("membre", "Le membre à bannir", Member)
@option("raison", "La raison du bannissement", modifier=OptionModifier.CONSUME_REST, default="Pas de raison")
@command("ban", "Bannir un membre du serveur")
@implements(SlashSubCommand)
async def ban(ctx: Context):
    embed = Embed(color=0x2ECC71, description=f"✅ {ctx.options.membre.mention} a été ban")

    await ctx.options.membre.ban(reason=ctx.options.raison)
    await ctx.respond(embed=embed)


@mod.child
@add_checks(has_guild_permissions(Permissions.BAN_MEMBERS))
@option("id", "L'ID du membre à débannir", int)
@option("raison", "La raison du débannissement", modifier=OptionModifier.CONSUME_REST, default="Pas de raison")
@command("unban", "Débannir un membre du serveur")
@command("unban", "Révoquer un bannissement")
@implements(SlashSubCommand)
async def unban(ctx: Context):
    try:
        guild = ctx.get_guild()
        user = plugin.bot.rest.fetch_user(ctx.options.id)

        await guild.unban(user, reason=ctx.options.raison)

        embed = Embed(color=0x2ECC71, description=f"✅ `{user.mention}` a été unban")
        await ctx.respond(embed=embed)
    except Exception:
        embed = Embed(color=0xE74C3C, description="❌ L'utilisateur n'est pas banni de ce serveur")
        await ctx.send(embed=embed)


def load(bot):
    bot.add_plugin(plugin)

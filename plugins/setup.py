from hikari import (
    Snowflake,
    Embed,
    Permissions,
    GuildJoinEvent,
    GuildLeaveEvent,
    MemberCreateEvent,
    MemberDeleteEvent,
)
from lightbulb import (
    Plugin,
    Context,
    SlashCommand,
    command,
    option,
    implements,
    guild_only,
    has_guild_permissions,
)

plugin = Plugin("Configuration")
plugin.add_checks(guild_only, has_guild_permissions(Permissions.ADMINISTRATOR))


@plugin.command()
@option("valeur", "La nouvelle valeur du paramètre (role ou channel)", Snowflake)
@option("reglage", "Le paramètre à modifier (logs, channel, new)", choices=['new', 'logs', 'channel'])
@command("set", "Modifier les paramètres du bot")
@implements(SlashCommand)
async def _set(ctx: Context):
    settings = {
        "new": "Rôle des muets",
        "logs": "Channel de logs",
        "channel": "Channel du bot",
    }

    await ctx.bot.db.change_setting(ctx.guild_id, ctx.options.reglage, ctx.options.valeur.id)

    embed = Embed(color=0x2ECC71, description=f"{settings[ctx.options.reglage]} modifié ({ctx.options.valeur.mention})")
    await ctx.respond(embed=embed)


@plugin.command()
@command("settings", "Afficher les paramètres du bot")
@implements(SlashCommand)
async def settings(ctx: Context):
    guild = ctx.get_guild()
    settings = await ctx.bot.db.fetch_settings(guild.id)

    channel = getattr(guild.get_channel(settings["channel"]), "mention", "pas défini")
    logs = getattr(guild.get_channel(settings["logs"]), "mention", "pas défini")
    new = getattr(guild.get_role(settings["new"]), "mention", "pas défini")

    embed = Embed(color=0x3498DB, description=f"💬 Bot : {channel}\n📟 Logs : {logs}\n🙍 Rôle des nouveaux : {new}",)
    await ctx.respond(embed=embed)


@plugin.listener(GuildJoinEvent)
async def guild_join(event):
    await plugin.bot.db.add_server(event.get_guild())


@plugin.listener(GuildLeaveEvent)
async def guild_leave(event):
    await plugin.bot.db.delete_server(event.get_guild())


@plugin.listener(MemberCreateEvent)
async def member_join(event):
    await plugin.bot.db.add_member_guild(event.guild_id, event.user.id)


@plugin.listener(MemberDeleteEvent)
async def member_leave(event):
    await plugin.bot.db.remove_member_guild(event.guild_id, event.user.id)


def load(bot):
    bot.add_plugin(plugin)

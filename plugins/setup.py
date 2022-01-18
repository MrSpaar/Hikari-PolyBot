from hikari import (
    Role,
    Embed,
    TextableGuildChannel,
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
    SlashCommandGroup,
    SlashSubCommand,
    command,
    option,
    implements,
    guild_only,
    has_guild_permissions,
)

plugin = Plugin("Configuration")
plugin.add_checks(guild_only, has_guild_permissions(Permissions.ADMINISTRATOR))


def get_snowflake(guild, value, cls=TextableGuildChannel):
    if value is None:
        return "`Non défini`"

    if cls == TextableGuildChannel:
        channel = guild.get_channel(value)
        return channel.mention if channel else "`Non défini`"

    role = guild.get_role(value)
    return role.mention if role else "`Non défini`"


@plugin.command()
@command("set", "Modifier les paramètres du bot")
@implements(SlashCommandGroup)
async def set_cmd(ctx: Context):
    pass


@set_cmd.child
@option("role", "Le rôle qu'auront les nouveaux membres", Role)
@command("new", "Modifier le role des nouveaux")
@implements(SlashSubCommand)
async def new(ctx: Context):
    await ctx.bot.db.change_setting(ctx.guild_id, "new", ctx.options.role.id)

    embed = Embed(color=0x2ECC71, description=f"Rôle des nouveaux modifié (<@&{ctx.options.role.id}>)")
    await ctx.respond(embed=embed)


@set_cmd.child
@option("channel", "Le salon où seront envoyés les logs", TextableGuildChannel)
@command("logs", "Modifier le channel des logs")
@implements(SlashSubCommand)
async def logs(ctx: Context):
    await ctx.bot.db.change_setting(ctx.guild_id, "logs", ctx.options.channel.id)

    embed = Embed(color=0x2ECC71, description=f"Channel des logs modifié (<#{ctx.options.channel.id}>)")
    await ctx.respond(embed=embed)


@set_cmd.child
@option("channel", "Le salon où seront envoyés les annonces de level up", TextableGuildChannel)
@command("niveaux", "Modifier le channel des annonces de level up")
@implements(SlashSubCommand)
async def logs(ctx: Context):
    await ctx.bot.db.change_setting(ctx.guild_id, "channel", ctx.options.channel.id)

    embed = Embed(color=0x2ECC71, description=f"Channel des annonces de level up modifié (<#{ctx.options.channel.id}>)")
    await ctx.respond(embed=embed)


@plugin.command()
@command("settings", "Afficher les paramètres du bot")
@implements(SlashCommand)
async def settings(ctx: Context):
    guild = ctx.get_guild()
    settings = await ctx.bot.db.fetch_settings(guild.id)

    channel = get_snowflake(guild, settings["channel"])
    logs = get_snowflake(guild, settings["logs"])
    new = get_snowflake(guild, settings["new"], Role)

    embed = Embed(color=0x3498DB, description=f"💬 Bot : {channel}\n📟 Logs : {logs}\n🙍 Rôle des nouveaux : {new}")
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

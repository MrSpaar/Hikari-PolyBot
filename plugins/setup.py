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

    await ctx.bot.db.setup.update({"_id": ctx.guild_id}, {"$set": {ctx.options.reglage: ctx.options.valeur.id}})

    embed = Embed(color=0x2ECC71, description=f"{settings[ctx.options.reglage]} modifié ({ctx.options.valeur.mention})")
    await ctx.respond(embed=embed)


@plugin.command()
@command("settings", "Afficher les paramètres du bot")
@implements(SlashCommand)
async def settings(ctx: Context):
    guild = ctx.get_guild()
    settings = await ctx.bot.db.setup.find({"_id": guild.id})

    channel = getattr(guild.get_channel(settings["channel"]), "mention", "pas défini")
    logs = getattr(guild.get_channel(settings["logs"]), "mention", "pas défini")
    new = getattr(guild.get_role(settings["new"]), "mention", "pas défini")

    embed = Embed(color=0x3498DB, description=f"💬 Bot : {channel}\n📟 Logs : {logs}\n🙍 Rôle des nouveaux : {new}",)
    await ctx.respond(embed=embed)


@plugin.listener(GuildJoinEvent)
async def on_guild_join(event):
    guild = event.get_guild()

    await plugin.bot.db.setup.insert(
        {
            "_id": guild.id,
            "logs": None,
            "channel": None,
            "new": None,
            "welcome": None,
        }
    )

    for member in filter(lambda m: not m.bot, guild.get_members()):
        await plugin.bot.db.members.update(
            {"_id": member.id},
            {"$addToSet": {"guilds": {"id": guild.id, "level": 0, "xp": 0}}},
            True,
        )


@plugin.listener(GuildLeaveEvent)
async def on_guild_remove(event):
    try:
        guild = event.get_guild()
        await plugin.bot.db.setup.delete({"_id": guild.id})
        await plugin.bot.db.members.collection.update_many(
            {"_id": {"$in": [member.id for member in guild.get_members()]}},
            {"$pull": {"guilds": {"id": guild.id}}},
        )
    except:
        return


@plugin.listener(MemberCreateEvent)
async def on_member_join(event):
    user, guild = event.user, event.get_guild()
    await plugin.bot.db.members.update(
        {"_id": user.id},
        {"$addToSet": {"guilds": {"id": guild.id, "level": 0, "xp": 0}}},
        True,
    )


@plugin.listener(MemberDeleteEvent)
async def on_member_remove(event):
    user, guild = event.user, event.get_guild()
    await plugin.bot.db.members.update(
        {"_id": user.id}, {"$pull": {"guilds": {"id": guild.id}}}
    )


def load(bot):
    bot.add_plugin(plugin)

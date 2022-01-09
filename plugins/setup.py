from hikari import (
    Role,
    TextableChannel,
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

from typing import Union

plugin = Plugin("Configuration")
plugin.add_checks(guild_only | has_guild_permissions(Permissions.ADMINISTRATOR))


@plugin.command()
@option("option", "Le paramètre à modifier (logs, channel, new)")
@option("valeur", "La nouvelle valeur du paramètre (role ou channel)", Union[Role, TextableChannel],)
@command("set", "Modifier les paramètres du bot")
@implements(SlashCommand)
async def _set(ctx: Context, key: str, value):
    settings = {
        "mute": "Rôle des muets",
        "logs": "Channel de logs",
        "channel": "Channel du bot",
    }

    if key not in settings:
        embed = Embed(color=0xE74C3C, description=f"❌ Clé invalide : {', '.join(settings.keys())}")
        return await ctx.respond(embed=embed)

    await ctx.bot.db.setup.update({"_id": ctx.guild_id}, {"$set": {key: value.id}})

    embed = Embed(color=0x2ECC71, description=f"{settings[key]} modifié ({value.mention})")
    await ctx.respond(embed=embed)


@plugin.command()
@command("settings", "Afficher les paramètres du bot")
@implements(SlashCommand)
async def settings(ctx: Context):
    guild = ctx.get_guild()
    settings = await ctx.bot.db.setup.find({"_id": guild.id})

    channel = getattr(guild.get_channel(settings["channel"]), "mention", "pas défini")
    logs = getattr(guild.get_channel(settings["logs"]), "mention", "pas défini")
    mute = getattr(guild.get_role(settings["mute"]), "mention", "pas défini")

    embed = Embed(color=0x3498DB, description=f"💬 Bot : {channel}\n📟 Logs : {logs}\n🔇 Mute : {mute}",)
    await ctx.respond(embed=embed)


@plugin.listener(GuildJoinEvent)
async def on_guild_join(event):
    guild = event.get_guild()

    await plugin.bot.db.setup.insert(
        {
            "_id": guild.id,
            "mute": None,
            "logs": None,
            "channel": None,
            "new": None,
            "welcome": None,
        }
    )

    for member in filter(lambda m: not m.bot, guild.members):
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
            {"_id": {"$in": [member.id for member in guild.members]}},
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

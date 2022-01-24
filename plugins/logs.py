from hikari import Embed, GatewayGuild, AuditLogEventType, Attachment, events
from lightbulb import Plugin

from src.funcs import now
from time import mktime

plugin = Plugin("Logs")


async def get_audit_log(guild, event):
    entries = await plugin.bot.rest.fetch_audit_log(guild, event_type=event)
    log_id = list(entries[0].entries.keys())[0]
    return entries[0].entries[log_id]


async def send_log(guild: GatewayGuild, embeds: list[Embed], attachments: list[Attachment] = []) -> dict:
    settings = await plugin.bot.db.fetch_settings(guild.id)
    channel = guild.get_channel(settings["logs"])

    if channel:
        await channel.send(embeds=embeds, attachments=attachments)

    return settings


@plugin.listener(events.MemberCreateEvent)
async def on_member_join(event):
    guild, member = plugin.bot.cache.get_guild(event.guild_id), event.member

    embed = Embed(color=0x2ECC71, description=f":inbox_tray: {member.mention} a rejoint le serveur !")
    settings = await send_log(guild, [embed])

    if settings["welcome"]:
        channel = guild.get_channel(settings["welcome"]["id"])
        message = settings["welcome"]["txt"].replace("<mention>", member.mention)

        await channel.send(message)

    if settings["new"]:
        role = guild.get_role(settings["new"])
        await member.add_role(role)


@plugin.listener(events.MemberDeleteEvent)
async def on_member_remove(event):
    if not event.old_member:
        return

    guild, member = plugin.bot.cache.get_guild(event.guild_id), event.old_member
    name = f"{member.display_name} ({member})" if member.display_name else str(member)

    embed = Embed(color=0xE74C3C, description=f":outbox_tray: {name} a quitté le serveur")
    await send_log(guild, [embed])


@plugin.listener(events.BanCreateEvent)
async def on_member_ban(event):
    guild, target = plugin.bot.cache.get_guild(event.guild_id), event.user

    try:
        entry = await get_audit_log(guild, AuditLogEventType.MEMBER_BAN_ADD)
    except:
        return

    reason, user = entry.reason, guild.get_member(entry.user_id)

    embed = Embed(color=0xE74C3C, description=f"👨‍⚖️ {user.mention} a ban {target.mention}\n❔ Raison : {reason or 'Pas de raison'}",)
    await send_log(guild, [embed])


@plugin.listener(events.BanDeleteEvent)
async def on_member_unban(event):
    guild, target = plugin.bot.cache.get_guild(event.guild_id), event.user

    try:
        entry = await get_audit_log(guild, AuditLogEventType.MEMBER_BAN_REMOVE)
    except:
        return

    reason, user = entry.reason, guild.get_member(entry.user_id)

    embed = Embed(color=0xC27C0E, description=f"👨‍⚖️ {user.mention} a unban {target.mention}\n❔ Raison : {reason or 'Pas de raison'}",)
    await send_log(guild, [embed])


@plugin.listener(events.MemberUpdateEvent)
async def on_member_update(event):
    guild = plugin.bot.cache.get_guild(event.guild_id)
    before, after = event.old_member, event.member

    if not before or not after or before.username != after.username:
        return

    embed = Embed(color=0x3498DB)

    if before.display_name != after.display_name:
        try:
            entry = await get_audit_log(guild, AuditLogEventType.MEMBER_UPDATE)
        except:
            return

        member = guild.get_member(entry.user_id)

        if after == member:
            embed.description = f"📝 {member.mention} a changé son surnom (`{before.display_name}` → `{after.display_name}`)"
        else:
            embed.description = f"📝 {member.mention} a changé de surnom de {before.mention} (`{before.display_name}` → `{after.display_name}`)"
    elif (broles := before.get_roles()) != (aroles := after.get_roles()):
        try:
            entry = await get_audit_log(guild, AuditLogEventType.MEMBER_ROLE_UPDATE)
        except:
            return

        member = guild.get_member(entry.user_id)
        role, = set(broles).symmetric_difference(set(aroles))

        if after == member:
            embed.description = f"📝 {member.mention} s'est {'ajouté' if role in aroles else 'retiré'} {role.mention}"
        else:
            embed.description = f"📝 {member.mention} à {'ajouté' if role in aroles else 'retiré'} {role.mention} à {before.mention}"
    else:
        return

    await send_log(guild, [embed])


@plugin.listener(events.GuildMessageDeleteEvent)
async def on_message_delete(event):
    if not event.old_message:
        return

    guild = event.get_guild()
    if not guild:
        return

    channel = event.get_channel()
    message = event.old_message

    if (
        message.author.is_bot
        or "test" in channel.name
        or (message.content and len(message.content) == 1)
    ):
        return

    date = message.timestamp.replace(tzinfo=None)
    mentions = tuple(message.mentions.users.keys()) + message.mentions.role_ids

    attachments = {"images": [], "other": []}
    for attachment in message.attachments:
        (attachments["other"], attachments["images"])[
            attachment.media_type.split("/")[0] == "image"
        ].append(attachment)

    if (now(utc=True) - date).total_seconds() <= 20 and mentions and message.content:
        emoji, color = "<:ping:768097026402942976>", 0xE74C3C
    elif message.content and not message.attachments:
        emoji, color = "🗑️", 0x979C9F
    else:
        emoji, color = "🗑️", 0xF1C40F

    embeds = [Embed(color=color,description=f"{emoji} Message de {message.author.mention} supprimé dans {channel.mention}",)]

    if message.content:
        embeds[0].description += f"\n\n> {message.content}"

    if attachments["images"]:
        embeds[0].set_image(attachments["images"][0])
        embeds += [
            (Embed(color=0xF1C40F).set_image(image))
            for image in attachments["images"][1:]
        ]

    await send_log(guild, embeds, attachments["other"])


@plugin.listener(events.InviteCreateEvent)
async def on_invite_create(event):
    invite, guild = event.invite, plugin.bot.cache.get_guild(event.guild_id)

    if not invite.inviter:
        return

    url = f"https://discord.gg/{invite.code}"
    uses = f"{invite.max_uses} fois" if invite.max_uses else "à l'infini"
    expire = (
        f"<t:{int(mktime((now() + invite.max_age).timetuple()))}:R>"
        if invite.max_age
        else "jamais"
    )

    embed = Embed(color=0x3498DB, description=f"✉️ {invite.inviter.mention} a créé une [invitation]({url}) qui expire {expire}, utilisable {uses}",)
    await send_log(guild, [embed])


def load(bot):
    bot.add_plugin(plugin)

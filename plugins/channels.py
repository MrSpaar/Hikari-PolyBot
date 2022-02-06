from hikari import VoiceStateUpdateEvent
from lightbulb import Plugin, guild_only

plugin = Plugin("Vocaux")
plugin.add_checks(guild_only)


@plugin.listener(VoiceStateUpdateEvent)
async def channel_create(event):
    guild = plugin.bot.cache.get_guild(event.guild_id)

    if not event.state or not event.state.channel_id:
        return

    member = event.state.member
    after = guild.get_channel(event.state.channel_id)
    entry = await plugin.bot.db.fetch_temp_channel(guild.id, member_id=member.id)

    if "Créer" not in after.name or member.is_bot or entry:
        return

    if category := guild.get_channel(after.parent_id):
        overwrites = category.permission_overwrites.values()
    else:
        overwrites = after.permission_overwrites.values()

    text = await guild.create_text_channel(
        name=f"Salon-de-{member.display_name}",
        category=category,
        permission_overwrites=overwrites,
    )

    channel = await guild.create_voice_channel(
        name=f"Salon de {member.display_name}",
        category=category,
        permission_overwrites=overwrites,
    )

    try:
        await member.edit(voice_channel=channel)
        await plugin.bot.db.insert_temp_channel(guild.id, member.id, channel.id, text.id)
    except:
        await channel.delete()
        await text.delete()


@plugin.listener(VoiceStateUpdateEvent)
async def channel_delete(event):
    guild = plugin.bot.cache.get_guild(event.guild_id)

    if not event.old_state or not event.old_state.channel_id:
        return

    before = guild.get_channel(event.old_state.channel_id)
    if not before:
        return

    entry = await plugin.bot.db.fetch_temp_channel(guild.id, voc_id=before.id)

    voice_states = filter(
        lambda vs: guild.get_channel(vs.channel_id) == before,
        guild.get_voice_states().values(),
    )

    count = len([vs.member for vs in voice_states])
    if not entry or count:
        return

    text = guild.get_channel(entry["txt_id"])

    await text.delete()
    await before.delete()
    await plugin.bot.db.delete_temp_channel(entry)


def load(bot):
    bot.add_plugin(plugin)

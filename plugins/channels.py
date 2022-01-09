from hikari import (
    Snowflake,
    Embed,
    Member,
    Role,
    PermissionOverwrite,
    Permissions,
    VoiceStateUpdateEvent
)

from lightbulb import (
    Plugin,
    Context,
    SlashCommand,
    OptionModifier,
    command,
    option,
    implements,
    guild_only,
)

from core.funcs import vc_check

plugin = Plugin("Vocaux")
plugin.add_checks(guild_only, vc_check)


@plugin.command()
@option("nom", "Le nouveau nom du channel", modifier=OptionModifier.CONSUME_REST)
@command("rename", "Modifier le nom de son channel")
@implements(SlashCommand)
async def rename(ctx: Context):
    guild = ctx.get_guild()
    channel = guild.get_channel(guild.get_voice_state(ctx.member).channel_id)
    entry = await ctx.bot.db.pending.find({"guild_id": guild.id, "voc_id": channel.id})

    channel = guild.get_channel(entry["voc_id"])
    await channel.edit(name=ctx.options.nom)

    embed = Embed(color=0x2ECC71, description="✅ Nom modifié")
    await ctx.respond(embed=embed)


@plugin.command()
@option("member", "Le membre qui pourra modifier le channel", Member)
@command("owner", "Définir le propriétaire du channel")
@implements(SlashCommand)
async def owner(ctx: Context):
    guild = ctx.get_guild()
    channel = guild.get_channel(guild.get_voice_state(ctx.member).channel_id)

    entry = await ctx.bot.db.pending.find({"guild_id": guild.id, "voc_id": channel.id})
    await ctx.bot.db.pending.update(entry, {"$set": {"owner": ctx.options.member.id}})

    embed = Embed(color=0x2ECC71, description="✅ Owner modifié")
    await ctx.respond(embed=embed)


@plugin.command()
@option("mentions", "Roles ou membres qui ont accès au channel", Snowflake, modifier=OptionModifier.GREEDY)
@command("private", "Rendre le channel privé")
@implements(SlashCommand)
async def private(ctx: Context):
    guild = ctx.get_guild()
    channel = guild.get_channel(guild.get_voice_state(ctx.member).channel_id)

    entry = await ctx.bot.db.pending.find({"guild_id": guild.id, "voc_id": channel.id})

    guild = ctx.get_guild()
    channel = guild.get_channel(entry["voc_id"])
    text = guild.get_channel(entry["txt_id"])

    if ctx.options.mentions:
        overwrites = [
            PermissionOverwrite(
                type=0 if isinstance(entry, Role) else 1,
                id=entry[0].id,
                allow=Permissions.VIEW_CHANNEL,
            )
            for entry in ctx.options.mentions
        ]

        overwrites.append(PermissionOverwrite(type=0, id=guild.id, deny=Permissions.VIEW_CHANNEL))
    elif not ctx.options.entries and (parent := guild.get_channel(channel.parent_id)):
        overwrites = parent.permission_overwrites.values()
    else:
        overwrites = {
            guild.id: PermissionOverwrite(
                type=0, id=guild.id, allow=Permissions.VIEW_CHANNEL
            )
        }

    await text.edit(permission_overwrites=overwrites)
    await channel.edit(permission_overwrites=overwrites)

    embed = Embed(color=0x2ECC71, description="✅ Permissions modifiées")
    await ctx.respond(embed=embed)


@plugin.listener(VoiceStateUpdateEvent)
async def voice_update(event):
    guild = plugin.bot.cache.get_guild(event.guild_id)

    if event.state and event.state.channel_id:
        after, member = guild.get_channel(event.state.channel_id), event.state.member
        entry = await plugin.bot.db.pending.find(
            {"guild_id": guild.id, "owner": member.id}
        )

        if "Créer" in after.name and not member.is_bot and not entry:
            category = guild.get_channel(after.parent_id)
            overwrites = (
                category.permission_overwrites.values()
                if category
                else after.permission_overwrites.values()
            )

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
                await plugin.bot.db.pending.insert(
                    {
                        "guild_id": guild.id,
                        "owner": member.id,
                        "voc_id": channel.id,
                        "txt_id": text.id,
                    }
                )
            except:
                await channel.delete()
                await text.delete()

    if event.old_state and event.old_state.channel_id:
        before = guild.get_channel(event.old_state.channel_id)
        entry = await plugin.bot.db.pending.find(
            {"guild_id": guild.id, "voc_id": before.id}
        )

        voice_states = filter(
            lambda vs: guild.get_channel(vs.channel_id) == before,
            guild.get_voice_states().values(),
        )
        count = len([vs.member for vs in voice_states])

        if entry and not count:
            text = guild.get_channel(entry["txt_id"])

            await text.delete()
            await before.delete()
            await plugin.bot.db.pending.delete(entry)


def load(bot):
    bot.add_plugin(plugin)

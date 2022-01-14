from hikari import Embed, Message, ShardReadyEvent, GuildReactionAddEvent, MessageFlag
from lavasnek_rs import Lavalink, LavalinkBuilder, Track
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


class EventHandler:
    async def track_finish(self, lavalink: Lavalink, event):
        await update_queue(lavalink, event.guild_id)


async def create_message(ctx: Context, track) -> Message:
    embed1 = Embed(color=0x3498DB, description=f"🎵 [`{track.info.title}`]({track.info.uri}) de `{track.info.author}`\n🙍 Demandé par {ctx.author.mention}")
    embed2 = Embed(color=0x99AAB5, description="*Pas de vidéos en attente*")

    resp = await ctx.respond(embeds=[embed1, embed2])
    message = await resp.message()

    for emoji in ("⏹️", "⏯️", "⏭️"):
        await message.add_reaction(emoji)

    return message


async def update_queue(lavalink: Lavalink, guild_id: int, track: Track = None):
    node = await lavalink.get_guild_node(guild_id)

    if not node.now_playing and not node.queue:
        return await stop(lavalink, guild_id)

    message = await node.get_data()
    embeds = message.embeds
    np = node.queue[0]

    tracks = [t.track.info for t in node.queue[1:]] + [track.info] if track else []
    queue = [
        f"{i+1}) [`{info.title}`]({info.uri}) de `{info.author}`"
        for i, info in enumerate(tracks)
    ]

    embeds[0].description = f"🎵 [`{np.track.info.title}`]({np.track.info.uri}) de `{np.track.info.author}`\n🙍 Demandé par <@{np.requester}>"
    embeds[1].description = "\n".join(queue) or "*Pas de vidéos en attente*"

    await message.edit(embeds=embeds)


async def stop(lavalink, guild_id):
    node = await lavalink.get_guild_node(guild_id)
    try: await (await node.get_data()).delete()
    except: pass

    await lavalink.destroy(guild_id)
    await lavalink.leave(guild_id)
    await lavalink.remove_guild_node(guild_id)
    await lavalink.remove_guild_from_loops(guild_id)


async def join(ctx):
    states = ctx.bot.cache.get_voice_states_view_for_guild(ctx.get_guild())
    voice_state = list(filter(lambda i: i.user_id == ctx.author.id, states.iterator()))

    if not voice_state:
        embed = Embed(color=0xE74C3C, description="❌ Tu n'es connecté à aucun salon vocal")
        return await ctx.respond(embed=embed, flags=MessageFlag.EPHEMERAL)

    try:
        connection_info = await ctx.bot.data.lavalink.join(ctx.guild_id, voice_state[0].channel_id)
    except TimeoutError:
        embed = Embed(color=0xE74C3C, description="❌ Je n'ai pas pu rejoindre le salon")
        return await ctx.respond(embed=embed, flags=MessageFlag.EPHEMERAL)

    await ctx.bot.data.lavalink.create_session(connection_info)


plugin = Plugin("Musique")
plugin.add_checks(guild_only)


@plugin.listener(ShardReadyEvent)
async def start_lavalink(_):
    try:
        builder = (
            LavalinkBuilder(plugin.bot.get_me().id, plugin.bot._token)
            .set_host("127.0.0.1")
            .set_password("")
        )
        lava_client = await builder.build(EventHandler())

        plugin.bot.data.lavalink = lava_client
    except:
        plugin.bot.remove_plugin(plugin)


@plugin.command()
@option("texte", "Le titre de la vidéo", modifier=OptionModifier.CONSUME_REST)
@command("play", "Écouter une vidéo dans le channel où vous êtes connecté")
@implements(SlashCommand)
async def play(ctx: Context):
    if not await ctx.bot.data.lavalink.get_guild_gateway_connection_info(ctx.guild_id):
        failed = await join(ctx)
        if failed:
            return

    query = await ctx.bot.data.lavalink.auto_search_tracks(ctx.options.texte)

    if not query.tracks:
        embed = Embed(color=0xE74C3C, description="❌ Aucun résultat correspondant à ta recherche")
        return await ctx.respond(embed=embed)

    track = query.tracks[0]
    node = await ctx.bot.data.lavalink.get_guild_node(ctx.guild_id)

    if node.now_playing:
        await update_queue(ctx.bot.data.lavalink, ctx.guild_id, track)
        await ctx.respond("Musique ajoutée", flags=MessageFlag.EPHEMERAL)
    else:
        message = await create_message(ctx, track)
        await node.set_data(message)

    await ctx.bot.data.lavalink.play(ctx.guild_id, track).requester(ctx.author.id).queue()


@plugin.listener(GuildReactionAddEvent)
async def reaction_pressed(event):
    if event.member.is_bot:
        return

    node = await plugin.bot.data.lavalink.get_guild_node(event.guild_id)
    message = await node.get_data()

    await message.remove_reaction(event.emoji_name, user=event.member.id)

    if not message:
        return

    if event.emoji_name == "⏹️":
        await stop(plugin.bot.data.lavalink, event.guild_id)
    elif event.emoji_name == "⏭️":
        await plugin.bot.data.lavalink.skip(event.guild_id)
    elif event.emoji_name == "⏭️" and not node.queue and not node.now_playing:
        await stop(plugin.bot.data.lavalink, event.guild_id)
    elif event.emoji_name == "⏯️" and not node.is_paused:
        await plugin.bot.data.lavalink.pause(event.guild_id)
    else:
        await plugin.bot.data.lavalink.resume(event.guild_id)


def load(bot):
    bot.add_plugin(plugin)

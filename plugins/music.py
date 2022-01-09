from hikari import Embed, ShardReadyEvent
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


async def update_queue(lavalink: Lavalink, guild_id: int, track: Track = None):
    node = await lavalink.get_guild_node(guild_id)
    message = await node.get_data()
    np = node.now_playing

    if not np:
        await _stop(lavalink, guild_id)

        try:
            await message.delete()
        except:
            pass

        return

    embeds = message.embeds

    tracks = [t.track.info for t in node.queue[1:]] + ([track.info] if track else [])
    queue = [
        f"{i+1}) [`{info.title}`]({info.uri}) de `{info.author}`"
        for i, info in enumerate(tracks)
    ]

    embeds[0].description = f"🎵 [`{np.track.info.title}`]({np.track.info.uri}) de `{np.track.info.author}`\n🙍 Demandé par <@{np.requester}>"
    embeds[1].description = "\n".join(queue) or "*Pas de vidéos en attente*"

    await message.edit(embeds=embeds)


class EventHandler:
    async def track_finish(self, lavalink: Lavalink, event):
        await update_queue(lavalink, event.guild_id)

    async def track_exception(self, lavalink: Lavalink, event):
        skip = await lavalink.skip(event.guild_id)
        node = await lavalink.get_guild_node(event.guild_id)

        if not skip:
            embed = Embed(color=0xE74C3C, description="❌ Aucune vidéo à skip")
            await event.message.respond(embed=embed)
        else:
            if not node.queue and not node.now_playing:
                await _stop(event.guild_id)


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


async def _stop(lavalink, guild_id):
    await lavalink.destroy(guild_id)

    await lavalink.leave(guild_id)
    await lavalink.remove_guild_node(guild_id)
    await lavalink.remove_guild_from_loops(guild_id)


async def _join(ctx):
    states = ctx.bot.cache.get_voice_states_view_for_guild(ctx.get_guild())
    voice_state = list(filter(lambda i: i.user_id == ctx.author.id, states.iterator()))

    if not voice_state:
        embed = Embed(color=0xE74C3C, description="❌ Tu n'es connecté à aucun salon vocal")
        return await ctx.respond(embed=embed)

    try:
        connection_info = await ctx.bot.data.lavalink.join(
            ctx.guild_id, voice_state[0].channel_id
        )
    except TimeoutError:
        embed = Embed(color=0xE74C3C, description="❌ Je n'ai pas pu rejoindre le salon")
        return await ctx.respond(embed=embed)

    await ctx.bot.data.lavalink.create_session(connection_info)


@plugin.command()
@option("texte", "Le titre de la vidéo", modifier=OptionModifier.CONSUME_REST)
@command("play", "Écouter une vidéo dans le channel où vous êtes connecté")
@implements(SlashCommand)
async def play(ctx: Context):
    if not await ctx.bot.data.lavalink.get_guild_gateway_connection_info(ctx.guild_id):
        await _join(ctx)

    query = await ctx.bot.data.lavalink.auto_search_tracks(ctx.options.texte)

    if not query.tracks:
        embed = Embed(color=0xE74C3C, description="❌ Aucun résultat correspondant à ta recherche")
        return await ctx.respond(embed=embed)

    track = query.tracks[0]
    node = await ctx.bot.data.lavalink.get_guild_node(ctx.guild_id)

    if node.now_playing:
        await update_queue(ctx.bot.data.lavalink, ctx.guild_id, track)
    else:
        embed1 = Embed(color=0x3498DB, description=f"🎵 [`{track.info.title}`]({track.info.uri}) de `{track.info.author}`\n🙍 Demandé par {ctx.author.mention}",)
        embed2 = Embed(color=0x99AAB5, description="*Pas de vidéos en attente*")

        message = await ctx.respond(embeds=[embed1, embed2])
        await node.set_data(message)

    await ctx.message.delete()
    await ctx.bot.data.lavalink.play(ctx.guild_id, track).requester(ctx.author.id).queue()


@plugin.command()
@command("leave", "Déconnecter le bot du channel")
@implements(SlashCommand)
async def leave(ctx: Context):
    await ctx.message.delete()
    await _stop(ctx.bot.data.lavalink, ctx.guild_id)


@plugin.command()
@command("skip", "Passer la vidéo en cours de lecture")
@implements(SlashCommand)
async def skip(ctx: Context):
    skip = await ctx.bot.data.lavalink.skip(ctx.guild_id)
    node = await ctx.bot.data.lavalink.get_guild_node(ctx.guild_id)

    if not skip:
        embed = Embed(color=0xE74C3C, description="❌ Aucune vidéo en cours de lecture")
        return await ctx.respond(embed=embed)

    if not node.queue and not node.now_playing:
        await ctx._stop(ctx.bot.data.lavalink, ctx.guild_id)

    await ctx.message.delete()


@plugin.command()
@command("pause", "Mettre en pause la vidéo en cours de lecture")
@implements(SlashCommand)
async def pause(ctx):
    await ctx.bot.data.lavalink.pause(ctx.guild_id)
    await ctx.message.delete()


@plugin.command()
@command("resume", "Reprendre la vidéo en cours de lecture")
@implements(SlashCommand)
async def resume(ctx):
    await ctx.bot.data.lavalink.resume(ctx.guild_id)
    await ctx.message.delete()


def load(bot):
    bot.add_plugin(plugin)

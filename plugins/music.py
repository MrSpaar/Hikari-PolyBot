from hikari import Embed, ShardReadyEvent
from lightbulb import Plugin, Context, listener, check, guild_only

from core.cls import Bot
from core.funcs import command
from logging import warning
from lavasnek_rs import Lavalink, LavalinkBuilder, Track


async def update_queue(lavalink: Lavalink, guild_id: int, track: Track = None):
    node = await lavalink.get_guild_node(guild_id)
    message = await node.get_data()
    np = node.now_playing

    if not np:
        await Musique._stop(lavalink, guild_id)

        try: await message.delete()
        except: pass

        return

    embeds = message.embeds

    tracks = [t.track.info for t in node.queue[1:]] + ([track.info] if track else [])
    queue = [f'{i+1}) [`{info.title}`]({info.uri}) de `{info.author}`' for i, info in enumerate(tracks)]

    embeds[0].description = f'🎵 [`{np.track.info.title}`]({np.track.info.uri}) de `{np.track.info.author}`\n🙍 Demandé par <@{np.requester}>'
    embeds[1].description = '\n'.join(queue) or '*Pas de vidéos en attente*'

    await message.edit(embeds=embeds)

class EventHandler:
    async def track_finish(self, lavalink: Lavalink, event):
        await update_queue(lavalink, event.guild_id)

    async def track_exception(self, lavalink: Lavalink, event):
        warning(f"Track exception event happened on guild: {event.guild_id}")

        skip = await lavalink.skip(event.guild_id)
        node = await lavalink.get_guild_node(event.guild_id)

        if not skip:
            embed = Embed(color=0xe74c3c, description='❌ Aucune vidéo à skip')
            await event.message.respond(embed=embed)
        else:
            if not node.queue and not node.now_playing:
                await Musique._stop(event.guild_id)

class Musique(Plugin):
    def __init__(self, bot):
        super().__init__()
        self.bot: Bot = bot

    @listener(ShardReadyEvent)
    async def start_lavalink(self, _):
        try:
            builder = (LavalinkBuilder(self.bot.get_me().id, self.bot._token)
                    .set_host('127.0.0.1').set_password(''))
            lava_client = await builder.build(EventHandler())

            self.bot.data.lavalink = lava_client
        except:
            self.bot.remove_plugin('Musique')

    @staticmethod
    async def _stop(lavalink, guild_id):
        await lavalink.destroy(guild_id)

        await lavalink.leave(guild_id)
        await lavalink.remove_guild_node(guild_id)
        await lavalink.remove_guild_from_loops(guild_id)

    async def _join(self, ctx):
        states = self.bot.cache.get_voice_states_view_for_guild(ctx.get_guild())
        voice_state = list(filter(lambda i: i.user_id == ctx.author.id, states.iterator()))

        if not voice_state:
            embed = Embed(color=0xe74c3c, description="❌ Tu n'es connecté à aucun salon vocal")
            return await ctx.respond(embed=embed)

        try:
            connection_info = await self.bot.data.lavalink.join(ctx.guild_id, voice_state[0].channel_id)
        except TimeoutError:
            embed = Embed(color=0xe74c3c, description="❌ Je n'ai pas pu rejoindre le salon")
            return await ctx.respond(embed=embed)

        await self.bot.data.lavalink.create_session(connection_info)

    @check(guild_only)
    @command(aliases=['p'], brief='leo eve', usage='<recherche ou lien>',
             description='Écouter une vidéo dans un salon vocal')
    async def play(self, ctx: Context, *, query):
        if not await self.bot.data.lavalink.get_guild_gateway_connection_info(ctx.guild_id):
            await self._join(ctx)

        query = await self.bot.data.lavalink.auto_search_tracks(query)

        if not query.tracks:
            embed = Embed(color=0xe74c3c, description='❌ Aucun résultat correspondant à ta recherche')
            return await ctx.respond(embed=embed)

        track = query.tracks[0]
        node = await self.bot.data.lavalink.get_guild_node(ctx.guild_id)

        if node.now_playing:
            await update_queue(self.bot.data.lavalink, ctx.guild_id, track)
        else:
            embed1 = Embed(color=0x3498db, description=f'🎵 [`{track.info.title}`]({track.info.uri}) de `{track.info.author}`\n🙍 Demandé par {ctx.author.mention}')
            embed2 = Embed(color=0x99aab5, description='*Pas de vidéos en attente*')

            message = await ctx.respond(embeds=[embed1, embed2])
            await node.set_data(message)

        await ctx.message.delete()
        await self.bot.data.lavalink.play(ctx.guild_id, track).requester(ctx.author.id).queue()

    @check(guild_only)
    @command()
    async def stop(self, ctx: Context):
        await ctx.message.delete()
        await self._stop(self.bot.data.lavalink, ctx.guild_id)

    @check(guild_only)
    @command(description='Passer la vidéo en cours de lecture')
    async def skip(self, ctx: Context):
        skip = await self.bot.data.lavalink.skip(ctx.guild_id)
        node = await self.bot.data.lavalink.get_guild_node(ctx.guild_id)

        if not skip:
            embed = Embed(color=0xe74c3c, description='❌ Aucune vidéo en cours de lecture')
            return await ctx.respond(embed=embed)

        if not node.queue and not node.now_playing:
            await self._stop(self.bot.data.lavalink, ctx.guild_id)

        await ctx.message.delete()

    @check(guild_only)
    @command(description='Mettre en pause la vidéo en cours de lecture')
    async def pause(self, ctx):
        await self.bot.data.lavalink.pause(ctx.guild_id)
        await ctx.message.delete()

    @check(guild_only)
    @command(description='Reprendre la vidéo en cours de lecture')
    async def resume(self, ctx):
        await self.bot.data.lavalink.resume(ctx.guild_id)
        await ctx.message.delete()


def load(bot):
    bot.add_plugin(Musique(bot))

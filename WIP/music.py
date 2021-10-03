from hikari import Embed, ShardReadyEvent
from lightbulb import Plugin, Context, listener, check, guild_only

from os import environ
from core.cls import Bot
from core.funcs import command
from logging import info, warning
from lavasnek_rs import LavalinkBuilder


class EventHandler:
    async def track_start(self, _lava_client, event):
        info(f"Track started on guild: {event.guild_id}")

    async def track_finish(self, _lava_client, event):
        info(f"Track finished on guild: {event.guild_id}")

    async def track_exception(self, lavalink, event):
        warning(f"Track exception event happened on guild: {event.guild_id}")

        skip = await lavalink.skip(event.guild_id)
        node = await lavalink.get_guild_node(event.guild_id)

        if not skip:
            embed = Embed(color=0xe74c3c, description='❌ Aucune vidéo à skip')
            await event.message.respond(embed=embed)
        else:
            if not node.queue and not node.now_playing:
                await lavalink.stop(event.guild_id)

class Musique(Plugin):
    def __init__(self, bot):
        super().__init__()
        self.bot: Bot = bot

    @listener(ShardReadyEvent)
    async def start_lavalink(self, event):
        builder = (LavalinkBuilder(self.bot.get_me().id, self.bot._token)
                   .set_host('127.0.0.1').set_password(environ['LAVALINK']))
        lava_client = await builder.build(EventHandler())

        self.bot.data.lavalink = lava_client

    async def _join(self, ctx: Context):
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
        await self._join(ctx)
        query = await self.bot.data.lavalink.auto_search_tracks(query)

        if not query.tracks:
            embed = Embed(color=0xe74c3c, description='❌ Aucun résultat correspondant à ta recherche')
            return await ctx.respond(embed=embed)

        track = query.tracks[0]
        await ctx.message.delete()
        await self.bot.data.lavalink.play(ctx.guild_id, track).requester(ctx.author.id).queue()

    @check(guild_only)
    @command(name='video', aliases=['np'],
             description='Voir la vidéo en cours de lecture')
    async def now_playing(self, ctx: Context):
        node = await self.bot.data.lavalink.get_guild_node(ctx.guild_id)
        track = node.now_playing.track.info

        description = f'🎵 [`{track.title}`]({track.uri}) de `{track.author}`\n' + \
                          f'🙍 Demandé par {ctx.author.mention}'

        now_playing = Embed(color=0x3498db, description=description)
        await ctx.respond(embed=now_playing)

    @check(guild_only)
    @command(description="Voir la file d'attente")
    async def queue(self, ctx: Context):
        node = await self.bot.data.lavalink.get_guild_node(ctx.guild_id)

        if queue := [t.track.info for t in node.queue[1:]]:
            queue = '\n'.join([f'{i+1}) [`{t.title}`]({t.uri}) de `{t.author}`' for i, t in enumerate(queue)])
        else:
            queue = '*Pas de vidéos en attente*'

        embed = Embed(color=0x99aab5, description=queue)
        await ctx.respond(embed=embed)

    @check(guild_only)
    @command()
    async def stop(self, ctx: Context):
        await ctx.message.delete()
        await self.bot.data.lavalink.destroy(ctx.guild_id)

        await self.bot.data.lavalink.leave(ctx.guild_id)
        await self.bot.data.lavalink.remove_guild_node(ctx.guild_id)
        await self.bot.data.lavalink.remove_guild_from_loops(ctx.guild_id)

    @check(guild_only)
    @command(description='Passer la vidéo en cours de lecture')
    async def skip(self, ctx: Context):
        skip = await self.bot.data.lavalink.skip(ctx.guild_id)
        node = await self.bot.data.lavalink.get_guild_node(ctx.guild_id)

        if not skip:
            embed = Embed(color=0xe74c3c, description='❌ Aucune vidéo en cours de lecture')
            return await ctx.respond(embed=embed)

        if not node.queue and not node.now_playing:
            await self.bot.data.lavalink.stop(ctx.guild_id)

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


def unload(bot):
    bot.remove_plugin("Musique")

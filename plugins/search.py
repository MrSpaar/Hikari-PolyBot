from hikari import Embed
from lightbulb import Plugin, Context

from core.funcs import get_json, command
from datetime import datetime, timedelta
from yt_dlp import YoutubeDL
import matplotlib.pyplot as plt
from io import BytesIO
from os import environ


class Recherche(Plugin):
    @command(brief='cs ranked', usage='<catégorie> <mots-clés>',
             description='Rechercher des streams Twitch')
    async def twitch(self, ctx: Context, game: str, *keys: str):
        query = f"https://api.twitch.tv/kraken/search/streams?query={game}&limit={100 if keys else 10}"
        headers = {
            'Accept': 'application/vnd.twitchtv.v5+json',
            'Client-ID': environ['TWITCH_CLIENT'],
            'Authorization': f"Bearer {environ['TWITCH_TOKEN']}",
        }

        resp = (await get_json(query, headers))['streams']
        embed = (Embed(color=0x3498db)
                 .set_author(name=f"Twitch - {resp[0]['game']}", icon='https://i.imgur.com/gArdgyC.png'))

        func = lambda s: any(key in s['channel']['status'].lower() for key in keys)
        streams = resp[:10] if not keys else filter(func, resp[:100])

        for stream in streams:
            stream = stream['channel']
            value = f"[{stream['status']}]({stream['url']})"
            embed.add_field(name=stream['display_name'], value=value, inline=True)

        if len(embed.fields) == 0:
            embed.add_field(name='\u200b', value='Aucuns streams trouvés', inline=True)

        await ctx.respond(embed=embed)

    @command(aliases=['yt'], brief='30 sec video', usage='<recherche>',
             description='Rechercher des vidéos youtube')
    async def youtube(self, ctx: Context, *, arg: str):
        url = (YoutubeDL({'format': 'bestaudio/best', 'noplaylist': 'True', 'quiet': 'True'})
               .extract_info(f"ytsearch:{arg}", download=False)['entries'][0]['webpage_url'])
        await ctx.respond(url)

    @command(aliases=['wiki'], brief='chien', usage='<recherche>',
             description='Rechercher des articles wikipedia')
    async def wikipedia(self, ctx: Context, *, arg: str):
        query = f'https://fr.wikipedia.org/w/api.php?action=opensearch&search={arg}&namespace=0&limit=1'
        resp = list(await get_json(query))
        title, url = resp[1][0], resp[3][0]

        query = f'https://fr.wikipedia.org/w/api.php?format=json&action=query&prop=extracts|pageimages&exintro&explaintext&redirects=1&titles={title}'
        resp = dict(await get_json(query))['query']['pages']
        data = next(iter(resp.values()))
        desc = f"{data['extract']} [Lire l'article]({url})"

        embed = (Embed(color=0x546e7a, description=desc)
                 .set_author(name=f'Wikipedia - {title}', icon='https://i.imgur.com/nDTQgbf.png')
                 .set_thumbnail(data['thumbnail']['source'] if 'thumbnail' in data.keys() else ''))

        await ctx.respond(embed=embed)

    @command(brief='Hunter x Hunter', usage="<nom de l'anime>",
             description='Rechercher des animes')
    async def anime(self, ctx: Context, *, name: str):
        resp = (await get_json(f'https://kitsu.io/api/edge/anime?filter[text]={name}'))['data'][0]
        anime = resp['attributes']

        end = datetime.strptime(anime['endDate'], '%Y-%m-%d').strftime('%d/%m/%Y') if anime['endDate'] else 'En cours'
        ep = f"{anime['episodeCount']} épisodes" if anime['episodeCount'] else 'En cours'
        h, m = divmod(int(anime['totalLength']), 60)

        diff = f"{datetime.strptime(anime['startDate'], '%Y-%m-%d').strftime('%d/%m/%Y')} → {end}"

        embed = (Embed(color=0x546e7a, description=anime['synopsis'])
                 .add_field(name='🥇 Score', value=f"{anime['averageRating']}/100", inline=True)
                 .add_field(name='🖥️ Épisodes', value=f"{ep} ({h:d}h{m:02d}min)", inline=True)
                 .add_field(name='📅 Diffusion', value=diff, inline=True)
                 .set_author(name=f"Anime - {anime['titles']['en_jp']}", icon=anime['posterImage']['tiny']))

        await ctx.respond(embed=embed)

    @command(brief='mc.hypixel.net', usage='<adresse IP>',
             description='Afficher des informations sur un serveur')
    async def minecraft(self, ctx: Context, *, ip):
        resp = await get_json(f'https://api.mcsrvstat.us/2/{ip}')

        if not resp['online']:
            embed = Embed(color=0xe74c3c, description="❌ Le serveur n'est pas en ligne")
            return await ctx.respond(embed=embed)

        versions = ', '.join(resp['version']) if isinstance(resp['version'], list) else resp['version']
        plugins = ', '.join([plugin['name'] for plugin in resp['plugins']]) if 'plugins' in resp else ''
        mods = ', '.join(resp['mods']['names']) if 'mods' in resp else ''

        description = f"🟢 Serveur en ligne, {resp['players']['online']} joueurs connectés\n" + \
                      f"🔢 Versions supportées : {versions}\n" + \
                      (f"🔌 Plugins du serveur : {plugins}" if plugins else '') + \
                      (f"💾 Mods du serveur : {mods}" if mods else '')

        embed = (Embed(color=0xfeca57, description=description)
                 .set_author(name=f"{resp['hostname']} - {resp['ip']}", icon=resp['icon'] if 'icon' in resp else 'https://media.minecraftforum.net/attachments/300/619/636977108000120237.png'))

        await ctx.respond(embed=embed)

    @command(aliases=['weather'], brief='Nancy', usage='<ville>',
             description="Donne la météo d'une ville sur un jour")
    async def meteo(self, ctx: Context, *, city: str):
        query = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&APPID={environ['WEATHER_TOKEN']}"
        resp = await get_json(query)
        today, now = resp['list'][0], datetime.now()
        info = {'wind': f"{today['wind']['speed']} km/h",
                'humidity': f"{today['main']['humidity']} %",
                'rain': f"{round(today['rain']['3h']/3, 2)} mm/h" if 'rain' in today.keys() else '0 mm/h',
                'ID': today['weather'][0]['icon'] + '.png'}

        data = {entry['dt_txt'][:10]: [] for entry in resp['list']}
        for entry in resp['list']:
            temp = [entry['dt_txt'][11:-6]+'h', entry['main']['temp']]
            data[entry['dt_txt'][:10]].append(temp)

        days = [now.strftime('%Y-%m-%d'), (now + timedelta(hours=24)).strftime('%Y-%m-%d')]
        data = [item for d, l in data.items() if d in days for item in l]
        hours, temps = [], []

        for hour in data:
            if hour[0] not in hours:
                hours.append(hour[0])
                temps.append(hour[1])

        fig, ax = plt.subplots()
        ax.plot(hours, temps, color='#feca57', marker='o', lw=2, ls='--')

        ax.grid()
        ax.fill_between(hours, 0, temps, alpha=.3, color='#1dd1a1')
        ax.set(xlim=(0, len(hours) - 1), ylim=(0, None), xticks=hours)
        ax.tick_params(axis='x', colors='white', pad=5)
        ax.tick_params(axis='y', colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('#2F3136')
        ax.spines['right'].set_color('#2F3136')
        ax.spines['left'].set_color('white')
        ax.set_facecolor('#2F3136')
        fig.patch.set_facecolor('#2F3136')

        stream = BytesIO()
        plt.savefig(stream, bbox_inches='tight')
        stream.seek(0)

        embed = (Embed(title=f"🌦️ Prévisions météo à {city.title()}", color=0x3498db)
                 .add_field(name='\u200b', value=f"Vent : {info['wind']}", inline=True)
                 .add_field(name='\u200b', value=f"Humidité : {info['humidity']}", inline=True)
                 .add_field(name='\u200b', value=f"Pluie : {info['rain']}", inline=True)
                 .set_image(stream)
                 .set_thumbnail('https://openweathermap.org/img/w/' + info['ID']))

        await ctx.respond(embed=embed)


def load(bot):
    bot.add_plugin(Recherche())

def unload(bot):
    bot.remove_plugin('Recherche')

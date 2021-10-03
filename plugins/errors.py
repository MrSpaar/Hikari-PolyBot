from hikari import Embed
from lightbulb import Plugin, listener, errors
from lightbulb.events import CommandErrorEvent

from core.cls import Bot
from difflib import get_close_matches as gcm


class Erreurs(Plugin):
    def __init__(self, bot, name=None):
        super().__init__(name=name)
        self.bot: Bot = bot

    @listener(CommandErrorEvent)
    async def on_command_error(self, event):
        if not event.context:
            guild = self.bot.cache.get_guild(event.message.guild_id)
            channel = guild.get_channel(event.message.channel_id)

            closest = gcm(event.message.content.split()[0][1:], [cmd.name for cmd in self.bot.commands])
            print(closest)
            embed = Embed(color=0xe74c3c, description=f"❌ Commande inexistante{'' if not closest else ', peut-être voulais-tu utiliser `' + closest[0] + '` ?'}")
            return await channel.send(embed=embed)

        ctx, error = event.context, event.exception

        handled = {
            errors.MissingRequiredPermission: "❌ Tu n'as pas la permission de faire ça",
            errors.MissingRequiredRole: "❌ Tu n'as pas la permission de faire ça",
            errors.BotMissingRequiredPermission: "❌ Je n'ai pas la permission de faire ça",
            errors.NotEnoughArguments: f"❌ Il manque des arguments : `{', '.join(getattr(error, 'missing_args', ''))}`",
            errors.CheckFailure: "❌ Tu n'es pas le créateur de ce channel ou tu n'es pas connecté à un channel",
            errors.CommandIsOnCooldown: "❌ Commande en cooldown",
            errors.OnlyInGuild: "❌ Cette commande n'est utilisable que sur un serveur",
            errors.ConverterFailure: {
                'member': '❌ Membre inexistant',
                'emoji': "❌ Cette commande ne marche qu'avec les emojis custom",
                'channel': '❌ Channel introuvable',
                'int': '❌ Les arguments doivent être des nombres entiers'
            },
            errors.CommandInvocationError: {
                'Not temp': "❌ Tu n'es pas dans un channel temporaire",
                'Not owner': "❌ Tu n'es pas le créateur de ce channel",
                'channel': "❌ Tu n'es connecté à aucun channel",
                'string index': '❌ Erreur dans la conversion',
                'list index': "❌ Recherche invalide, aucun résultat trouvé",
                'UnknownObjectException': "❌ Recherche invalide, aucun résultat trouvé",
                'not enough values to unpack': "❌ Lancer invalide",
                "KeyError: 'list'": "❌ Ville introuvable ou inexistante",
                'This video may be': "❌ Restriction d'âge, impossible de jouer la vidéo",
                'No video formats found': "❌ Aucun format vidéo trouvé, impossible de jouer la vidéo",
                'RecursionError': '❌ Trop de récursions, nombre trop grand',
                '4000': "❌ Mon message est trop long, impossible de l'envoyer",
            },
        }

        if type(error) not in handled:
            raise error

        error_entry = handled[type(error)]
        if isinstance(error_entry, dict):
            for key, value in error_entry.items():
                if key in str(error):
                    error_entry = value

        if isinstance(error_entry, dict):
            raise error

        if ctx and ctx.command and type(error) not in [errors.MissingRequiredPermission, errors.MissingRequiredRole]:
            error_entry += f"\nExemple d'utilisation : `{'-' if self.bot.debug else '!'}{ctx.command.qualified_name} {ctx.command.brief}`"

        embed = Embed(color=0xe74c3c, description=error_entry)
        await ctx.respond(embed=embed)


def load(bot):
    bot.add_plugin(Erreurs(bot))

def unload(bot):
    bot.remove_plugin('Erreurs')

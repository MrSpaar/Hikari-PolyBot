from hikari import Embed
from lightbulb import Plugin, CommandErrorEvent, errors

from difflib import get_close_matches as gcm

plugin = Plugin("Erreurs")


@plugin.listener(CommandErrorEvent)
async def on_command_error(self, event):
    if not event.context:
        guild = self.bot.cache.get_guild(event.message.guild_id)
        channel = guild.get_channel(event.message.channel_id)

        closest = gcm(
            event.message.content.split()[0][1:],
            [cmd.name for cmd in self.bot.commands],
        )

        embed = Embed(color=0xE74C3C, description=f"❌ Commande inexistante")
        embed.description += f', peut-être voulais-tu utiliser `{closest[0]}` ?' if closest else '.'

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
        errors.NotOwner: "❌ Seul le créateur du bot peut utiliser cette commande",
        errors.ConverterFailure: {
            "member": "❌ Membre inexistant",
            "emoji": "❌ Cette commande ne marche qu'avec les emojis custom",
            "channel": "❌ Channel introuvable",
            "int": "❌ Les arguments doivent être des nombres entiers",
        },
        errors.CommandInvocationError: {
            "Not temp": "❌ Tu n'es pas dans un channel temporaire",
            "Not owner": "❌ Tu n'es pas le créateur de ce channel",
            "channel": "❌ Tu n'es connecté à aucun channel",
            "string index": "❌ Erreur dans la conversion",
            "list index": "❌ Recherche invalide, aucun résultat trouvé",
            "UnknownObjectException": "❌ Recherche invalide, aucun résultat trouvé",
            "not enough values to unpack": "❌ Lancer invalide",
            "KeyError: 'list'": "❌ Ville introuvable ou inexistante",
            "This video may be": "❌ Restriction d'âge, impossible de jouer la vidéo",
            "No video formats found": "❌ Aucun format vidéo trouvé, impossible de jouer la vidéo",
            "RecursionError": "❌ Trop de récursions, nombre trop grand",
            "4000": "❌ Mon message est trop long, impossible de l'envoyer",
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

    embed = Embed(color=0xE74C3C, description=error_entry)
    await ctx.respond(embed=embed)


def load(bot):
    bot.add_plugin(plugin)

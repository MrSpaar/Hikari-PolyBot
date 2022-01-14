from hikari import Embed, MessageFlag
from lightbulb import Plugin, SlashCommandErrorEvent, errors

plugin = Plugin("Erreurs")


@plugin.listener(SlashCommandErrorEvent)
async def on_command_error(event):
    ctx, error = event.context, event.exception.__cause__

    handled = {
        errors.MissingRequiredPermission: "❌ Tu n'as pas la permission de faire ça",
        errors.MissingRequiredRole: "❌ Tu n'as pas la permission de faire ça",
        errors.BotMissingRequiredPermission: "❌ Je n'ai pas la permission de faire ça",
        errors.CheckFailure: "❌ Tu n'as pas la permission de faire ça",
        errors.OnlyInGuild: "❌ Cette commande n'est utilisable que sur un serveur",
        errors.NotOwner: "❌ Seul le créateur du bot peut utiliser cette commande",
    }

    if type(error) not in handled:
        raise error

    embed = Embed(color=0xE74C3C, description=handled[type(error)])
    await ctx.respond(embed=embed, flags=MessageFlag.EPHEMERAL)


def load(bot):
    bot.add_plugin(plugin)

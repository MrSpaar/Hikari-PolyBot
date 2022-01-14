from hikari import Member, Embed, InteractionCreateEvent, SelectMenuComponent, CommandInteraction
from hikari.impl import ActionRowBuilder
from lightbulb import (
    Context,
    Plugin,
    SlashCommand,
    command,
    option,
    implements,
    add_checks,
    guild_only,
)

from games.minesweeper import Minesweeper
from games.hangman import Hangman
from games.chess import Chess
from random import randint, choice
from datetime import datetime
from asyncio import sleep

plugin = Plugin("Jeux")


@plugin.command()
@add_checks(guild_only)
@option("membre", "La personne contre qui tu veux jouer", Member)
@command("chess", "Jouer aux échecs contre quelqu'un")
@implements(SlashCommand)
async def chess(ctx: Context):
    if ctx.options.membre.is_bot or ctx.options.membre == ctx.member:
        return await ctx.respond("Tu ne peux pas jouer contre un bot ou contre toi-même")

    await ctx.respond("\u200b")
    await Chess(ctx).start()


@plugin.command()
@command("pendu", "Jouer au pendu")
@implements(SlashCommand)
async def pendu(ctx: Context):
    await Hangman(ctx).start()


@plugin.command()
@command("demineur", "Jouer au démineur")
@implements(SlashCommand)
async def demineur(ctx: Context):
    await ctx.respond("Commande en cours de développement")
    # await Minesweeper(ctx).start()


@plugin.command()
@add_checks(guild_only)
@command("regles", "Message d'aide pour jouer aux échecs")
@implements(SlashCommand)
async def regles(ctx: Context):
    embed = (
        Embed(color=0x3498DB)
        .add_field(
            inline=False,
            name="Pour jouer",
            value="Envoie un message sous une des deux formes supportées :\n"
            + "    • SAN : représentation usuelle (`a4`, `Nf5`, ...)\n"
            + "    • UCI : représentation universelle `départarrivée` (`a2a4`, `b1c3`, ...)\n"
            + "\n Les promotions sous le format UCI se font en ajoutant un `q` à la fin (`a2a1q` par exemple)",
        )
        .add_field(
            inline=False,
            name="Autres fonctionnalités",
            value="Envoie `quit` pour abandonner la partie.\n",
        )
        .set_footer(text="⚠️ Ne pas mettre ! dans vos messages")
    )

    await ctx.respond(embed=embed)


@plugin.command()
@option("face", "La face sur laquelle tu paries")
@command("coinflip", "Jouer au pile ou face")
@implements(SlashCommand)
async def coinflip(ctx: Context):
    result = choice(["Pile", "Face"])

    if ctx.options.face.title() not in ["Pile", "Face"]:
        color = 0xE74C3C
        desc = "❌ Tu dois entrer `pile` ou `face` !"
    elif ctx.options.face.title() in result:
        color = 0xF1C40F
        desc = f"🪙 {result} ! Tu as gagné."
    else:
        color = 0xE74C3C
        desc = f"🪙 {result} ! Tu as perdu."

    embed = Embed(color=color, description=desc)
    await ctx.respond(embed=embed)


@plugin.command()
@option("chaine", "Chaine de caractères sous la forme d'un lancé de dé Roll20 (2d10+3d20 par exemple)")
@command("roll", "Faire une lancer de dés")
@implements(SlashCommand)
async def roll(ctx: Context):
    try:
        content = ctx.options.chaine.split("+")
        rolls = [int(content.pop(i)) for i in range(len(content)) if content[i].isdigit()]

        for elem in content:
            n, faces = elem.split("d") if elem.split("d")[0] != "" else (1, elem[1:])
            rolls += [randint(1, int(faces)) for _ in range(int(n))]

        rolls_str = " + ".join([str(n) for n in rolls])
    except:
        embed = Embed(color=0xE74C3C, description="❌ Lancer invalide")
        return await ctx.respond(embed=embed)

    embed = Embed(
        color=0xF1C40F,
        description=f"**🎲 Résultat du lancé :** {rolls_str} = **{sum(rolls)}**",
    )

    await ctx.respond(embed=embed)


@plugin.command()
@command("reaction", "Tester son temps de réaction")
@implements(SlashCommand)
async def reaction(ctx: Context):
    component = ActionRowBuilder()
    component.add_button(2, str(ctx.author.id)).set_label(
        "Appuie quand tu es prêt"
    ).add_to_container()
    message = await ctx.respond("\u200b", component=component)

    event = await ctx.bot.wait_for(
        InteractionCreateEvent,
        predicate=lambda event: event.interaction.custom_id == str(ctx.author.id),
        timeout=None,
    )

    component = ActionRowBuilder()
    component.add_button(4, str(ctx.author.id)).set_label(
        "Appuie dès que je change de couleur"
    ).add_to_container()
    await event.interaction.create_initial_response(
        response_type=7, components=[component]
    )

    await sleep(randint(2, 10))
    temp = await ctx.get_channel().fetch_message(event.interaction.message.id)

    if not temp.components:
        return

    component = ActionRowBuilder()
    component.add_button(3, str(ctx.author.id)).set_label(
        "Maintenant !"
    ).add_to_container()
    await message.edit(component=component)
    start = datetime.now()

    event = await ctx.bot.wait_for(
        InteractionCreateEvent,
        predicate=lambda event: event.interaction.custom_id == str(ctx.author.id),
        timeout=None,
    )
    td = datetime.now() - start
    td = round(td.seconds + td.microseconds / 1000000 - ctx.bot.heartbeat_latency, 3)

    embed = Embed(
        color=0x3498DB, description=f"⏱️ Ton temps de réaction : `{td}` secondes"
    )
    await event.interaction.create_initial_response(
        response_type=7, components=[], embed=embed
    )


@plugin.listener(InteractionCreateEvent)
async def on_button_click(event):
    if isinstance(event.interaction, CommandInteraction):
        return

    interaction = event.interaction
    button = interaction.message.components[0].components[0]

    if isinstance(button, SelectMenuComponent):
        return

    if button.label == 'Appuie dès que je change de couleur' and button.style == 4:
        embed = Embed(color=0xe74c3c, description='❌ Tu as appuyé trop tôt')
        return await event.interaction.create_initial_response(response_type=7, components=[], embed=embed)


def load(bot):
    bot.add_plugin(plugin)

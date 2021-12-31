from hikari import Member, Embed, SelectMenuComponent, InteractionCreateEvent
from hikari.impl import ActionRowBuilder
from lightbulb import Context, Plugin, check, listener, guild_only

from games.minesweeper import Minesweeper
from games.hangman import Hangman
from games.dchess import Chess
from core.funcs import command
from random import randint, choice
from datetime import datetime
from asyncio import sleep


class Fun(Plugin):
    @check(guild_only)
    @command(aliases=['chess'], brief='@Noah Conrard', usage='<membre>',
             description="Jouer aux échecs contre quelqu'un (!regles echecs)")
    async def echecs(self, ctx: Context, opponent: Member):
        if opponent.is_bot or opponent == ctx.member:
            return await ctx.send('Tu ne peux pas jouer contre un bot ou contre toi-même')
        
        await Chess(ctx, opponent).start()

    @command(aliases=['hangman'], description='Jouer au pendu')
    async def pendu(self, ctx: Context):
        await Hangman(ctx).start()

    @command(aliases=['minesweeper'], description='Jouer au démineur (!regles demineur)')
    async def demineur(self, ctx: Context):
        await ctx.respond('Commande en cours de développement')
        # await Minesweeper(ctx).start()

    @command(brief='echecs', usage='<echecs ou demineur>',
             description='Afficher une aide pour jouer aux échecs ou au démineur')
    async def regles(self, ctx: Context, game: str):
        if game.lower() in ['démineur', 'demineur']:
            embed = (Embed(color=0x3498db)
                     .add_field(name='Pour jouer', value='Envois un message sous la forme `action,ligne,colonne` :\n' +
                                                         '    • `f` pour mettre un drapeau\n' +
                                                         '    •  `m` pour révéler une case\n\n' +
                                                         'Par exemple : `m,2,1` pour révéler la case à la deuxième ligne, première colonne.')
                     .add_field(inline=False, name='Autres fonctionnalités', value='Envoie `quit` pour abandonner la partie.\n' +
                                                                                   'Envoie `repost` pour renvoyer une grille (garde la progression)'))
        else:
            embed = (Embed(color=0x3498db)
                     .add_field(inline=False, name='Pour jouer',
                                value='Envoie un message sous une des deux formes supportées :\n' +
                                      '    • SAN : représentation usuelle (`a4`, `Nf5`, ...)\n' +
                                      '    • UCI : représentation universelle `départarrivée` (`a2a4`, `b1c3`, ...)\n' +
                                      '\n Les promotions sous le format UCI se font en ajoutant un `q` à la fin (`a2a1q` par exemple)')
                     .add_field(inline=False, name='Autres fonctionnalités', value='Envoie `quit` pour abandonner la partie.\n'))

        embed.set_footer(text='⚠️ Ne pas mettre ! dans vos messages')
        await ctx.respond(embed=embed)

    @command(aliases=['pof', 'hot'], brief='pile', usage='<pile ou face>',
             description='Jouer au pile ou face contre le bot')
    async def toss(self, ctx: Context, arg: str):
        result = choice(['Pile', 'Face'])

        if arg.title() not in ['Pile', 'Face']:
            color = 0xe74c3c
            desc = '❌ Tu dois entrer `pile` ou `face` !'
        elif arg.title() in result:
            color = 0xf1c40f
            desc = f'🪙 {result} ! Tu as gagné.'
        else:
            color = 0xe74c3c
            desc = f'🪙 {result} ! Tu as perdu.'

        embed = Embed(color=color, description=desc)
        await ctx.respond(embed=embed)

    @command(brief='2d6+5d20+20', usage='<texte>',
             description='Faire une lancer de dés')
    async def roll(self, ctx: Context, dices: str):
        content = dices.split('+')
        rolls = [int(content.pop(i))
                 for i in range(len(content)) if content[i].isdigit()]

        for elem in content:
            n, faces = elem.split('d') if elem.split('d')[0] != '' else (1, elem[1:])
            rolls += [randint(1, int(faces)) for _ in range(int(n))]

        rolls_str = ' + '.join([str(n) for n in rolls])

        embed = Embed(color=0xf1c40f, description=f"**🎲 Résultat du lancé :** {rolls_str} = **{sum(rolls)}**")
        await ctx.respond(embed=embed)

    @command(description='Tester son temps de réaction')
    async def reaction(self, ctx: Context):
        component = ActionRowBuilder()
        component.add_button(2, str(ctx.author.id)).set_label('Appuie quand tu es prêt').add_to_container()
        message = await ctx.respond('\u200b', component=component)

        event = await ctx.bot.wait_for(InteractionCreateEvent, predicate=lambda event: event.interaction.custom_id==str(ctx.author.id), timeout=None)

        component = ActionRowBuilder()
        component.add_button(4, str(ctx.author.id)).set_label('Appuie dès que je change de couleur').add_to_container()
        await event.interaction.create_initial_response(response_type=7, components=[component])

        await sleep(randint(2,10))
        temp = await ctx.get_channel().fetch_message(event.interaction.message.id)

        if not temp.components:
            return

        component = ActionRowBuilder()
        component.add_button(3, str(ctx.author.id)).set_label('Maintenant !').add_to_container()
        await message.edit(component=component)
        start = datetime.now()

        event = await ctx.bot.wait_for(InteractionCreateEvent, predicate=lambda event: event.interaction.custom_id==str(ctx.author.id), timeout=None)
        td = datetime.now() - start
        td = round(td.seconds+td.microseconds/1000000-ctx.bot.heartbeat_latency, 3)

        embed = Embed(color=0x3498db, description=f'⏱️ Ton temps de réaction : `{td}` secondes')
        await event.interaction.create_initial_response(response_type=7, components=[], embed=embed)

    @listener(InteractionCreateEvent)
    async def on_button_click(self, event):
        interaction = event.interaction
        button = interaction.message.components[0].components[0]

        if isinstance(button, SelectMenuComponent):
            return

        if button.label == 'Appuie dès que je change de couleur' and button.style == 4:
            embed = Embed(color=0xe74c3c, description='❌ Tu as appuyé trop tôt')
            return await event.interaction.create_initial_response(response_type=7, components=[], embed=embed)


def load(bot):
    bot.add_plugin(Fun())

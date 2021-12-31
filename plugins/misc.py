from hikari import Embed, User, Emoji
from lightbulb import Plugin, Context, Group

from inspect import getsource
from core.funcs import command
from core.cls import Bot
from os import remove


class Divers(Plugin):
    def __init__(self, bot, name=None):
        super().__init__(name=name)
        self.bot: Bot = bot

    @command(brief='utilitaire', usage='<argument>',
             description='Faire apparaître ce menu')
    async def help(self, ctx: Context, arg: str = None, sub: str = None):
        embed = Embed(color=0x3498db, title='Aide - ')

        if (arg or sub) and (command := self.bot.get_command(arg)):
            if isinstance(command, Group) and sub:
                sub = command.get_command(sub)

            embed.title += command.name
            embed.description = f'{command.description}.' if not sub else sub.description

            if isinstance(command, Group) and not sub:
                embed.description += f'\nLes sous-commandes disponibles :\nㅤ• ' + \
                                      '\nㅤ• '.join([cmd.name for cmd in command.walk_commands()]) + \
                                     f'\n\n Détail : `{self.bot.cprefix}help {command.name} sous-commande`'
            elif sub:
                embed.description += f'\n\n🙋 Utilisation : `{self.bot.cprefix}{command.name} {sub.name} {sub.usage}`\n' + \
                                     f'👉 Exemple : `{self.bot.cprefix}{command.name} {sub.name} {sub.brief}`'
            else:
                embed.description += f'\n\n🙋 Utilisation : `{self.bot.cprefix}{command.name} {command.usage}`\n' + \
                                     f'👉 Exemple : `{self.bot.cprefix}{command.name} {command.brief}`'
        elif arg and (plugin := self.bot.get_plugin(arg.title())):
            embed.title += plugin.name
            embed.description = '\n'.join([f'`{self.bot.cprefix}{command.name}` : {command.description}' for command in plugin.commands])
            embed.description += f'\n\nDétail : `{self.bot.cprefix}help commande`'
        else:
            plugins = ['Configuration', 'Moderation', 'Musique', 'Niveaux', 'Recherche', 'Informations', 'Vocaux', 'Fun', 'Maths', 'Divers', 'Menus']
            embed.title += 'Modules'
            embed.description = f'Les modules disponibles :\nㅤ• ' + '\n\ㅤ• '.join(plugins) + '\n\nDétail : `!help catégorie`'

        await ctx.respond(embed=embed)

    @command(aliases=['poll'], brief="Êtes-vous d'accord ? | Oui | Non",
             usage='<question> | <choix 1> | <choix 2> | ...',
             description='Faire un sondage (9 choix au maximum)')
    async def sondage(self, ctx: Context, *, args: str):
        items = [arg.strip() for arg in args.split('|')]
        question = items[0]
        reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
        embed = (Embed(title=f'>> {question[0].upper() + question[1:]}', color=0x3498db)
                 .set_author(name=f'Sondage de {ctx.member.display_name}', icon=ctx.author.avatar_url))

        await ctx.message.delete()

        for i in range(1, len(items)):
            embed.add_field(name=f"{reactions[i-1]} Option n°{i}", value=f'```{items[i]}```', inline=False)

        message = await ctx.respond(embed=embed)

        for i in range(len(items[1:])):
            await message.add_reaction(reactions[i])

    @command(brief='@[!] Polybot', usage='<mention>',
             description="Afficher l'image de profil d'un membre")
    async def pfp(self, ctx: Context, member: User = None):
        member = member or ctx.member
        embed = (Embed(color=member.get_top_role().color)
                 .set_image(member.avatar_url))

        await ctx.respond(embed=embed)

    @command(brief=':pepeoa:', usage='<emoji custom>',
             description="Afficher l'image d'origine d'un emoji")
    async def emoji(self, ctx: Context, emoji: Emoji):
        embed = (Embed(color=ctx.member.get_top_role().color)
                 .set_image(emoji.url)
                 .set_footer(text=f'<:{emoji.name}:{emoji.id}>'))

        await ctx.respond(embed=embed)

    @command(description='Envoyer le lien vers le code source du bot')
    async def repo(self, ctx: Context):
        await ctx.respond('https://github.com/MrSpaar/PolyBot')

    @command(description='Afficher le format pour envoyer du code',)
    async def code(self, ctx: Context):
        await ctx.respond('\`\`\`py\nTon code\n\`\`\`')

def load(bot):
    bot.add_plugin(Divers(bot))

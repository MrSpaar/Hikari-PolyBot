from lightbulb import Plugin, Context, SlashCommand, OptionModifier, command, option, implements
from hikari import Embed

from core.funcs import api_call

plugin = Plugin('Mathematiques')


def base_conv(k: int, b: int, n: int):
    def to_base(num, b, numerals='0123456789abcdefghijklmnopqrstuvwxyxABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        return ((num == 0) and numerals[0]) or (to_base(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b])

    return to_base(int(str(k), b), n)


@plugin.command()
@option('calcul', 'Le calcul dont tu veux le résultat', modifier=OptionModifier.CONSUME_REST)
@command('calcul', "Obtenir le résultat d'un calcul")
@implements(SlashCommand)
async def calcul(ctx: Context):
    query = ctx.options.calcul.replace('+', '%2B').replace('x', '*')
    result = await api_call(f"https://api.mathjs.org/v4/?expr={query}", json=False)

    embed = Embed(color=0x3498db, description=f':pager: `{expr}` = `{result}`')
    await ctx.respond(embed=embed)


@plugin.command()
@option('base1', 'La base du nombre à convertir', int)
@option('base2', 'La base du nombre converti', int)
@option('nombre', 'Le nombre à convertir')
@command('base', "Convertir un nombre d'une base à une autre base (base 62 maximum)")
@implements(SlashCommand)
async def base(ctx: Context):
    if ctx.options.base1 > 62 or ctx.options.base2 > 62:
        return await ctx.respond('❌ Base trop grande (base 52 maximum)')

    conv = base_conv(ctx.options.nombre, ctx.options.base1, ctx.options.base2)
    embed = Embed(color=0x3498db, description=f'⚙️ `{ctx.options.nombre}` en base {ctx.options.base2} : `{conv}`')
    await ctx.respond(embed=embed)


@plugin.command()
@option('texte', 'Le texte à convertir en binaire', modifier=OptionModifier.CONSUME_REST)
@command('binaire', description='Convertir du texte en binaire')
@implements(SlashCommand)
async def binaire(ctx: Context):
    try:
        conv = [bin(int(ctx.options.texte))[2:]]
    except:
        conv = [bin(s)[2:] for s in bytearray(ctx.options.texte, 'utf-8')]

    embed = Embed(color=0x3498db, description=f'⚙️ Binaire : `{"".join(conv)}`')
    await ctx.respond(embed=embed)


@plugin.command()
@option('texte', 'Le texte à convertir en hexadécimal', modifier=OptionModifier.CONSUME_REST)
@command('hexa', 'Convertir du texte en hexadécimal')
@implements(SlashCommand)
async def hexa(ctx: Context):
    embed = Embed(color=0x3498db, description=f'⚙️ Hexadécimal : `{ctx.options.texte.encode().hex()}`')
    await ctx.respond(embed=embed)


def load(bot):
    bot.add_plugin(plugin)

from hikari import Embed
from lightbulb import (
    Plugin,
    Context,
    SlashCommandGroup,
    SlashSubCommand,
    OptionModifier,
    command,
    option,
    implements,
)

from src.funcs import api_call

plugin = Plugin("Mathematiques")


@plugin.command()
@command("math", "Groupes de commandes en rapport avec les maths")
@implements(SlashCommandGroup)
async def math(ctx: Context):
    pass


def base_conv(k: int, b: int, n: int):
    def to_base(num, b, numerals="0123456789abcdefghijklmnopqrstuvwxyxABCDEFGHIJKLMNOPQRSTUVWXYZ",):
        return ((num == 0) and numerals[0]) or (
            to_base(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b]
        )

    return to_base(int(str(k), b), n)


@math.child
@option("calcul", "Le calcul dont tu veux le résultat", modifier=OptionModifier.CONSUME_REST)
@command("calcul", "Obtenir le résultat d'un calcul")
@implements(SlashSubCommand)
async def calcul(ctx: Context):
    query = ctx.options.calcul.replace("+", "%2B").replace("x", "*")
    result = await api_call(f"https://api.mathjs.org/v4/?expr={query}", json=False)

    embed = Embed(color=0x3498DB, description=f":pager: `{ctx.options.calcul}` = `{result}`")
    await ctx.respond(embed=embed)


@math.child
@option("base_arrivee", "La base du nombre à convertir", int)
@option("base_initiale", "La base du nombre converti", int)
@option("nombre", "Le nombre à convertir")
@command("base", "Convertir un nombre d'une base à une autre base (base 62 maximum)")
@implements(SlashSubCommand)
async def base(ctx: Context):
    if ctx.options.base_initiale > 62 or ctx.options.base_arrivee > 62:
        return await ctx.respond("❌ Base trop grande (base 52 maximum)")

    conv = base_conv(ctx.options.nombre, ctx.options.base_initiale, ctx.options.base_arrivee)
    embed = Embed(color=0x3498DB, description=f"⚙️ `{ctx.options.nombre}` en base {ctx.options.base_arrivee} : `{conv}`")
    await ctx.respond(embed=embed)


@math.child
@option("texte", "Le texte à convertir en binaire", modifier=OptionModifier.CONSUME_REST)
@command("binaire", description="Convertir du texte en binaire")
@implements(SlashSubCommand)
async def binaire(ctx: Context):
    try:
        conv = [bin(int(ctx.options.texte))[2:]]
    except:
        conv = [bin(s)[2:] for s in bytearray(ctx.options.texte, "utf-8")]

    embed = Embed(color=0x3498DB, description=f'⚙️ `{ctx.options.texte}` = `{"".join(conv)}`')
    await ctx.respond(embed=embed)


@math.child
@option("texte", "Le texte à convertir en hexadécimal", modifier=OptionModifier.CONSUME_REST)
@command("hexa", "Convertir du texte en hexadécimal")
@implements(SlashSubCommand)
async def hexa(ctx: Context):
    embed = Embed(color=0x3498DB, description=f"⚙️ `{ctx.options.texte}` = `{ctx.options.texte.encode().hex()}`",)
    await ctx.respond(embed=embed)


def load(bot):
    bot.add_plugin(plugin)

from lightbulb import Plugin, Context
from hikari import Embed

from core.funcs import api_call, command


class Maths(Plugin):
    @command(aliases=['compute'], brief='3*log(50)', usage='<expression>',
             description="Obtenir le résultat d'un calcul")
    async def calcul(self, ctx: Context, *, expr: str):
        query = expr.replace('+', '%2B').replace('x', '*')
        result = await api_call(f"https://api.mathjs.org/v4/?expr={query}", json=False)

        embed = Embed(color=0x3498db, description=f':pager: `{expr}` = `{result}`')
        await ctx.respond(embed=embed)

    @staticmethod
    def base_conv(k: int, b: int, n: int):
        def to_base(num, b, numerals='0123456789abcdefghijklmnopqrstuvwxyxABCDEFGHIJKLMNOPQRSTUVWXYZ'):
            return ((num == 0) and numerals[0]) or (to_base(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b])

        return to_base(int(str(k), b), n)

    @command(brief='16 f', usage='<base> <nombre>',
             description="Convertir un nombre d'une base à une autre base (base 62 maximum)")
    async def base(self, ctx: Context, from_base: int, to_base: int, num: str):
        if from_base > 62 or to_base > 62:
            return await ctx.respond('❌ Base trop grande (base 52 maximum)')

        conv = self.base_conv(num, from_base, to_base)
        embed = Embed(color=0x3498db, description=f'⚙️ `{num}` en base {to_base} : `{conv}`')
        await ctx.respond(embed=embed)

    @command(aliases=['bin', 'binary'], brief='prout', usage='<texte>',
             description='Convertir du texte en binaire')
    async def binaire(self, ctx: Context, *, arg: str):
        try:
            conv = [bin(int(arg))[2:]]
        except:
            conv = [bin(s)[2:] for s in bytearray(arg, 'utf-8')]

        embed = Embed(color=0x3498db, description=f'⚙️ Binaire : `{"".join(conv)}`')
        await ctx.respond(embed=embed)

    @command(aliases=['hex', 'hexa'], brief='16', usage='<texte>',
             description='Convertir du texte en hexadécimal')
    async def hexadecimal(self, ctx: Context, *, arg: str):
        embed = Embed(color=0x3498db, description=f'⚙️ Hexadécimal : `{arg.encode().hex()}`')
        await ctx.respond(embed=embed)


def load(bot):
    bot.add_plugin(Maths())

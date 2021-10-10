from hikari import Embed
from lightbulb import Context, check, owner_only

from core.cls import Bot
from core.funcs import command

plugins = [
    'WIP.music'
]

bot = Bot(debug=True)

@check(owner_only)
@command(hidden=True)
async def reload(self, ctx: Context):
    for plugin in plugins:
        self.bot.reload_extension(plugin)

    embed = Embed(color=0x2ecc71, description='✅ Tous les plugins ont été relancé')
    await ctx.respond(embed=embed)

bot.load_extension('WIP.music')
bot.run()

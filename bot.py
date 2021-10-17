from hikari import StartedEvent, Activity

from glob import glob
from core.cls import Bot

bot = Bot(debug=False)

@bot.listen(StartedEvent)
async def set_status(_):
    await bot.update_presence(activity=Activity(type=0, name=f'{bot.cprefix}help'))

for plugin in glob('plugins/*.py'):
    plugin = plugin.replace('/', '.')[:-3]
    bot.load_extension(plugin)

bot.run()

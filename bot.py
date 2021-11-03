from hikari import StartedEvent, Activity

from glob import glob
from sys import platform
from core.cls import Bot

bot = Bot(debug=False)

@bot.listen(StartedEvent)
async def set_status(_):
    print('Bot is ready')
    await bot.update_presence(activity=Activity(type=0, name=f'{bot.cprefix}help'))

sep = '/' if platform == 'linux' else '\\'

for plugin in glob('plugins/*.py'):
    plugin = plugin.replace(sep, '.')[:-3]
    bot.load_extension(plugin)


bot.run()

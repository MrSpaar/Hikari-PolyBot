from glob import glob
from core.cls import Bot

bot = Bot(debug=False)

for plugin in glob('plugins/*.py'):
    plugin = plugin.replace('/', '.')[:-3]
    bot.load_extension(plugin)

bot.run()

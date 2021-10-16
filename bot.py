from glob import glob
from core.cls import Bot

bot = Bot(debug=False)

for plugin in (path.replace('/', '.')[:-3] for path in glob('plugins/*.py')):
    bot.load_extension(plugin)

bot.run()

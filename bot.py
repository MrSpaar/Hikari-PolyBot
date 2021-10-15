from glob import glob
from core.cls import Bot

bot = Bot(debug=True)

for plugin in (path.replace('\\', '.')[:-3] for path in glob('plugins/*.py')):
    if plugin in ['plugins.music', 'plugins.errors']:
        continue

    bot.load_extension(plugin)

bot.run()

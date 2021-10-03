from glob import glob
from core.cls import Bot


bot = Bot(debug=True)

# for plugin in glob('FINISHED/*.py'):
#     bot.load_extension(plugin[:-3].replace('\\', '.'))

bot.load_extension('WIP.music')

bot.run()

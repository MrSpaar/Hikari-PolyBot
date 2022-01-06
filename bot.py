from hikari import StartedEvent, Activity
from lightbulb import implements, PrefixCommand, command

from core.cls import Bot

bot = Bot()

@bot.listen(StartedEvent)
async def set_status(_):
    print('Bot is ready')

bot.load_extensions_from('./plugins/')
bot.run()

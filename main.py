from hikari import StartedEvent, Activity

from core.bot import Bot
from core.funcs import get_oauth


def main():
    bot = Bot()


    @bot.listen(StartedEvent)
    async def ready(_):
        # bot.twitch = await get_oauth()
        print("Bot is ready")


    bot.load_extensions_from("./plugins/")
    bot.run(activity=Activity(name='vous observer', type=0))


if __name__ == "__main__":
    main()

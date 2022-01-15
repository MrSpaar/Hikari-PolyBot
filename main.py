from hikari import StartedEvent, Activity

from src.bot import Bot


def main():
    bot = Bot()


    @bot.listen(StartedEvent)
    async def ready(_):
        print("Bot is ready")


    bot.load_extensions_from("./plugins/")
    bot.run(activity=Activity(name='vous observer', type=0))


if __name__ == "__main__":
    main()

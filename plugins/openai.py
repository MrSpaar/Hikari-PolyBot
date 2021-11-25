from lightbulb import Plugin, listener
from hikari.events.message_events import MessageCreateEvent

from aiohttp import ClientSession
from core.funcs import normalize_string
from core.cls import Bot
from os import environ


class OpenAI(Plugin):
    def __init__(self, bot, name=None):
        super().__init__(name=name)
        self.bot: Bot = bot

    @listener(MessageCreateEvent)
    async def on_message(self, event):
        message, channel = event.message, self.bot.cache.get_guild_channel(event.channel_id)
        if not message or not message.content or not message.content[:22] in ['<@713781013830041640> ', '<@!713781013830041640>']:
            return

        question = normalize_string(message.content[22:].strip())
        query = f"Ce qui suit est une conversation avec un assistant IA. L'assistant est serviable, creatif, intelligent et tres sympathique.\\n\\n {question}"
        data = '{"prompt": "%s", "max_tokens": 100, "temperature": 0.1}' % query

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {environ["OPENAI_TOKEN"]}',
        }

        async with channel.trigger_typing():
            async with ClientSession() as s:
                async with s.post('https://api.openai.com/v1/engines/davinci/completions', headers=headers, data=data) as resp:
                    data = await resp.json()

                    if 'error' in data:
                        await message.respond("Quota atteinte, impossible de répondre au message",reply=True)
                    elif 'choices' in data:
                        await message.respond(data['choices'][0]['text'].split('\n\n')[1].strip('—-'), reply=True)
                    else:
                        await message.respond("J'ai pas compris :(", reply=True)


def load(bot):
    bot.add_plugin(OpenAI(bot))

def unload(bot):
    bot.remove_plugin('OpenAI')

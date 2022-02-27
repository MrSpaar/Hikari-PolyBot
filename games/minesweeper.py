from hikari import Message, InteractionCreateEvent
from hikari.impl import ActionRowBuilder
from lightbulb import Context

from random import sample, randint


class Minesweeper:
    def __init__(self, ctx):
        self.ctx: Context = ctx
        self.messages: Message = []

        self.sol = None
        self.cur = ['\u200b']*100

    async def start(self):
        grid = []
        for i in range(5):
            component = ActionRowBuilder()
            for j in range(5):
                component.add_button(1, f'{i};{j}').set_label('\u200b').add_to_container()

            grid.append(component)

        actions = ActionRowBuilder()
        actions.add_button(2, 'mine').set_emoji('⛏️').add_to_container()
        actions.add_button(2, 'flag').set_emoji('🚩').add_to_container()

        self.messages.append(await self.ctx.respond('Partie de démineur', components=grid))
        self.messages.append(await self.ctx.respond('Actions', component=actions))
        await self.loop()

    async def loop(self):
        event = await self.ctx.bot.wait_for(InteractionCreateEvent, timeout=120, predicate=lambda e: e.interaction.member.id == self.ctx.member.id)
        await event.interaction.create_initial_response(4, 'OUI', flags=1 << 6)

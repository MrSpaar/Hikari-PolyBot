from hikari import Embed, Message, GuildReactionAddEvent, GuildMessageCreateEvent
from hikari.guilds import Member
from lightbulb import Context

from asyncio import TimeoutError
from chess import Board, Move
from chess.svg import board
from cairosvg import svg2png
from core.cls import Bot
from os import remove


class Chess:
    def __init__(self, ctx, opponent):
        self.bot: Bot = ctx.bot
        self.ctx: Context = ctx
        self.message: Message = None

        self.end = False
        self.board = Board()
        self.opponent: Member = opponent
        self.cur = [ctx.member, opponent]

    async def start(self) -> None:
        await self.send_message(init=True)
        await self.message.add_reaction('✅')
        await self.message.add_reaction('❌')

        try:
            event = await self.bot.wait_for(GuildReactionAddEvent, timeout=300,
                                            predicate=lambda e: (e.emoji_name == '✅' or e.emoji_name == '❌') and e.member == self.opponent)
        except:
            return await self.send_message(color=0xe74c3c, text="❌ L'adversaire n'a pas accepté la partie à temps")

        if str(event.emoji_name) == '❌':
            return await self.send_message(color=0xe74c3c, text="❌ L'adversaire à refusé la partie")

        await self.send_message(color=0xfffff)
        return await self.play()

    async def send_message(self, move: Move = None, color=0x00000, text: str = '', init: bool = False) -> None:
        if self.message:
            await self.message.delete()

        b = board(self.board, lastmove=move) if move else board(self.board)
        svg2png(bytestring=b, write_to='output.png')
        footer = '2 minutes par coups' + f' • Tour de {self.cur[1].display_name}' if not init else ''

        embed = (Embed(color=color, description=text)
                 .set_footer(text=footer)
                 .set_image('output.png')
                 .set_author(name=f'{self.opponent.username} contre {self.ctx.author.username}',
                             icon=self.opponent.avatar_url))

        self.message = await self.ctx.respond(embed=embed)
        remove('output.png')

    async def play(self) -> None:
        try:
            event = await self.bot.wait_for(GuildMessageCreateEvent, timeout=120, predicate=lambda m: m.author == self.cur[0])

            if event.message.content in ['ff', 'resign', 'abandon', 'abandonner', 'quit']:
                return await self.ctx.respond(f'{self.cur[0].mention} a abandonné la partie')

            try:
                m = self.board.parse_san(event.message.content)
                self.board.push(m)
            except:
                await self.turn()
            else:
                await event.message.delete()
                await self.send_message(m, 0xfffff)
        except TimeoutError:
            return await self.ctx.respond(f'Temps de réflexion écoulé, {self.cur[1].mention} a gagné')

        if self.board.is_checkmate():
            return await self.ctx.respond(f'{self.cur[0].mention} a gagné la partie !')
        elif self.board.is_game_over():
            return await self.ctx.respond('Égalité, personne ne gagne')
        else:
            self.cur[0], self.cur[1] = self.cur[1], self.cur[0]
            await self.play()

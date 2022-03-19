from hikari import Embed, User, Emoji
from lightbulb import EmojiConverter, Plugin, Context, SlashCommand, OptionModifier, command, option, implements

plugin = Plugin("Divers")


@plugin.command()
@option("texte", "Le texte au format Question | Option 1 | Option 2 | ...", modifier=OptionModifier.CONSUME_REST,)
@command("sondage", description="Faire un sondage (9 choix au maximum)")
@implements(SlashCommand)
async def sondage(ctx: Context):
    items = [arg.strip() for arg in ctx.options.texte.split("|")]
    question = items[0]
    reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

    embed = Embed(title=f">> {question[0].upper() + question[1:]}", color=0x3498DB)
    embed.set_author(name=f"Sondage de {ctx.member.display_name}", icon=ctx.author.avatar_url)

    for i in range(1, len(items)):
        embed.add_field(
            name=f"{reactions[i-1]} Option n°{i}",
            value=f"```{items[i]}```",
            inline=False,
        )

    resp = await ctx.respond(embed=embed)
    message = await resp.message()

    for i in range(len(items[1:])):
        await message.add_reaction(reactions[i])


@plugin.command()
@option("membre", "Le membre dont tu veux afficher l'image de profil", User, default=None)
@command("pp", "Afficher l'image de profil d'un membre")
@implements(SlashCommand)
async def pp(ctx: Context):
    member = ctx.options.membre or ctx.member
    embed = Embed(color=member.get_top_role().color).set_image(member.avatar_url)

    await ctx.respond(embed=embed)


@plugin.command()
@option("emoji", "L'emoji que tu veux afficher", Emoji)
@command("emoji", description="Afficher l'image d'origine d'un emoji")
@implements(SlashCommand)
async def emoji(ctx: Context):
    emoji = await EmojiConverter(ctx).convert(ctx.options.emoji)

    embed = (
        Embed(color=ctx.member.get_top_role().color)
        .set_image(emoji.url)
        .set_footer(text=f"<:{emoji.name}:{emoji.id}>")
    )

    await ctx.respond(embed=embed)


def load(bot):
    bot.add_plugin(plugin)
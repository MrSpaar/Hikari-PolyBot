from hikari import Permissions, InteractionCreateEvent, GuildMessageCreateEvent
from hikari.impl import ActionRowBuilder
from lightbulb import (
    RoleConverter,
    Plugin,
    Context,
    SlashCommand,
    OptionModifier,
    command,
    option,
    implements,
    guild_only,
    has_guild_permissions,
)

plugin = Plugin("Menus")
plugin.add_checks(guild_only | has_guild_permissions(Permissions.MANAGE_ROLES))


def build_menu(custom_id: str, labels: list[str], ids: list, emojis: list[str] = None, select: bool = False) -> ActionRowBuilder:
    component = ActionRowBuilder()

    if select:
        select = component.add_select_menu(custom_id)

        for label, id in zip(labels, ids):
            select.add_option(label, id).add_to_menu()

        select.add_to_container()
    else:
        if emojis:
            for i in range(len(labels)):
                component.add_button(3, ids[i]).set_emoji(emojis[i]).set_label(labels[i]).add_to_container()
        else:
            for i in range(len(labels)):
                component.add_button(3, ids[i]).set_label(labels[i]).add_to_container()

    return component


async def fetch_roles(ctx: Context, string: str):
    for char in "<@&>":
        string = string.replace(char, "")

    converter = RoleConverter(ctx)
    role_ids = string.split()

    for role_id in role_ids:
        yield await converter.convert(role_id)


@plugin.command()
@option("titre", "Le titre du menu de rôles", modifier=OptionModifier.CONSUME_REST)
@command("menu", "Créer un menu de rôles")
@implements(SlashCommand)
async def menu(ctx: Context):
    component = build_menu("setup", ('Boutons', 'Liste', 'Emojis'), ('button', 'select', 'emoji'), select=True)
    resp = await ctx.respond("Choisis le type de menu :", component=component)
    message = await resp.message()

    type_event = await plugin.bot.wait_for(InteractionCreateEvent, None, lambda e: e.interaction.member == ctx.member)
    await type_event.interaction.create_initial_response(7, "Entre les rôles du menu : ", components=[])

    roles_event = await plugin.bot.wait_for(GuildMessageCreateEvent, None, lambda m: m.author == ctx.user)
    await roles_event.message.delete()

    menu_type = type_event.interaction.values[0]
    labels, ids = zip(*[(role.name, role.id) async for role in fetch_roles(ctx, roles_event.message.content)])

    if menu_type == "emoji":
        await message.edit('Entre les emojis : ')
        emojis_event = await plugin.bot.wait_for(GuildMessageCreateEvent, None, lambda m: m.author == ctx.user)
        await emojis_event.message.delete()

        emojis = emojis_event.message.content.split()
        component = build_menu('menu', labels, ids, emojis)
    elif menu_type == 'select':
        component = build_menu('menu', labels, ids, select=True)
    else:
        component = build_menu('menu', labels, ids)

    await message.edit(f'Menu de rôles - {ctx.options.titre}', component=component)

@plugin.listener(InteractionCreateEvent)
async def on_button_click(event):
    interaction = event.interaction
    if interaction.type == 2 or "Menu de rôles" not in interaction.message.content:
        return

    guild = plugin.bot.cache.get_guild(interaction.guild_id)

    if interaction.component_type == 2:
        role = guild.get_role(interaction.custom_id)
        await interaction.member.add_role(role)

        return await interaction.create_initial_response(
            4, f"✅ Rôle {role.mention} ajouté", flags=1 << 6
        )

    role = guild.get_role(int(interaction.values[0]))
    member_roles = interaction.member.get_roles()
    menu_roles = [
        guild.get_role(int(option.value))
        for option in interaction.message.components[0].components[0].options
    ]

    if any([role in member_roles for role in menu_roles]):
        return await interaction.create_initial_response(
            4, f"❌ Tu as déjà un des rôles", flags=1 << 6
        )

    await interaction.member.add_role(role)
    await interaction.create_initial_response(
        4, f"✅ Rôle {role.mention} ajouté", flags=1 << 6
    )


def load(bot):
    bot.add_plugin(plugin)

from hikari import Role, Permissions, InteractionCreateEvent, ComponentInteraction
from hikari.impl import ActionRowBuilder
from lightbulb import Plugin, Context, SlashCommand, OptionModifier, command, option, implements, guild_only, has_guild_permissions

from typing import Union

plugin = Plugin('Menus')
plugin.add_checks(guild_only | has_guild_permissions(Permissions.MANAGE_ROLES))


@plugin.command()
@option('roles', 'Les rôles du menu', Role, modifier=OptionModifier.GREEDY)
@option('titre', 'Le titre du menu de rôles (ex. /boutons @role1 @role2 Incroyable menu)', modifier=OptionModifier.CONSUME_REST)
@command('boutons', 'Créer un menu de rôles avec des boutons')
@implements(SlashCommand)
async def boutons(ctx: Context):
    components = []

    for i in range(0, len(ctx.options.roles), 5):
        component = ActionRowBuilder()
        for role in roles[i:i+5]:
            component.add_button(3, role.id).set_label(role.name).add_to_container()

        components += [component]
    await ctx.respond(f'Menu de rôles - {ctx.options.titre}', components=components)


@plugin.command()
@option('paires', 'Les paires emoji/role du menu', Union[Role, str], modifier=OptionModifier.GREEDY)
@command('emojis', 'Faire un menu de rôles avec des boutons incluant des emojis (ex. /emoji 🥫 @role1 🎮 @role2')
@implements(SlashCommand)
async def emojis(ctx: Context):
    components = []

    for i in range(0, len(ctx.options.paires), 10):
        component = ActionRowBuilder()
        for emoji, role in zip(ctx.options.paires[i:i+10:2], ctx.options.paires[i+1:i+10:2]):
            component.add_button(3, role.id).set_label(role.name).set_emoji(emoji).add_to_container()

        components += [component]
    await ctx.respond(f'Menu de rôles', components=components)


@plugin.command()
@option('roles', 'Les rôles du menu', Role, modifier=OptionModifier.GREEDY)
@option('titre', 'Le titre du menu', modifier=OptionModifier.CONSUME_REST)
@command('liste', 'Faire un menu de rôles avec une liste déroulante')
@implements(SlashCommand)
async def liste(ctx: Context):
    component = ActionRowBuilder()
    select = component.add_select_menu('menu')

    for role in ctx.options.roles:
        select.add_option(role.name, role.id).add_to_menu()

    select.set_placeholder(ctx.options.titre)
    select.add_to_container()
    await ctx.respond('Menu de rôles', component=component)


@plugin.listener(InteractionCreateEvent)
async def on_button_click(event):
    interaction: ComponentInteraction = event.interaction
    if interaction.type == 2 or 'Menu de rôles' not in interaction.message.content:
        return

    guild = plugin.bot.cache.get_guild(interaction.guild_id)

    if interaction.component_type == 2:
        role = guild.get_role(interaction.custom_id)
        await interaction.member.add_role(role)
        return await interaction.create_initial_response(4, f'✅ Rôle {role.mention} ajouté', flags=1 << 6)

    role = guild.get_role(int(interaction.values[0]))
    member_roles = interaction.member.get_roles()
    menu_roles = [guild.get_role(int(option.value)) for option in interaction.message.components[0].components[0].options]

    if any([role in member_roles for role in menu_roles]):
        return await interaction.create_initial_response(4, f'❌ Tu as déjà un des rôles', flags=1 << 6)

    await interaction.member.add_role(role)
    await interaction.create_initial_response(4, f'✅ Rôle {role.mention} ajouté', flags=1 << 6)


def load(bot):
    bot.add_plugin(plugin)

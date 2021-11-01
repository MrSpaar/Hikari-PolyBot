from hikari import Role, Embed, Permissions, ComponentInteraction
from hikari.events import InteractionCreateEvent
from hikari.impl import ActionRowBuilder
from lightbulb import Plugin, Context, Greedy, listener, check, guild_only, has_guild_permissions

from typing import Union
from core.funcs import group
from core.cls import Bot


class Menus(Plugin):
    def __init__(self, bot, name=None):
        super().__init__(name=name)
        self.bot: Bot = bot

    @check(guild_only)
    @check(has_guild_permissions(Permissions.MANAGE_ROLES))
    @group(brief='boutons @CM 1 @CM 2 Groupes de CM', usage='<sous commande> <sous arguments>',
           description='Commandes liées aux menus de rôles')
    async def menu(self, ctx: Context):
        if ctx.invoked_with not in ['boutons', 'liste', 'emoji']:
            embed = Embed(color=0xe74c3c, description='❌ Sous commande inconnue : `boutons` `liste` `emoji`')
            return await ctx.respond(embed=embed)

        await ctx.message.delete()

    @check(guild_only)
    @check(has_guild_permissions(Permissions.MANAGE_ROLES))
    @menu.command(brief='@CM 1 @CM 2 Groupes de CM', usage='<rôles> <titre>',
                  description='Faire un menu de rôles avec des boutons')
    async def boutons(self, ctx: Context, roles: Greedy[Role], *, title: str):
        components = []
        for i in range(0, len(roles), 5):
            component = ActionRowBuilder()
            for role in roles[i:i+5]:
                component.add_button(3, role.id).set_label(role.name).add_to_container()

            components += [component]
        await ctx.respond(f'Menu de rôles - {title}', components=components)

    @check(guild_only)
    @check(has_guild_permissions(Permissions.MANAGE_ROLES))
    @menu.command(brief='🥫 @Kouizinier 🎮 @Soirées jeux', usage='<emojis et rôles> <titre>',
                  description='Faire un menu de rôles avec des boutons incluant des emojis')
    async def emojis(self, ctx: Context, entries: Greedy[Union[Role, str]]):
        components = []
        for i in range(0, len(entries), 10):
            component = ActionRowBuilder()
            for emoji, role in zip(entries[i:i+10:2], entries[i+1:i+10:2]):
                component.add_button(3, role.id).set_label(role.name).set_emoji(emoji).add_to_container()

            components += [component]
        await ctx.respond(f'Menu de rôles', components=components)

    @check(guild_only)
    @check(has_guild_permissions(Permissions.MANAGE_ROLES))
    @menu.command(brief='@CM 1 @CM 2 Choisis ton CM', usage='<rôles> <titre>',
                  description='Faire un menu de rôles avec une liste déroulante')
    async def liste(self, ctx: Context, roles: Greedy[Role], *, title: str):
        component = ActionRowBuilder()
        select = component.add_select_menu('menu')
        for role in roles:
            select.add_option(role.name, role.id).add_to_menu()

        select.add_to_container()
        await ctx.respond('Menu de rôles', component=component)

    @listener(InteractionCreateEvent)
    async def on_button_click(self, event):
        interaction: ComponentInteraction = event.interaction
        if interaction.type == 2 or 'Menu de rôles' not in interaction.message.content:
            return

        guild = self.bot.cache.get_guild(interaction.guild_id)

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
    bot.add_plugin(Menus(bot))

def unload(bot):
    bot.remove_plugin('Menus')

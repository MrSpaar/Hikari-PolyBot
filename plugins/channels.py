from hikari import Embed, Role, Member, PermissionOverwrite, Permissions
from hikari.events.voice_events import VoiceStateUpdateEvent
from lightbulb import Plugin, Context, Greedy, listener, check, guild_only

from core.cls import Bot
from core.funcs import group, vc_check
from typing import Union


class Vocaux(Plugin):
    def __init__(self, bot, name=None):
        super().__init__(name=name)
        self.bot: Bot = bot

    @check(guild_only)
    @group(brief='owner @Alexandre Humber', usage='<sous commande> <sous arguments>',
           description='Commandes liées aux channels temporaires')
    async def voc(self, ctx: Context):
        if ctx.invoked_with.lower() not in ['rename', 'owner', 'private']:
            embed = Embed(color=0xe74c3c, description='❌ Sous commande inconnue : `rename` `owner` `private`')
            await ctx.respond(embed=embed)

    @check(vc_check)
    @check(guild_only)
    @voc.command(brief='Mdrr', usage='<nouveau nom>', insensitive_commands=True,
                 description='Modifier le nom de son channel')
    async def rename(self, ctx: Context, *, name: str):
        guild = ctx.get_guild()
        channel = guild.get_channel(guild.get_voice_state(ctx.member).channel_id)
        entry = await self.bot.db.pending.find({'guild_id': guild.id, 'voc_id': channel.id})

        channel = guild.get_channel(entry['voc_id'])
        await channel.edit(name=name)

        embed = Embed(color=0x2ecc71, description='✅ Nom modifié')
        await ctx.respond(embed=embed)

    @check(vc_check)
    @check(guild_only)
    @voc.command(brief='@Noah Haenel', usage='<membre>',
                 description='Définir le propriétaire du channel')
    async def owner(self, ctx: Context, member: Member):
        guild = ctx.get_guild()
        channel = guild.get_channel(guild.get_voice_state(ctx.member).channel_id)

        entry = await self.bot.db.pending.find({'guild_id': guild.id, 'voc_id': channel.id})
        await self.bot.db.pending.update(entry, {'$set': {'owner': member.id}})

        embed = Embed(color=0x2ecc71, description='✅ Owner modifié')
        await ctx.respond(embed=embed)

    @check(vc_check)
    @check(guild_only)
    @voc.command(brief='@1A @2A', usage='<membres et/ou rôles>',
                 description='Rendre le channel privé')
    async def private(self, ctx: Context, entries: Greedy[Union[Role, Member]] = None):
        guild = ctx.get_guild()
        channel = guild.get_channel(guild.get_voice_state(ctx.member).channel_id)

        entry = await self.bot.db.pending.find({'guild_id': guild.id, 'voc_id': channel.id})

        guild = ctx.get_guild()
        channel, text = guild.get_channel(entry['voc_id']), guild.get_channel(entry['txt_id'])

        if entries:
            overwrites = [PermissionOverwrite(type=0, id=entry.id, allow=Permissions.VIEW_CHANNEL) for entry in entries] + \
                         [PermissionOverwrite(type=0, id=guild.id, deny=Permissions.VIEW_CHANNEL)]
        elif not entries and (parent := guild.get_channel(channel.parent_id)):
            overwrites = parent.permission_overwrites.values()
        elif not entries:
            overwrites = PermissionOverwrite(type=0, id=guild.id, allow=Permissions.VIEW_CHANNEL)

        await text.edit(permission_overwrites=overwrites)
        await channel.edit(permission_overwrites=overwrites)

        embed = Embed(color=0x2ecc71, description='✅ Permissions modifiées')
        await ctx.respond(embed=embed)

    @listener(VoiceStateUpdateEvent)
    async def voice_update(self, event: VoiceStateUpdateEvent):
        guild = self.bot.cache.get_guild(event.guild_id)

        if event.state and event.state.channel_id:
            after, member = guild.get_channel(event.state.channel_id), event.state.member
            entry = await self.bot.db.pending.find({'guild_id': guild.id, 'owner': member.id})

            if 'Créer' in after.name and not member.is_bot and not entry:
                category = guild.get_channel(after.parent_id)
                overwrites = category.permission_overwrites.values() if category else after.permission_overwrites.values()

                text = await guild.create_text_channel(name=f'Salon-de-{member.display_name}', category=category, 
                                                       permission_overwrites=overwrites)
                channel = await guild.create_voice_channel(name=f'Salon de {member.display_name}', category=category,
                                                           permission_overwrites=overwrites)

                try:
                    await member.edit(voice_channel=channel)
                    await self.bot.db.pending.insert({'guild_id': guild.id, 'owner': member.id, 'voc_id': channel.id, 'txt_id': text.id})
                except:
                    await channel.delete()
                    await text.delete()

        if event.old_state and event.old_state.channel_id:
            before = guild.get_channel(event.old_state.channel_id)
            entry = await self.bot.db.pending.find({'guild_id': guild.id, 'voc_id': before.id})

            voice_states = filter(lambda vs: guild.get_channel(vs.channel_id)==before, guild.get_voice_states().values())
            count = len([vs.member for vs in voice_states])

            if entry and not count:
                text = guild.get_channel(entry['txt_id'])

                await text.delete()
                await before.delete()
                await self.bot.db.pending.delete(entry)


def load(bot):
    bot.add_plugin(Vocaux(bot))

def unload(bot):
    bot.remove_plugin('Vocaux')

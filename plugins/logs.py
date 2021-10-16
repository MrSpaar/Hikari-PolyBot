from hikari import Embed, GatewayGuild, AuditLogEventType, events
from hikari.events.channel_events import InviteCreateEvent
from lightbulb import Plugin, listener

from core.cls import Bot
from core.funcs import now
from time import mktime


class Logs(Plugin):
    def __init__(self, bot, name=None):
        super().__init__(name=name)
        self.bot: Bot = bot

    async def get_audit_log(self, guild, event):
        entries = await self.bot.rest.fetch_audit_log(guild, event_type=event)
        log_id = list(entries[0].entries.keys())[0]
        return entries[0].entries[log_id]

    async def send_log(self, guild: GatewayGuild, embed: Embed):
        settings = await self.bot.db.setup.find({'_id': guild.id})

        if settings['logs'] and (channel := guild.get_channel(settings['logs'])):
            await channel.send(embed=embed)        

        return settings

    @listener(events.MemberCreateEvent)
    async def on_member_join(self, event):
        guild, member = self.bot.cache.get_guild(event.guild_id), event.member

        embed = Embed(color=0x2ecc71, description=f':inbox_tray: {member.mention} a rejoint le serveur !')
        settings = await self.send_log(guild, embed)

        if settings['welcome']:
            channel = guild.get_channel(settings['welcome']['id'])
            await channel.send(settings['welcome']['txt'])

        if settings['new']:
            role = guild.get_role(settings['new'])
            await member.add_roles(role)

    @listener(events.MemberDeleteEvent)
    async def on_member_remove(self, event):
        guild, member = self.bot.cache.get_guild(event.guild_id), event.old_member

        embed = Embed(color=0xe74c3c, description=f':outbox_tray: {member.display_name} ({member}) a quitté le serveur')
        await self.send_log(guild, embed)

    @listener(events.BanDeleteEvent)
    async def on_member_unban(self, event):
        guild, target = self.bot.cache.get_guild(event.guild_id), event.user

        entry = await self.get_audit_log(guild, AuditLogEventType.MEMBER_BAN_REMOVE)
        reason, user = entry.reason, guild.get_member(entry.user_id)

        embed = Embed(color=0xc27c0e, description=f"👨‍⚖️ {user.mention} a unban {target}\n❔ Raison : {reason or 'Pas de raison'}")
        await self.send_log(guild, embed)

    @listener(events.MemberUpdateEvent)
    async def on_member_update(self, event):
        guild = self.bot.cache.get_guild(event.guild_id)
        before, after = event.old_member, event.member
        embed = Embed(color=0x3498db)

        entry = await self.get_audit_log(guild, AuditLogEventType.MEMBER_UPDATE)
        member = guild.get_member(entry.user_id)

        if before.display_name != after.display_name:
            if after == member:
                embed.description = f"📝 {member.mention} a changé son surnom (`{before.display_name}` → `{after.display_name}`)"
            else:
                embed.description = f"📝 {member.mention} a changé de surnom de {before.mention} (`{before.display_name}` → `{after.display_name}`)"
        elif (broles := before.get_roles()) != (aroles := after.get_roles()):
            new = list(filter(lambda r: r not in broles, aroles))
            removed = list(filter(lambda r: r not in aroles, broles))
            role, = new if new else removed

            if after == member:
                embed.description = f"📝 {member.mention} s'est {'ajouté' if new else 'retiré'} {role.mention}"
            else:
                embed.description = f"📝 {member.mention} à {'ajouté' if new else 'retiré'} {role.mention} à {before.mention}"
        else:
            return

        await self.send_log(guild, embed)

    # events.GuildMessageDeleteEvent.old_message will be added in the next hikari release
    # and messages are removed from the cache when they're deleted
    # so the bot can't log deleted messages yet

    # @listener(events.GuildMessageDeleteEvent)
    # async def on_message_delete(self, event):
    #     guild = event.get_guild()
    #     if not guild:
    #         return

    #     channel = event.get_channel()
    #     message = event.old_message

    #     if message.author.is_bot or 'test' in channel.name or len(message.content) == 1 or \
    #        (len(message.content) in [5, 6, 7] and message.content.count(',') == 2):
    #         return

    #     flags = [
    #         (now(utc=True)-message.timestamp).total_seconds() <= 20 and message.mentions and message.content,
    #         message.content and not message.attachments,
    #         message.content or message.attachments
    #     ]

    #     infos = [
    #         {'emoji': '<:ping:768097026402942976>', 'color': 0xe74c3c},
    #         {'emoji': '🗑️', 'color': 0x979c9f},
    #         {'emoji': '🗑️', 'color': 0xf1c40f}
    #     ]

    #     entry = [infos[i] for i, flag in enumerate(flags) if flag][0]

    #     embed = Embed(color=entry['color'], description=f'{entry["emoji"]} Message de {message.author.mention} supprimé dans {channel.mention}:')

    #     if message.content:
    #         embed.description += f'\n\n> {message.content}'
    #     if message.attachments:
    #         embed.set_image(url=message.attachments[0].url)

    #     await self.send_log(message.guild, embed)

    @listener(InviteCreateEvent)
    async def on_invite_create(self, event):
        invite, guild = event.invite, self.bot.cache.get_guild(event.guild_id)

        url = f'https://discord.gg/{invite.code}'
        uses = f'{invite.max_uses} fois' if invite.max_uses else "à l'infini"
        expire = f'<t:{int(mktime((now() + invite.max_age).timetuple()))}:R>' if invite.max_age else 'jamais'

        embed = Embed(color=0x3498db, description=f'✉️ {invite.inviter.mention} a créé une [invitation]({url}) qui expire {expire}, utilisable {uses}')
        await self.send_log(guild, embed)


def load(bot):
    bot.add_plugin(Logs(bot))

def unload(bot):
    bot.remove_plugin('Logs')

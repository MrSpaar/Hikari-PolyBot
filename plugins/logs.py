from hikari import Embed, GatewayGuild, AuditLogEventType, events
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
            await channel.send(settings['welcome']['txt'].replace('<mention>', member.mention))

        if settings['new']:
            role = guild.get_role(settings['new'])
            await member.add_role(role)

    @listener(events.MemberDeleteEvent)
    async def on_member_remove(self, event):
        if not event.old_member:
            return

        guild, member = self.bot.cache.get_guild(event.guild_id), event.old_member
        name = f'{member.display_name} ({member})' if member.display_name else str(member)

        embed = Embed(color=0xe74c3c, description=f':outbox_tray: {name} a quitté le serveur')
        await self.send_log(guild, embed)

    @listener(events.BanCreateEvent)
    async def on_member_ban(self, event: events.BanCreateEvent):
        guild, target = self.bot.cache.get_guild(event.guild_id), event.user

        try: entry = await self.get_audit_log(guild, AuditLogEventType.MEMBER_BAN_ADD)
        except: return

        reason, user = entry.reason, guild.get_member(entry.user_id)

        embed = Embed(color=0xe74c3c, description=f"👨‍⚖️ {user.mention} a ban {target.mention}\n❔ Raison : {reason or 'Pas de raison'}")
        await self.send_log(guild, embed)

    @listener(events.BanDeleteEvent)
    async def on_member_unban(self, event):
        guild, target = self.bot.cache.get_guild(event.guild_id), event.user

        try: entry = await self.get_audit_log(guild, AuditLogEventType.MEMBER_BAN_REMOVE)
        except : return

        reason, user = entry.reason, guild.get_member(entry.user_id)

        embed = Embed(color=0xc27c0e, description=f"👨‍⚖️ {user.mention} a unban {target.mention}\n❔ Raison : {reason or 'Pas de raison'}")
        await self.send_log(guild, embed)

    @listener(events.MemberUpdateEvent)
    async def on_member_update(self, event):
        guild = self.bot.cache.get_guild(event.guild_id)
        before, after = event.old_member, event.member

        if not before or not after:
            return

        embed = Embed(color=0x3498db)

        if before.display_name != after.display_name:
            try: entry = await self.get_audit_log(guild, AuditLogEventType.MEMBER_UPDATE)
            except: return

            member = guild.get_member(entry.user_id)

            if after == member:
                embed.description = f"📝 {member.mention} a changé son surnom (`{before.display_name}` → `{after.display_name}`)"
            else:
                embed.description = f"📝 {member.mention} a changé de surnom de {before.mention} (`{before.display_name}` → `{after.display_name}`)"
        elif (broles := before.get_roles()) != (aroles := after.get_roles()):
            try: entry = await self.get_audit_log(guild, AuditLogEventType.MEMBER_ROLE_UPDATE)
            except: return

            member = guild.get_member(entry.user_id)

            role, = set(broles).symmetric_difference(set(aroles))

            if after == member:
                embed.description = f"📝 {member.mention} s'est {'ajouté' if role in aroles else 'retiré'} {role.mention}"
            else:
                embed.description = f"📝 {member.mention} à {'ajouté' if role in aroles else 'retiré'} {role.mention} à {before.mention}"
        else:
            return

        await self.send_log(guild, embed)

    @listener(events.GuildMessageDeleteEvent)
    async def on_message_delete(self, event):
        guild = event.get_guild()
        if not guild:
            return

        channel = event.get_channel()
        message = event.old_message

        if message.author.is_bot or 'test' in channel.name or (message.content and len(message.content) == 1):
            return

        date = message.timestamp.replace(tzinfo=None)
        mentions = tuple(message.mentions.users.keys()) + message.mentions.role_ids

        flags = [
            (now(utc=True)-date).total_seconds() <= 20 and mentions and message.content,
            message.content and not message.attachments,
            message.content or message.attachments
        ]

        infos = [
            {'emoji': '<:ping:768097026402942976>', 'color': 0xe74c3c},
            {'emoji': '🗑️', 'color': 0x979c9f},
            {'emoji': '🗑️', 'color': 0xf1c40f}
        ]

        entry = [infos[i] for i, flag in enumerate(flags) if flag][0]

        embed = Embed(color=entry['color'], description=f'{entry["emoji"]} Message de {message.author.mention} supprimé dans {channel.mention}:')

        if message.content:
            embed.description += f'\n\n> {message.content}'
        if message.attachments:
            embed.set_image(message.attachments[0].url)

        await self.send_log(guild, embed)

    @listener(events.InviteCreateEvent)
    async def on_invite_create(self, event):
        invite, guild = event.invite, self.bot.cache.get_guild(event.guild_id)

        if not invite.inviter:
            return

        url = f'https://discord.gg/{invite.code}'
        uses = f'{invite.max_uses} fois' if invite.max_uses else "à l'infini"
        expire = f'<t:{int(mktime((now() + invite.max_age).timetuple()))}:R>' if invite.max_age else 'jamais'

        embed = Embed(color=0x3498db, description=f'✉️ {invite.inviter.mention} a créé une [invitation]({url}) qui expire {expire}, utilisable {uses}')
        await self.send_log(guild, embed)


def load(bot):
    bot.add_plugin(Logs(bot))

def unload(bot):
    bot.remove_plugin('Logs')

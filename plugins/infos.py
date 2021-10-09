from hikari import Embed, Member, Role, GuildTextChannel, GuildVoiceChannel, Permissions
from lightbulb import Plugin, Context, check, guild_only

from core.funcs import command
from time import mktime


class Informations(Plugin):
    @check(guild_only)
    @command(description='Afficher des informations à propos du serveur')
    async def serverinfo(self, ctx: Context):
        guild = ctx.get_guild()

        channels = guild.get_channels().values()
        text = len([channel for channel in channels if isinstance(channel, GuildTextChannel)])
        voice = len([channel for channel in channels if isinstance(channel, GuildVoiceChannel)])
        emojis = [emoji.mention for emoji in guild.get_emojis().values()]

        creation = int(mktime(guild.created_at.timetuple()))
        owner = guild.get_member(guild.owner_id)

        members = guild.get_members().values()
        bots = [member for member in members if member.is_bot]

        description = (guild.description+'\n\n' if guild.description else '') + \
                      f'🙍 {guild.member_count} membres dont {len(bots)} bots\n' + \
                      f'📈 Nitro niveau {guild.premium_tier.value} avec {guild.premium_subscription_count} boosts\n' + \
                      f'📝 {len(guild.get_roles())} roles et {len(channels)} salons ({text} textuels et {voice} vocaux)\n' + \
                      f'🔐 Géré par {owner.mention} et créé le <t:{creation}:D>\n' + \
                      f"\nEmotes du serveur : {''.join(emojis)}" if emojis else ''

        embed = (Embed(description=description, color=0x546e7a)
                 .set_author(name=f'{guild.name} - {guild.id}', icon=guild.icon_url))

        await ctx.respond(embed=embed)

    @check(guild_only)
    @command(brief='@Julien Pistre', usage='<membre>',
             description="Afficher des informations à propos du serveur d'un membre")
    async def userinfo(self, ctx: Context, member: Member = None):
        member = member or ctx.member

        activities = {0: 'En train de jouer à `{0.name}`',
                      1: 'Est en train de [stream]({0.url})',
                      2: "En train d'écouter `{0.details}` de `{0.state}`"}

        status = {'online': 'En ligne',
                  'offline': 'Hors ligne',
                  'invisible': 'Invisible',
                  'idle': 'Absent',
                  'dnd': 'Ne pas déranger'}

        presence = member.get_presence()
        status = status[presence.visible_status]
        flags = [flag.name.replace('_', ' ').title() for flag in member.flags]
        activities = [activities[activity.type].format(activity) for activity in presence.activities if activity.type in activities]

        since = int(mktime(member.joined_at.timetuple()))
        creation = int(mktime(member.created_at.timetuple()))
        boost = int(mktime(member.premium_since.timetuple())) if member.premium_since else None

        description = f'⏱️ A rejoint <t:{since}:R>\n' + \
                      f'📝 A créé son compte <t:{creation}:R>\n' + \
                      f'💳 Surnom : `{member.display_name}`\n' + \
                      f'🏷️ Rôle principal : {member.get_top_role().mention}\n' + \
                      (f"🚩 Flags : {', '.join(flags)}\n" if flags else '') + \
                      (f'📈 A commencé à booster le serveur <t:{boost}:R>\n\n' if boost else '') + \
                      ('🏃‍♂️ Activités :\n- ' + '\n- '.join(activities) if activities else '')

        embed = (Embed(color=0x1abc9c, description=description)
                 .set_author(name=f'{member} - {status}', icon=member.avatar_url))

        await ctx.respond(embed=embed)

    @check(guild_only)
    @command(brief='@Modo', usage='<role>',
             description="Afficher des informations à propos du serveur d'un rôle")
    async def roleinfo(self, ctx: Context, role: Role):
        since = int(mktime(role.created_at.timetuple()))
        guild = ctx.get_guild()

        perms = {
            Permissions.ADMINISTRATOR: 'Administrateur',
            Permissions.MANAGE_GUILD: 'Gérer le serveur',
            Permissions.MANAGE_CHANNELS: 'Gérer les salons',
            Permissions.MANAGE_NICKNAMES: 'Gérer les pseudos',
            Permissions.MANAGE_THREADS: 'Gérer les fils',
            Permissions.MANAGE_WEBHOOKS: 'Gérer les webhooks',
            Permissions.MANAGE_MESSAGES: 'Gérer les messages',
            Permissions.MANAGE_EMOJIS_AND_STICKERS: 'Gérer les emojis et stickers',
            Permissions.MANAGE_ROLES: 'Gérer les rôles',
            Permissions.VIEW_AUDIT_LOG: 'Voir les logs',
            Permissions.VIEW_GUILD_INSIGHTS: 'Voir les analyses du serveur',
            Permissions.USE_VOICE_ACTIVITY: 'Voir les activités de voix',
            Permissions.VIEW_CHANNEL: 'Voir les salons',
            Permissions.BAN_MEMBERS: 'Bannier des membres',
            Permissions.KICK_MEMBERS: 'Expulser des membres',
            Permissions.MUTE_MEMBERS: 'Muter des membres',
            Permissions.MOVE_MEMBERS: 'Bouger des membres',
            Permissions.DEAFEN_MEMBERS: 'Rendre des membres sourds',
            Permissions.ADD_REACTIONS: 'Ajouter des réactions',
            Permissions.CHANGE_NICKNAME: 'Changer de pseudo',
            Permissions.CREATE_INSTANT_INVITE: 'Créer des invitations',
            Permissions.MENTION_ROLES: 'Mentionner everyone et les rôles',
            Permissions.ATTACH_FILES: 'Envoyer des fichiers',
            Permissions.SEND_TTS_MESSAGES: 'Envoyer des TTS',
            Permissions.EMBED_LINKS: 'Envoyer des intégrations',
            Permissions.SEND_MESSAGES: 'Envoyer des messages',
            Permissions.READ_MESSAGE_HISTORY: "Lire les historiques de messages",
            Permissions.USE_APPLICATION_COMMANDS: 'Utiliser les applications',
            Permissions.USE_EXTERNAL_EMOJIS: 'Utiliser les emojis externes',
            Permissions.USE_EXTERNAL_STICKERS: 'Utiliser les stickers externes',
            Permissions.USE_PRIVATE_THREADS: 'Utiliser les fils privés',
            Permissions.USE_PUBLIC_THREADS: 'Utiliser les fils publiques',
            Permissions.PRIORITY_SPEAKER: 'Parler en prioritaire',
            Permissions.REQUEST_TO_SPEAK: 'Demander la parole',
            Permissions.SPEAK: 'Parler en vocal',
            Permissions.STREAM: 'Faire un stream',
            Permissions.CONNECT: 'Se connecter à un vocal'
        }

        description = f'⏱️ Créé <t:{since}:R>\n' + \
                      f'🌈 Couleur : `{role.color.hex_code}`\n' + \
                      f"🔔 {'Mentionnable' if role.is_mentionable else 'Non mentionnable'}{' et affiché séparemment' if role.is_hoisted else ''}\n\n" + \
                      f'⛔ Permissions : \n- ' + '\n- '.join([perms[perm] for perm in role.permissions])

        embed = (Embed(color=role.color, description=description)
                 .set_author(name=f'{role.name} - {role.id}', icon=guild.icon_url))
        
        await ctx.respond(embed=embed)


def load(bot):
    bot.add_plugin(Informations())

def unload(bot):
    bot.remove_plugin('Informations')
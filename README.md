# Commandes

PolyBot est **un bot discord multi-fonction**. Pour l'instant, il est **semi-privé mais open-source** !<br>
⚠️ Chaque lien mène vers le code source ou le dossier lui correspondant.<br>


### • 🧍 Commandes utilisateur

|                                            Categorie                                            |                         Commandes                       |
|-------------------------------------------------------------------------------------------------|---------------------------------------------------------|
|[Fun](https://github.com/MrSpaar/Hikari-PolyBot/blob/master/plugins/fun.py)                      | `chess` `hangman` `minesweeper` `toss` `roll` `reaction`|
|[Musique](https://github.com/MrSpaar/Hikari-PolyBot/blob/master/plugins/music.py)                | `play` `stop` `skip` `pause` `resume`                   |
|[Recherche](https://github.com/MrSpaar/Hikari-PolyBot/blob/master/plugins/search.py)             | `twitch` `youtube` `wikipedia` `anime` `weather`        |
|[Divers](https://github.com/MrSpaar/Hikari-PolyBot/blob/master/plugins/misc.py)                  | `help` `poll` `pfp` `emoji` `repo` `code`               |
|[Maths](https://github.com/MrSpaar/Hikari-PolyBot/blob/master/plugins/maths.py)                  | `base` `binary` `hexadecimal` `calcul`                  |
|[Niveaux](https://github.com/MrSpaar/Hikari-PolyBot/blob/master/plugins/levels.py)               | `rank` `levels`                                         |
|[Channels Temporaires](https://github.com/MrSpaar/Hikari-PolyBot/blob/master/plugins/channels.py)| `voc rename` `voc private` `voc owner`                  |

### • 🔒 Commandes admin

|                                        Categorie                                        |                                  Commandes                                |
|-----------------------------------------------------------------------------------------|---------------------------------------------------------------------------|
|[Modération](https://github.com/MrSpaar/Hikari-PolyBot/blob/master/plugins/moderation.py)| `mute` `unmute` `clear` `kick` `ban` `unban`                              |
|[Infos](https://github.com/MrSpaar/Hikari-PolyBot/blob/master/plugins/informations.py)   | `serverinfo` `userinfo` `roleinfo`                                        |
|[Menus](https://github.com/MrSpaar/Hikari-PolyBot/blob/master/plugins/utility.py)        | `menu boutons` `menu liste` `menu emojis`                                 |
|[Setup](https://github.com/MrSpaar/Hikari-PolyBot/blob/master/plugins/setup.py)          | `set` `settings`                                                          |

# Modules supplémentaires

### • 📈 [Système d'expérience](https://github.com/MrSpaar/Hikari-PolyBot/blob/master/plugins/levels.py)

Le système a la **même courbe d'xp que [Mee6](https://mee6.xyz/)**. <br>
Ecrivez `!set channel <#channel>` pour définir le salon où le bot fait ses annonces de level up.<br>
`!rank` vous montrera votre niveau, expérience et position dans le classement du serveur.<br>
`!levels` vous montrera le classement du serveur par page de 10.

### • ⏲️ [Channels temporaires](https://github.com/MrSpaar/Hikari-PolyBot/blob/master/plugins/channels.py)

Ce module permet d'avoir des channels vocaux temporaires :

- Chaque channel contenant [ce prefix](https://github.com/MrSpaar/Hikari-PolyBot/blob/master/plugins/channels.py#L18) génèrera un channel tempaire dès que quelqu'un le rejoindra.
- Un channel écrit est généré et lié avec le channel temporaire.
- Les deux sont supprimés dès que le channel vocal est vide.

### • 📝 [Logs](https://github.com/MrSpaar/Hikari-PolyBot/blob/master/plugins/logs.py)

Ecrivez `!set logs <#channel>` pour définir le channel contenant les logs.

|           Log            |                Informations affichées                  |
|--------------------------|--------------------------------------------------------|
|Nouveau membre            | Mention                                                |
|Départ d'un membre        | Pseudo, ID et raison (ban, kick, ...)                  |
|Membre unban              | Pseudo, par qui et raison                              |
|Changement de surnom      | Ancien et nouveau surnom et par qui                    |
|Ajout/Suppression de rôles| Rôle ajouté ou enlevé, de qui et par qui               |
|Création d'invitation     | Lien, autheur, date d'expiration, nombre d'utilisations|

### • ❌ [Gestion d'erreurs](https://github.com/MrSpaar/PolyBot/blob/master/modules/errors.py)

Ce module permet d'afficher des messages d'erreurs. A chaque erreur, un message suivi d'un exemple est envoyé.<br>
S'il s'agit d'une commande inconnue, la commande la plus proche apparait également dans le message d'erreur.

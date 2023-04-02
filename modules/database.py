from modules.commons import *
from modules.const import *
from modules.myanimelist import *

def checkIfRegistered(discordId: int) -> bool:
    """Check if user is registered on Database"""
    with open(database, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if row[0] == discordId:
                return True
        return False


def saveToDatabase(discordId: int, discordUsername: str, discordJoined: int, malUsername: str, malId: int,
                   malJoined: int, registeredAt: int, registeredGuild: int, registeredBy: int, guildName: str):
    """Save information regarding to user with their consent"""
    with open(database, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow([discordId, discordUsername, discordJoined, malUsername,
                        malId, malJoined, registeredAt, registeredGuild, registeredBy, guildName])


def dropUser(discordId: int) -> bool:
    """Drop a user from the database"""
    df = pd.read_csv(database, sep="\t")
    df_drop = df.drop(df.query(f'discordId == {discordId}').index)
    df_drop.to_csv(database, sep="\t", index=False, encoding="utf-8")


async def verifyUser(discordId: int) -> bool:
    """Verify a user on the database"""
    with open(database, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if row[0] == discordId:
                username = row[3]
                break
        else:
            raise Exception(f"{EMOJI_UNEXPECTED_ERROR} User maybe not registered to the bot, or there's unknown error")

        clubs = await checkClubMembership(username)
        verified: bool = False
        for club in clubs:
            if int(club['mal_id']) == int(CLUB_ID):
                verified = True
                break
        else:
            raise Exception(f"{EMOJI_UNEXPECTED_ERROR} User is not a member of the club")

    return verified

async def registerUser(
    whois: str, # discord uname#1234
    discordId: int,
    server: interactions.CommandContext.guild,
    malUsername: str,
    actor: interactions.CommandContext.author = None,
) -> str:
    """Register a user to the database"""
    if checkIfRegistered(discordId):
        if actor is not None:
            return f"{EMOJI_DOUBTING} User is already registered to the bot"
        else:
            m1 = f"{EMOJI_DOUBTING} You are already registered to the bot"
            if str(server.id) == str(VERIFICATION_SERVER):
                m2 = f"\nTo get your role back, please use the command `/verify` if you have joined [our club](<https://myanimelist.net/clubs.php?cid={CLUB_ID}>)!"
            else:
                m2 = ""

            return m1 + m2

    try:
        jkUser = await getJikanUserData(malUsername.strip())
        malUid = jkUser['mal_id']
        malUname = jkUser['username']
        jkUser['joined'] = jkUser['joined'].replace("+00:00", "+0000")
        malJoined = datetime.datetime.strptime(jkUser['joined'], "%Y-%m-%dT%H:%M:%S%z")
        malJoined = int(malJoined.timestamp())
        registered = int(datetime.datetime.now().timestamp())
        dcJoined = int(snowflake_to_datetime(discordId))
        dcGuildName = server.name
        dcGuildId = server.id
        if actor is not None:
            registeredBy = actor.id
        else:
            registeredBy = discordId

        saveToDatabase(discordId=discordId, discordUsername=whois, discordJoined=dcJoined, malUsername=malUname,
                       malId=malUid, malJoined=malJoined, registeredAt=registered, registeredGuild=dcGuildId,
                       registeredBy=registeredBy, guildName=dcGuildName)

        if actor is not None:
            dcActor = f"{actor.username}#{actor.discriminator}"
            return f"""{EMOJI_SUCCESS} **User registered!**```json
{{
    "discordId": {discordId},
    "discordUsername": "{whois}",
    "discordJoined": {dcJoined},
    "registeredGuildId": {dcGuildId},
    "registeredGuildName": "{dcGuildName}",
    "malUname": "{malUname}",
    "malId": {malUid},
    "malJoined": {malJoined},
    "registeredAt": {registered},
    "registeredBy": {registeredBy} // it's you, {dcActor}!
}}```"""
        else:
            m = f"""{EMOJI_SUCCESS} **Your account has been registered!** :tada:

**Discord Username**: {whois} `{discordId}`
**Discord Joined date**: <t:{dcJoined}:F>
———————————————————————————————
**MyAnimeList Username**: [{malUname}](<https://myanimelist.net/profile/{malUname}>) `{malUid}`
**MyAnimeList Joined date**: <t:{malJoined}:F>"""
            if str(server.id) == str(VERIFICATION_SERVER):
                m += f"\n*Now, please use the command `/verify` if you have joined [our club](<https://myanimelist.net/clubs.php?cid={CLUB_ID}>) to get your role!*"
            return m

    except Exception as e:
        raise Exception(f"{EMOJI_UNEXPECTED_ERROR} {e}")


def exportUserData(userId: int) -> str:
    with open(database, "r") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if row[0] == 'discordId':
                header = row
                continue
            if row[0] == str(userId):
                for i in row:
                    if i is None:
                        row[row.index(i)] = ""
                    if i.isdigit():
                        row[row.index(i)] = int(i)
                    else:
                        row[row.index(i)] = str(i)
                userRow = dict(zip(header, row))
                userRow = json.dumps(userRow)
                return userRow

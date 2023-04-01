from modules.commons import *
from modules.myanimelist import *

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

import pandas as pd

from modules.const import database


def checkIfRegistered(discordId: int) -> bool:
    """Check if user is registered on Database

    Args:
        discordId (int): Discord ID of the user

    Returns:
        bool: True if user is registered, False if not
    """
    df = pd.read_csv(database, delimiter="\t", dtype={'discordId': str})
    if str(discordId) in df['discordId'].values:
        return True
    else:
        return False

from modules.commons import *

def dropUser(discordId: int) -> None:
    """Drop a user from the database"""
    df = pd.read_csv(database, sep="\t")
    df_drop = df.drop(df.query(f'discordId == {discordId}').index)
    df_drop.to_csv(database, sep="\t", index=False, encoding="utf-8")


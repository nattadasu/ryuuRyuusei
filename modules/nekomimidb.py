from modules.commons import *
from modules.platforms import getPlatformColor


async def getNekomimi(gender: str = None) -> dict:
    """Get a random nekomimi image from the database"""
    seed = getRandom()
    nmDb = pd.read_csv("database/nekomimiDb.tsv", sep="\t")
    nmDb = nmDb.fillna('')
    if gender is not None:
        query = nmDb[nmDb['girlOrBoy'] == f'{gender}']
    else:
        query = nmDb
    # get a random row from the query
    row = query.sample(n=1, random_state=seed)
    return row


def generateNekomimi(row: dict) -> interactions.Embed:
    img = row['imageUrl'].values[0]
    mediaSource = row['mediaSource'].values[0]
    if mediaSource == '':
        mediaSource = 'Original Character'
    artist = row['artist'].values[0]
    artistUrl = row['artistUrl'].values[0]
    imageSourceUrl = row['imageSourceUrl'].values[0]
    col = getPlatformColor(row['platform'].values[0])
    # Send the image url to the user
    dcEm = interactions.Embed(
        title=f"{mediaSource}",
        image=interactions.EmbedImageStruct(
            url=str(img)
        ),
        color=col,
        author=interactions.EmbedAuthor(
            name="Powered by Natsu's nekomimiDb",
            url="https://github.com/nattadasu/nekomimiDb"
        ),
        fields=[
            interactions.EmbedField(
                name="Image source",
                value=f"[Click here]({imageSourceUrl})",
                inline=True
            ),
            interactions.EmbedField(
                name="Artist",
                value=f"[{artist}]({artistUrl})",
                inline=True
            )
        ]
    )

    return dcEm


async def nekomimiSubmit(ctx: interactions.CommandContext, gender: str = None):
    data = await getNekomimi(gender)
    dcEm = generateNekomimi(row=data)
    await ctx.send("", embeds=dcEm)

from modules.commons import *
from modules.const import *


async def generateLastFm(username: str, maximum: int = 9) -> interactions.Embed:
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://ws.audioscrobbler.com/2.0/?method=user.getinfo&user={username}&api_key={LASTFM_API_KEY}&format=json') as resp:
            if resp.status == 404:
                raise Exception(
                    "User can not be found on Last.fm. Check the name or register?")
            else:
                jsonText = await resp.text()
                jsonFinal = jload(jsonText)
                ud = jsonFinal['user']
        await session.close()
    tracks = []
    # trim scb if items more than {maximum}
    if maximum > 0:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={username}&api_key={LASTFM_API_KEY}&format=json&limit={maximum}') as resp:
                jsonText = await resp.text()
                jsonFinal = jload(jsonText)
                scb = jsonFinal['recenttracks']['track']
            await session.close()
        if maximum > 1:
            rpt = "\n\n**Recently played tracks**"
        else:
            rpt = "\n\n**Recently played track**"
        if len(scb) > maximum:
            scb = scb[:maximum]
        nRep = 1
        for tr in scb:
            try:
                if tr['@attr']['nowplaying'] is not None:
                    np = jload(tr['@attr']['nowplaying'].lower())
            except:
                np = False
            # sanitize title to be markdown compatible
            tr['name'] = sanitizeMarkdown(str(tr['name']))
            tr['artist']['#text'] = sanitizeMarkdown(
                str(tr['artist']['#text']))
            tr['album']['#text'] = sanitizeMarkdown(
                str(tr['album']['#text']))
            scu = tr['url']
            scus = scu.split("/")
            # assumes the url as such: https://www.last.fm/music/Artist/_/Track
            # so, the artist is at index 4, and track is at index 6
            # in index 4 and 6, encode the string to be url compatible with percent encoding
            track = []
            for art in scus[6].split("+"):
                track.append(urlquote(art))
            track = "+".join(track)
            track = track.replace('%25', '%')

            artist = []
            for art in scus[4].split("+"):
                artist.append(urlquote(art))
            artist = "+".join(artist)
            artist = artist.replace('%25', '%')

            tr['url'] = f"https://www.last.fm/music/{artist}/_/{track}"

            if np is True:
                title = f"▶️ {tr['name']}"
                dt = "*Currently playing*"
            else:
                title = tr['name']
                dt = int(tr['date']['uts'])
                dt = f"<t:{dt}:R>"
            tracks += [interactions.EmbedField(
                name=title,
                value=f"""{tr['artist']['#text']}
{tr['album']['#text']}
{dt}, [Link]({tr['url']})""",
                inline=True
            )]
            nRep += 1
    else:
        rpt = ""
    # read ud['images'], and grab latest one
    imgLen = len(ud['image'])
    img = ud['image'][imgLen - 1]['#text']
    lfmpro = ud['subscriber']
    icShine = "<:icons_shine1:859424400959602718>"
    if lfmpro == "1":
        lfmpro = f"{icShine} Last.FM Pro User\n"
        badge = icShine + " "
    else:
        lfmpro, badge = "", ""
    # building embed
    dcEm = interactions.Embed(
        author=interactions.EmbedAuthor(
            name="Last.FM Profile",
            url="https://last.fm",
            icon_url="https://media.discordapp.net/attachments/923830321433149453/1079483003396432012/Tx1ceVTBn2Xwo2dF.png"
        ),
        title=f"{badge}{ud['name']}'s Last.FM Profile",
        url=ud['url'],
        color=0xF71414,
        description=f"""{lfmpro}Real name: {ud['realname']}
Account created: <t:{ud['registered']['#text']}:D> (<t:{ud['registered']['#text']}:R>)
Total scrobbles: {ud['playcount']}
🧑‍🎤 {ud['artist_count']}  💿 {ud['album_count']} 🎶 {ud['track_count']}{rpt}""",
        thumbnail=interactions.EmbedImageStruct(
            url=img
        ),
        fields=tracks
    )

    return dcEm

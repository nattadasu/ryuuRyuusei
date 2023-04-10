from modules.commons import *
from modules.platforms import *
from modules.simkl import searchSimklId, getSimklID
from modules.trakt import getTraktID, lookupTrakt
from modules.animeapi import getNatsuAniApi


def platformsToFields(currPlatform: str, **k) -> list:
    """Convert a platform to a dictionary of fields"""
    relsEm = []
    if k['allcin'] is not None:
        pin = mediaIdToPlatform(k['allcin'], 'allcin')
        relsEm += [
            interactions.EmbedField(
                name=f"<:allcinema:{pin['emoid']}> {pin['pf']}",
                value=f"[{k['allcin']}](<{pin['uid']}>)",
                inline=True
            )
        ]
    if (k['anidb'] is not None) and (currPlatform != 'anidb'):
        pin = mediaIdToPlatform(k['anidb'], 'anidb')
        relsEm += [
            interactions.EmbedField(
                name=f"<:aniDb:{pin['emoid']}> {pin['pf']}",
                value=f"[{k['anidb']}](<{pin['uid']}>)",
                inline=True
            )
        ]
    if (k['anilist'] is not None) and (currPlatform != 'anilist'):
        pin = mediaIdToPlatform(k['anilist'], 'anilist')
        relsEm += [
            interactions.EmbedField(
                name=f"<:anilist:{pin['emoid']}> {pin['pf']}",
                value=f"[{k['anilist']}](<{pin['uid']}>)",
                inline=True
            )
        ]
    if k['ann'] is not None:
        pin = mediaIdToPlatform(k['ann'], 'ann')
        relsEm += [
            interactions.EmbedField(
                name=f"<:ann:{pin['emoid']}> {pin['pf']}",
                value=f"[{k['ann']}](<{pin['uid']}>)",
                inline=True
            )
        ]
    if (k['animeplanet'] is not None) and (currPlatform != 'animeplanet'):
        pin = mediaIdToPlatform(k['animeplanet'], 'animeplanet')
        relsEm += [
            interactions.EmbedField(
                name=f"<:animePlanet:{pin['emoid']}> {pin['pf']}",
                value=f"[{k['animeplanet']}](<{pin['uid']}>)",
                inline=True
            )
        ]
    if (k['anisearch'] is not None) and (currPlatform != 'anisearch'):
        pin = mediaIdToPlatform(k['anisearch'], 'anisearch')
        relsEm += [
            interactions.EmbedField(
                name=f"<:aniSearch:{pin['emoid']}> {pin['pf']}",
                value=f"[{k['anisearch']}](<{pin['uid']}>)",
                inline=True
            )
        ]
    if (k['annict'] is not None) and (currPlatform != 'annict'):
        pin = mediaIdToPlatform(k['annict'], 'annict')
        relsEm += [
            interactions.EmbedField(
                name=f"<:annict:{pin['emoid']}> {pin['pf']}",
                value=f"[{k['annict']}](<{pin['uid']}>)",
                inline=True
            )
        ]
    if (k['imdb'] is not None) and (currPlatform != 'imdb'):
        pin = mediaIdToPlatform(k['imdb'], 'imdb')
        relsEm += [
            interactions.EmbedField(
                name=f"<:imdb:{pin['emoid']}> {pin['pf']}",
                value=f"[{k['imdb']}](<{pin['uid']}>)",
                inline=True
            )
        ]
    if (k['kaize'] is not None) and (currPlatform != 'kaize'):
        pin = mediaIdToPlatform(k['kaize'], 'kaize')
        relsEm += [
            interactions.EmbedField(
                name=f"<:kaize:{pin['emoid']}> {pin['pf']}",
                value=f"[{k['kaize']}](<{pin['uid']}>)",
                inline=True
            )
        ]
    if (k['kitsu'] is not None) and (currPlatform != 'kitsu'):
        pin = mediaIdToPlatform(k['kitsu'], 'kitsu')
        relsEm += [
            interactions.EmbedField(
                name=f"<:kitsu:{pin['emoid']}> {pin['pf']}",
                value=f"[{k['kitsu']}](<{pin['uid']}>)",
                inline=True
            )
        ]
    if (k['livechart'] is not None) and (currPlatform != 'livechart'):
        pin = mediaIdToPlatform(k['livechart'], 'livechart')
        relsEm += [
            interactions.EmbedField(
                name=f"<:liveChart:{pin['emoid']}> {pin['pf']}",
                value=f"[{k['livechart']}](<{pin['uid']}>)",
                inline=True
            )
        ]
    if (k['myanimelist'] is not None) and (currPlatform != 'myanimelist'):
        pin = mediaIdToPlatform(k['myanimelist'], 'myanimelist')
        relsEm += [
            interactions.EmbedField(
                name=f"<:myAnimeList:{pin['emoid']}> {pin['pf']}",
                value=f"[{k['myanimelist']}](<{pin['uid']}>)",
                inline=True
            )
        ]
    if (k['notify'] is not None) and (currPlatform != 'notify'):
        pin = mediaIdToPlatform(k['notify'], 'notify')
        relsEm += [
            interactions.EmbedField(
                name=f"<:notify:{pin['emoid']}> {pin['pf']}",
                value=f"[{k['notify']}](<{pin['uid']}>)",
                inline=True
            )
        ]
    if (k['otakotaku'] is not None) and (currPlatform != 'otakotaku'):
        pin = mediaIdToPlatform(k['otakotaku'], 'otakotaku')
        relsEm += [
            interactions.EmbedField(
                name=f"<:otakOtaku:{pin['emoid']}> {pin['pf']}",
                value=f"[{k['otakotaku']}](<{pin['uid']}>)",
                inline=True
            )
        ]
    if (k['shikimori'] is not None) and (currPlatform != 'shikimori'):
        pin = mediaIdToPlatform(k['shikimori'], 'shikimori')
        relsEm += [
            interactions.EmbedField(
                name=f"<:shikimori:{pin['emoid']}> {pin['pf']}",
                value=f"[{k['shikimori']}](<{pin['uid']}>)",
                inline=True
            )
        ]
    if (k['shoboi'] is not None) and (currPlatform != 'shoboi'):
        pin = mediaIdToPlatform(k['shoboi'], 'shoboi')
        relsEm += [
            interactions.EmbedField(
                name=f"<:shoboi:{pin['emoid']}> {pin['pf']}",
                value=f"[{k['shoboi']}](<{pin['uid']}>)",
                inline=True
            )
        ]
    if (k['silveryasha'] is not None) and (currPlatform != 'silveryasha'):
        pin = mediaIdToPlatform(k['silveryasha'], 'silveryasha')
        relsEm += [
            interactions.EmbedField(
                name=f"<:silverYasha:{pin['emoid']}> {pin['pf']}",
                value=f"[{k['silveryasha']}](<{pin['uid']}>)",
                inline=True
            )
        ]
    # if ((k['simkl'] is not None) and (str(k['simkl']) != '0')) and (currPlatform != 'simkl'):
    if (k['simkl'] not in [None, 0, '0']) and (currPlatform != 'simkl'):
        pin = mediaIdToPlatform(
            media_id=k['simkl'], platform='simkl', simklType=k['simklType'])
        relsEm += [
            interactions.EmbedField(
                name=f"<:simkl:{pin['emoid']}> {pin['pf']}",
                value=f"[{k['simkl']}](<{pin['uid']}>)",
                inline=True
            )
        ]
    if (k['trakt'] is not None) and (currPlatform != 'trakt'):
        pin = mediaIdToPlatform(k['trakt'], 'trakt')
        relsEm += [
            interactions.EmbedField(
                name=f"<:trakt:{pin['emoid']}> {pin['pf']}",
                value=f"[{k['trakt']}](<{pin['uid']}>)",
                inline=True
            )
        ]
    if (re.match(r'None$', k['tmdb']) is False) and (currPlatform != 'tmdb'):
        tmdb = re.sub(r'^(movie|tv)/', '', k['tmdb'])
        pin = mediaIdToPlatform(k['tmdb'], 'tmdb')
        relsEm += [
            interactions.EmbedField(
                name=f"<:tmdb:{pin['emoid']}> {pin['pf']}",
                value=f"[{tmdb}](<{pin['uid']}>)",
                inline=True
            )
        ]
    if (k['tvdb'] is not None) and (currPlatform != 'tvdb'):
        pin = mediaIdToPlatform(k['tvdb'], 'tvdb')
        if k['isSlug'] is False:
            tvdb = k['tvdb'].split('=')
            # assumes the link is https://www.thetvdb.com/?tab=series&id=123456
            tvdb = tvdb[1]
        else:
            tvdb = k['tvdb']
            # assumes the link is https://www.thetvdb.com/series/123456/seasons/official/1
            # grab from 123456 to the end of the string
            tvdb = re.sub(
                r'^https://(www.)?thetvdb.com/(series|movies)/', '', tvdb)
        relsEm += [
            interactions.EmbedField(
                name=f"<:tvdb:{pin['emoid']}> {pin['pf']}",
                value=f"[{tvdb}](<{pin['uid']}>)",
                inline=True
            )
        ]
    # tvtime
    if (k['tvdb'] is not None) and (k['isSlug'] is False):
        if k['tvtyp'] == 'series':
            tvtime = k['tvdb'].split('=')
            # assumes the link is https://www.thetvdb.com/?tab=series&id=123456
            media_id = tvtime[1]
            pin = mediaIdToPlatform(media_id=media_id, platform='tvtime')
            relsEm += [
                interactions.EmbedField(
                    name=f"<:tvTime:{pin['emoid']}> {pin['pf']}",
                    value=f"[{k['tvdb']}](<{pin['uid']}>)",
                    inline=True
                )
            ]
        else:
            pass

    return relsEm


async def relationsSubmit(ctx: interactions.CommandContext, id: str, platform: str):
    await ctx.send(f"Searching for relations on `{platform}` using ID: `{id}`", embeds=None)
    try:
        simId = 0
        imdbId = None
        malId = None
        tmdbId = None
        tvdbId = None
        traktId = None
        trkSeason = None
        trkType = None
        smk = simkl0rels
        simDat = simkl0rels
        aa = invAa

        # Properly config the ID
        if (platform == 'shikimori') and (re.match(r'^[a-zA-Z]+', id)):
            id = re.sub(r'^[a-zA-Z]+', '', id)
            await ctx.edit(f'Removed the prefix from the ID on `{platform}`', embeds=None)
            aa = await getNatsuAniApi(id=id, platform='shikimori')
        elif platform == 'simkl':
            simDat = await getSimklID(id, 'anime')
            simId = id
            malId = simDat['mal']
        elif platform in ['tmdb', 'tvdb', 'imdb']:
            try:
                if platform == 'tmdb':
                    id = id.split('/')
                    if len(id) > 1:
                        await ctx.edit(f'Season split is currently not supported on `{platform}`', embeds=None)
                        id = id[0]
                simId = await searchSimklId(id, platform=platform)
                simDat = await getSimklID(simId, 'anime')
                malId = simDat['mal']
            except KeyError:
                raise Exception(
                    f'No anime found on SIMKL with ID: `{id}` on `{platform}`')
        elif platform == 'trakt':
            try:
                if re.match(r'^(show|movie)s?\/[a-z0-9-]+(/season(s)?/[\d]+)$', id):
                    trkQuery = id.split('/')
                    trkType = trkQuery[0]
                    traktId = trkQuery[1]
                    if len(trkQuery) > 2:
                        trkSeason = trkQuery[3]
                    if trkType == "show":
                        trkType += "s"
                    elif trkType == "movie":
                        trkType += "s"
                else:
                    raise Exception(
                        'Invalid Trakt ID required by bot. Valid ID format: `shows/<slug-or-id>` and `movies/<slug-or-id>`.')
                trkData = await getTraktID(traktId, trkType)
                traktId = trkData['ids']['trakt']
                imdbId = trkData['ids']['imdb']
                tmdbId = trkData['ids']['tmdb']
                if trkSeason is not None:
                    aa = await getNatsuAniApi(id=f"{trkType}/{traktId}/seasons/{trkSeason}", platform='trakt')
                else:
                    aa = await getNatsuAniApi(id=f"{trkType}/{traktId}", platform='trakt')
                if aa['title'] is not None:
                    simId = await searchSimklId(title_id=aa['myanimelist'], platform='mal')
                elif (aa['title'] is None) and (imdbId is not None):
                    simId = await searchSimklId(title_id=imdbId, platform='imdb')
                elif (aa['title'] is None) and (tmdbId is not None):
                    mdtype = "show" if re.match(
                        r'shows?', trkType) else "movie"
                    simId = await searchSimklId(title_id=tmdbId, platform='tmdb', media_type=mdtype)

                simDat = await getSimklID(simkl_id=simId, media_type='anime')
                malId = simDat['mal']
            except aiohttp.ContentTypeError:
                raise Exception(
                    f'Title not found on the database, or you have entered the wrong ID/slug!')
            except KeyError:
                raise Exception(
                    f'Error while searching for the ID of `{platform}` via `imdb` and `tmdb` on SIMKL, entry may not linked with SIMKL counterpart, so unfortunately we can\'t reverse search for the relation')
        elif platform == 'kitsu':
            if re.match(r'^[a-zA-Z\-]+', id):
                # replace slug to id
                async with aiohttp.ClientSession() as session:
                    async with session.get(f'https://kitsu.io/api/edge/anime?filter[slug]={id}') as resp:
                        if resp.status == 200:
                            kitsuData = await resp.json()
                            ktSlug = id
                            id = kitsuData['data'][0]['id']
                        else:
                            raise Exception(
                                f'Error while searching for the ID of `{platform}`')
                    await session.close()
                await ctx.edit(f'Replaced the slug (`{ktSlug}`) with the ID (`{id}`) on `{platform}`', embeds=None)
            aa = await getNatsuAniApi(id=id, platform=platform)
        elif platform == 'kaize':
            try:
                try:
                    aa = await getNatsuAniApi(id=id, platform=platform)
                except:
                    # check on slug using regex, if contains `-N` suffix, try to decrease by one,
                    # if `-N` is `-1`, remove completely the slug
                    # get the last number
                    lastNum = re.search(r'\d+$', uid).group()
                    # get the slug
                    slug = re.sub(r'-\d+$', '', uid)
                    # decrease the number by one
                    lastNum = int(lastNum) - 1
                    # if the number is 0, remove the suffix
                    if lastNum == 0:
                        uid = slug
                    else:
                        uid = f"{slug}-{lastNum}"
                    await ctx.edit(f"Searching for relations on `{platform}` using ID: `{uid}` (decrease by one)", embeds=None)
                    aa = await getNatsuAniApi(id=uid, platform=platform)
            except json.JSONDecodeError:
                raise Exception(ERR_KAIZE_SLUG_MODDED)
        else:
            aa = await getNatsuAniApi(id=id, platform=platform)

        if (aa['title'] is None) and (malId is not None):
            aa = await getNatsuAniApi(id=malId, platform='myanimelist')

        # link SIMKL ID
        if platform not in ['simkl', 'trakt', 'tmdb', 'tvdb', 'imdb']:
            try:
                if aa['myanimelist'] is not None:
                    simId = await searchSimklId(title_id=aa['myanimelist'], platform='mal')
                    smk = await getSimklID(simkl_id=simId, media_type='anime')
                elif aa['anidb'] is not None:
                    simId = await searchSimklId(title_id=aa['anidb'], platform='anidb')
                    smk = await getSimklID(simkl_id=simId, media_type='anime')
            except:
                pass
        else:
            smk = simDat

        if (tmdbId is None) and (platform != 'tmdb'):
            tmdbId = smk['tmdb']
        elif platform == 'tmdb':
            tmdbId = id
        if (imdbId is None) and (platform != 'imdb'):
            imdbId = smk['imdb']
        elif platform == 'imdb':
            imdbId = id

        if (aa['title'] is None) and (simId != 0):
            title = smk['title']
        else:
            title = aa['title']

        if (aa['trakt'] is not None) and (platform != 'trakt'):
            trkType = aa['trakt_type']
            trkSeason = aa['trakt_season']
            traktId = f"{trkType}/{aa['trakt']}/seasons/{trkSeason}"
        elif (aa['trakt'] is None) and ((tmdbId is not None) or (imdbId is not None)) and (platform != 'trakt'):
            try:
                tid = imdbId
                lookup = f"imdb/{tid}"
                scpf = "IMDb"
                trkData = await lookupTrakt(lookup_param=lookup)
                trkType = trkData['type']
                traktId = trkData[trkType]['ids']['trakt']
            except KeyError:
                try:
                    tid = tmdbId
                    ttype = "movie" if smk['aniType'] == "movie" else "show" if (
                        (smk['aniType'] == "tv") or (smk['aniType'] == "ona")) else "movie"
                    lookup = f"tmdb/{tid}?type={ttype}"
                    scpf = "TMDB"
                    trkData = await lookupTrakt(lookup_param=lookup)
                    trkType = trkData['type']
                    traktId = trkData[trkType]['ids']['trakt']
                except KeyError:
                    pass

        relsEm = []
        # Get the relations
        try:
            if traktId is not None:
                if re.search(r"^shows?$", trkType):
                    tvtyp = "series"
                    tmtyp = "tv"
                else:
                    tvtyp = "movies"
                    tmtyp = "movie"
            else:
                if smk['aniType'] == "tv":
                    tvtyp = "series"
                    tmtyp = "tv"
                elif smk['aniType'] is not None:
                    tvtyp = "movies"
                    tmtyp = "movie"
        except:
            tvtyp = "series"
            tmtyp = "tv"
        isSlug = False

        if trkSeason is not None:
            if smk['tvdb'] is not None:
                tvdbId = 'https://www.thetvdb.com/' + \
                    f"?tab={tvtyp}&id={smk['tvdb']}"
            elif smk['tvdbslug'] is not None:
                tvdbId = 'https://www.thetvdb.com/' + \
                    f"{tvtyp}/{smk['tvdbslug']}/seasons/official/{trkSeason}"
                isSlug = True
            tmdbId = f"{tmtyp}/{tmdbId}/season/{trkSeason}"
        else:
            if smk['tvdb'] is not None:
                tvdbId = 'https://www.thetvdb.com/' + \
                    f"?tab={tvtyp}&id={smk['tvdb']}"
            elif smk['tvdbslug'] is not None:
                tvdbId = 'https://www.thetvdb.com/' + \
                    tvtyp + '/' + smk['tvdbslug']
                isSlug = True
            tmdbId = tmtyp + '/' + str(tmdbId)

        relsEm = platformsToFields(
            currPlatform=platform,
            allcin=smk['allcin'],
            anidb=aa['anidb'],
            anilist=aa['anilist'],
            ann=smk['ann'],
            animeplanet=aa['animeplanet'],
            anisearch=aa['anisearch'],
            annict=aa['annict'],
            imdb=imdbId,
            kaize=aa['kaize'],
            kitsu=aa['kitsu'],
            livechart=aa['livechart'],
            myanimelist=aa['myanimelist'],
            notify=aa['notify'],
            otakotaku=aa['otakotaku'],
            shikimori=aa['shikimori'],
            shoboi=aa['shoboi'],
            silveryasha=aa['silveryasha'],
            simkl=simId,
            simklType=smk['type'],
            trakt=traktId,
            tvdb=tvdbId,
            tmdb=tmdbId,
            tvtyp=tvtyp,
            isSlug=isSlug,
        )

        if (platform == 'tvdb') and (re.match(r"^[\d]+$", id)):
            tvdbId = f"https://www.thetvdb.com/?tab={tvtyp}&id={id}"
        elif (platform == 'tvdb'):
            tvdbId = f"https://www.thetvdb.com/{tvtyp}/{id}"
        else:
            tvdbId = None

        col = getPlatformColor(platform)

        if platform == 'trakt':
            media_id = f"{trkType}/{traktId}"
        elif platform == 'tvdb':
            media_id = tvdbId
        elif platform == 'tmdb':
            media_id = f"{tmtyp}/{id}"
        else:
            media_id = id

        pfs = mediaIdToPlatform(media_id=media_id, platform=platform)
        pf = pfs['pf']
        uid = pfs['uid']
        emoid = pfs['emoid']

        if smk['poster'] is not None:
            poster = f"https://simkl.in/posters/{smk['poster']}_m.webp"
            postsrc = "SIMKL"
        elif aa['kitsu'] is not None:
            poster = f"https://media.kitsu.io/anime/poster_images/{aa['kitsu']}/large.jpg"
            postsrc = "Kitsu"
        elif aa['notify'] is not None:
            poster = f"https://media.notify.moe/images/anime/original/{aa['notify']}.jpg"
            postsrc = "Notify.moe"
        else:
            poster = None
            postsrc = None

        if postsrc is not None:
            postsrc = f" Poster from {postsrc}"
        else:
            postsrc = ""

        uAu = uid.split('/')
        uAu = uAu[0] + "//" + uAu[2]

        if title is not None:
            dcEm = interactions.Embed(
                author=interactions.EmbedAuthor(
                    name=f"Looking external site relations from {pf}",
                    icon_url=f"https://cdn.discordapp.com/emojis/{emoid}.png?v=1",
                    url=uAu
                ),
                title=f"{title}",
                url=uid,
                description="Data might be inaccurate, especially for sequels of the title (as IMDb, TVDB, TMDB, and Trakt relies on per title entry than season entry)",
                color=col,
                fields=relsEm,
                footer=interactions.EmbedFooter(
                    text=f"Powered by nattadasu's AnimeAPI, Trakt, and SIMKL.{postsrc}"
                ),
                thumbnail=interactions.EmbedImageStruct(
                    url=poster
                )
            )
        else:
            raise Exception(
                f"No relations found on {pf} with following url: <{uid}>!\nEither the anime is not in the database, or you have entered the wrong ID.")
        await ctx.edit("", embeds=dcEm)

    except Exception as e:
        if e == 'Expecting value: line 1 column 1 (char 0)':
            e = 'No relations found!\nEither the anime is not in the database, or you have entered the wrong ID.'
        else:
            e = e
        e = f"""While getting the relations for `{platform}` with id `{id}`, we got error message: {e}"""
        dcEm = exceptionsToEmbed(returnException(e))

        await ctx.edit("", embeds=dcEm)

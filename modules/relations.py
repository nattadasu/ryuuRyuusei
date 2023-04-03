from modules.commons import *
from modules.platforms import *


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
        pin = mediaIdToPlatform(media_id=k['simkl'], platform='simkl', simklType=k['simklType'])
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

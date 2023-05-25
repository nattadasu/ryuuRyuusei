import interactions as ipy

from classes.animeapi import AnimeApi, AnimeApiAnime
from classes.trakt import Trakt
from classes.simkl import Simkl, SimklRelations, SimklMediaTypes
from classes.excepts import ProviderHttpError, SimklTypeError
from classes.kitsu import Kitsu
from typing import Literal
import re

from modules.platforms import (
    platforms_to_fields,
    media_id_to_platform,
    get_platform_color,
)


class ExtenalSitesRelations(ipy.Extension):
    """Extension class for /relations"""

    def __init__(self, bot: ipy.AutoShardedClient):
        """Initialize the extension class"""
        self.bot = bot
        """The bot client"""

    @ipy.slash_command(
        name="relations",
        description="Get external links relations of a title from one of the supported sites",
    )
    async def relations(self, ctx: ipy.SlashContext):
        pass

    @staticmethod
    async def search_simkl_id(
        provider: Simkl.Provider,
        media_id: str,
        media_type: Simkl.TmdbMediaTypes | None = None,
    ) -> dict:
        """
        Utility function to search for a title on SIMKL by ID

        Args:
            provider (Simkl.Provider): The provider to search on
            media_id (str): The media ID
            media_type (Simkl.TmdbMediaTypes | None, optional): The media type if it's TMDB. Defaults to None.
        """
        async with Simkl() as simkl:
            entry = await simkl.search_by_id(provider, media_id, media_type=media_type)
            if entry is None:
                raise SimklTypeError(
                    "Could not find any entry with the given ID",
                    expected_type=list[dict],
                )
            return entry[0]

    @staticmethod
    async def get_simkl_title_ids(simkl_id: int) -> SimklRelations:
        """
        Utility function to get the title IDs from SIMKL

        Args:
            simkl_id (int): SIMKL ID

        Returns:
            SimklRelations: SIMKL relations object
        """
        async with Simkl() as simkl:
            return await simkl.get_title_ids(
                id=simkl_id, media_type=SimklMediaTypes.ANIME
            )

    @staticmethod
    async def get_anime_api_relation(
        media_id: str, platform: AnimeApi.AnimeApiPlatforms
    ) -> AnimeApiAnime:
        """
        Utility function to get the relation from Anime API

        Args:
            media_id (str): The media ID
            platform (AnimeApi.AnimeApiPlatforms): The platform to get the relation from

        Returns:
            AnimeApiAnime: The Anime API relation object
        """
        async with AnimeApi() as api:
            return await api.get_relation(media_id=f"{media_id}", platform=platform)

    @relations.subcommand(
        sub_cmd_name="shows",
        sub_cmd_description="Get external links relations of a show from one of the supported sites",
        options=[
            ipy.SlashCommandOption(
                name="media_id",
                description="The media ID of the show",
                type=ipy.OptionType.STRING,
                required=True,
            ),
            ipy.SlashCommandOption(
                name="platform",
                description="The platform to get the relations from",
                type=ipy.OptionType.STRING,
                choices=[
                    ipy.SlashCommandChoice(name="aniDB", value="anidb"),
                    ipy.SlashCommandChoice(name="AniList", value="anilist"),
                    ipy.SlashCommandChoice(name="Anime-Planet", value="animeplanet"),
                    ipy.SlashCommandChoice(name="Annict", value="annict"),
                    ipy.SlashCommandChoice(name="IMDb", value="imdb"),
                    ipy.SlashCommandChoice(name="Kaize", value="kaize"),
                    ipy.SlashCommandChoice(name="Kitsu", value="kitsu"),
                    ipy.SlashCommandChoice(name="LiveChart", value="livechart"),
                    ipy.SlashCommandChoice(name="MyAnimeList", value="myanimelist"),
                    ipy.SlashCommandChoice(name="Notify.moe", value="notify"),
                    ipy.SlashCommandChoice(name="Otak Otaku", value="otakotaku"),
                    ipy.SlashCommandChoice(name="Shikimori", value="shikimori"),
                    ipy.SlashCommandChoice(name="Shoboi", value="shoboi"),
                    ipy.SlashCommandChoice(
                        name="Silver Yasha: DB Tontonan Indonesia", value="silveryasha"
                    ),
                    ipy.SlashCommandChoice(name="SIMKL", value="simkl"),
                    ipy.SlashCommandChoice(name="The Movie Database", value="tmdb"),
                    ipy.SlashCommandChoice(name="The TVDB", value="tvdb"),
                    ipy.SlashCommandChoice(
                        name="Trakt (requires <type>/<slug>/seasons/<season>)",
                        value="trakt",
                    ),
                ],
                required=True,
            ),
            ipy.SlashCommandOption(
                name="media_type",
                description="The media type of the show, required for TMDB",
                type=ipy.OptionType.STRING,
                choices=[
                    ipy.SlashCommandChoice(name="TV Shows", value="show"),
                    ipy.SlashCommandChoice(name="Movie", value="movie"),
                ],
                required=False,
            ),
        ],
    )
    async def relations_shows(
        self,
        ctx: ipy.SlashContext,
        media_id: str,
        platform: Literal[
            "anidb",
            "anilist",
            "animeplanet",
            "aniSearch",
            "annict",
            "imdb",
            "kaize",
            "kitsu",
            "livechart",
            "myanimelist",
            "notify",
            "otakotaku",
            "shikimori",
            "shoboi",
            "silveryasha",
            "simkl",
            "tmdb",
            "tvdb",
            "trakt",
        ],
        media_type: Literal["show", "movie"] | None = None,
    ) -> None:
        simkl_id = 0
        imdb_id = None
        mal_id = None
        tmdb_id = None
        tvdb_id = None
        trakt_id = None
        trakt_season = None
        trakt_type = None
        simkl_dat = SimklRelations()

        if (platform == "shikimori") and (not re.match(r"^\d+$", media_id)):
            media_id = re.search(r"^\d+", media_id).group(0)
            anime_api = await self.get_anime_api_relation(
                media_id=f"{media_id}", platform=AnimeApi.AnimeApiPlatforms.SHIKIMORI
            )
            simkl_id = await self.search_simkl_id(
                Simkl.Provider.MYANIMELIST, media_id, media_type=media_type
            )
            simkl_id = simkl_id["ids"]["simkl"]
            simkl_dat = await self.get_simkl_title_ids(simkl_id)
        elif platform == "simkl":
            simkl_dat = await self.get_simkl_title_ids(media_id)
            simkl_id = media_id
            mal_id = simkl_dat.mal
            anime_api = (
                await self.get_anime_api_relation(
                    f"{mal_id}", AnimeApi.AnimeApiPlatforms.MAL
                )
                if mal_id
                else AnimeApiAnime()
            )
        elif platform in ["tmdb", "tvdb", "imdb"]:
            try:
                if platform == "tmdb":
                    media_id = media_id.split("/")[0]
                simkl_id = await self.search_simkl_id(
                    Simkl.Provider(platform), media_id, media_type=media_type
                )
                simkl_id = simkl_id["ids"]["simkl"]
                simkl_dat = await self.get_simkl_title_ids(simkl_id)
                mal_id = simkl_dat.mal
                anime_api = (
                    await self.get_anime_api_relation(
                        f"{mal_id}", AnimeApi.AnimeApiPlatforms.MAL
                    )
                    if mal_id
                    else AnimeApiAnime()
                )
            except SimklTypeError:
                await ctx.send(
                    f"❌ The media type is required for {platform}! Please use the `media_type` option to specify it!"
                )
                return
        elif platform == "trakt":
            try:
                matching = re.match(
                    r"^(?P<type>show|movie)s?/(?P<slug>[^/]+)(?:/seasons?/(?P<season>\d+))?$",
                    media_id,
                )
                if matching:
                    trakt_type = matching.group("type")
                    trakt_id = matching.group("slug")
                    trakt_season = matching.group("season")
                    if trakt_season is None:
                        trakt_season = 1
                else:
                    await ctx.send(
                        "❌ The Trakt ID is invalid! Please use the format `<type>/<slug>/[seasons/<season>]`!"
                    )
                async with Trakt() as api:
                    trakt_data = await api.get_title_data(
                        media_id=trakt_id,
                        media_type=api.MediaType(f"{trakt_type}s"),
                    )
                    imdb_id = trakt_data.ids.imdb
                    tmdb_id = trakt_data.ids.tmdb
                    tvdb_id = trakt_data.ids.tvdb
                anime_api = (
                    await self.get_anime_api_relation(
                        f"{trakt_type}/{trakt_id}/seasons/{trakt_season}",
                        AnimeApi.AnimeApiPlatforms.TRAKT,
                    )
                    if trakt_id
                    else AnimeApiAnime()
                )
                tmdb_media_type = None
                if anime_api.myanimelist:
                    mal_id = anime_api.myanimelist
                    pfm = Simkl.Provider.MYANIMELIST
                    search_id = mal_id
                elif imdb_id:
                    pfm = Simkl.Provider.IMDB
                    search_id = imdb_id
                elif tmdb_id:
                    pfm = Simkl.Provider.TMDB
                    tmdb_media_type = (
                        Simkl.TmdbMediaTypes.MOVIE
                        if trakt_type == "movie"
                        else Simkl.TmdbMediaTypes.TV
                    )
                    search_id = tmdb_id
                elif tvdb_id:
                    pfm = Simkl.Provider.TVDB
                    search_id = tvdb_id
                simkl_id = await self.search_simkl_id(
                    pfm, search_id, media_type=tmdb_media_type
                )
                simkl_id = simkl_id["ids"]["simkl"]
                simkl_dat = await self.get_simkl_title_ids(simkl_id)
            except ProviderHttpError as eht:
                await ctx.send(
                    f"❌ We can't connect to Trakt right now! Please try again later! Reason: {eht.message}"
                )
                return
        elif platform == "kitsu":
            if not re.match(r"^\d+$", media_id):
                async with Kitsu() as api:
                    kitsu_data = await api.resolve_slug(
                        slug=media_id,
                        media_type=api.MediaType.ANIME,
                    )
                    media_id = kitsu_data["data"][0]["id"]
            anime_api = await self.get_anime_api_relation(
                f"{media_id}", AnimeApi.AnimeApiPlatforms.KITSU
            )
        elif platform == "kaize":
            anime_api = await self.get_anime_api_relation(
                media_id, AnimeApi.AnimeApiPlatforms.KAIZE
            )
            if anime_api.myanimelist is None:
                await ctx.send("❌ AnimeAPI can't find correlations for Kaize!")
                return
        else:
            async with AnimeApi() as api:
                anime_api = await api.get_relation(
                    media_id=f"{media_id}",
                    platform=AnimeApi.AnimeApiPlatforms(platform),
                )

        if platform not in ["simkl", "trakt", "tmdb", "tvdb", "imdb"]:
            pfm = (
                anime_api.myanimelist
                if anime_api.myanimelist
                else anime_api.anidb
                if anime_api.anidb
                else None
            )
            if pfm:
                simkl_id = await self.search_simkl_id(
                    media_id=pfm,
                    provider=Simkl.Provider.MYANIMELIST
                    if anime_api.myanimelist
                    else Simkl.Provider.ANIDB,
                )
                simkl_id = simkl_id["ids"]["simkl"]
                simkl_dat = await self.get_simkl_title_ids(simkl_id)

        if tmdb_id is None:
            tmdb_id = simkl_dat.tmdb if platform != "tmdb" else media_id

        if imdb_id is None:
            imdb_id = simkl_dat.imdb if platform != "imdb" else media_id

        title = (
            simkl_dat.title
            if anime_api.title is None and simkl_id != 0
            else anime_api.title
        )

        if anime_api.trakt is not None and platform != "trakt":
            trakt_type = anime_api.trakt_type
            trakt_season = anime_api.trakt_season
            trakt_id = f"{trakt_type}/{anime_api.trakt}/seasons/{trakt_season}"
        elif (
            anime_api.trakt is None
            and (tmdb_id is not None or imdb_id is not None)
            and platform != "trakt"
        ):
            try:
                tid = imdb_id if imdb_id is not None else tmdb_id
                platform_ = "imdb" if imdb_id is not None else "tmdb"
                if simkl_dat.anitype == "movie" or simkl_dat.type == "movie":
                    media_type_ = "movies"
                elif simkl_dat.anitype in ["tv", "ona"] or simkl_dat.type == "tv":
                    media_type_ = "shows"
                else:
                    media_type_ = "movies"
                async with Trakt() as trakt:
                    trakt_data = await trakt.lookup(
                        media_id=tid,
                        platform=trakt.Platform(platform_),
                        media_type=trakt.MediaType(media_type_),
                    )
                trakt_type = trakt_data.type
                trakt_id = (
                    trakt_data.show.ids.trakt
                    if trakt_data.type == "show"
                    else trakt_data.movie.ids.trakt
                )
            except ProviderHttpError as eht:
                await ctx.send(
                    f"❌ We can't connect to Trakt right now! Please try again later! Reason: {eht.message}"
                )
                return

        try:
            if trakt_id is not None or (
                simkl_dat.anitype == "tv" if simkl_dat.anitype is not None else False
            ):
                tvtyp = "series"
                tmtyp = "tv"
            else:
                tvtyp = "movies"
                tmtyp = "movie"
        except BaseException:
            tvtyp = "series"
            tmtyp = "tv"
        is_slug = False

        if trakt_season is not None:
            if simkl_dat.tvdb is not None:
                tvdb_id = f"https://www.thetvdb.com/?tab={tvtyp}&id={simkl_dat.tvdb}"
            elif simkl_dat.tvdbslug is not None:
                tvdb_id = f"https://www.thetvdb.com/{tvtyp}/{simkl_dat.tvdbslug}/seasons/official/{trakt_season}"
                is_slug = True
            tmdb_id = f"{tmtyp}/{tmdb_id}/season/{trakt_season}"
        else:
            if simkl_dat.tvdb is not None:
                tvdb_id = f"https://www.thetvdb.com/?tab={tvtyp}&id={simkl_dat.tvdb}"
            elif simkl_dat.tvdbslug is not None:
                tvdb_id = f"https://www.thetvdb.com/{tvtyp}/{simkl_dat.tvdbslug}"
                is_slug = True
            tmdb_id = f"{tmtyp}/{tmdb_id}"

        relsEm = platforms_to_fields(
            currPlatform=platform,
            allcin=simkl_dat.allcin,
            anidb=anime_api.anidb,
            anilist=anime_api.anilist,
            ann=simkl_dat.ann,
            animeplanet=anime_api.animeplanet,
            anisearch=anime_api.anisearch,
            annict=anime_api.annict,
            imdb=imdb_id,
            kaize=anime_api.kaize,
            kitsu=anime_api.kitsu,
            livechart=anime_api.livechart,
            myanimelist=anime_api.myanimelist,
            notify=anime_api.notify,
            otakotaku=anime_api.otakotaku,
            shikimori=anime_api.shikimori,
            shoboi=anime_api.shoboi,
            silveryasha=anime_api.silveryasha,
            simkl=simkl_id,
            simklType=simkl_dat.type,
            trakt=trakt_id,
            tvdb=tvdb_id,
            tmdb=tmdb_id,
            tvtyp=tvtyp,
            is_slug=is_slug,
        )

        tvdb_id = None
        col = get_platform_color(platform)
        poster = None
        postsrc = None

        if platform == "tvdb":
            if re.match(r"^\d+$", id):
                tvdb_id = f"https://www.thetvdb.com/?tab={tvtyp}&id={id}"
            else:
                tvdb_id = f"https://www.thetvdb.com/{tvtyp}/{id}"
        elif platform == "trakt":
            media_id = f"{trakt_type}/{trakt_id}"
        elif platform == "tmdb":
            media_id = f"{tmtyp}/{id}"

        pfs = media_id_to_platform(
            media_id=media_id, platform=platform, simkl_type=simkl_dat.type
        )
        pf = pfs["pf"]
        uid = pfs["uid"]
        emoid = pfs["emoid"]

        if simkl_dat.poster is not None:
            poster = f"https://simkl.in/posters/{simkl_dat.poster}_m.webp"
            postsrc = "SIMKL"
        elif anime_api.kitsu is not None:
            poster = f"https://media.kitsu.io/anime/poster_images/{anime_api.kitsu}/large.jpg"
            postsrc = "Kitsu"
        elif anime_api.notify is not None:
            poster = (
                f"https://media.notify.moe/images/anime/original/{anime_api.notify}.jpg"
            )
            postsrc = "Notify.moe"

        postsrc = f" Poster from {postsrc}" if postsrc else ""

        uAu = "/".join(uid.split("/")[:3])

        if title is not None:
            dcEm = ipy.Embed(
                author=ipy.EmbedAuthor(
                    name=f"Looking external site relations from {pf}",
                    icon_url=f"https://cdn.discordapp.com/emojis/{emoid}.png?v=1",
                    url=uAu,
                ),
                title=title,
                url=uid,
                description="Data might be inaccurate, especially for sequels of the title (as IMDb, TVDB, TMDB, and Trakt rely on per title entry rather than season entry)",
                color=col,
                fields=relsEm,
                footer=ipy.EmbedFooter(
                    text=f"Powered by nattadasu's AnimeAPI, Trakt, and SIMKL.{postsrc}"
                ),
            )
            dcEm.set_thumbnail(url=poster)
        else:
            raise Exception(
                f"No relations found on {pf} with the following URL: <{uid}>!\nEither the anime is not in the database, or you have entered the wrong ID."
            )

        await ctx.send(embed=dcEm)


def setup(bot: ipy.AutoShardedClient) -> None:
    ExtenalSitesRelations(bot)

<!-- markdownlint-disable MD033 MD013 MD041 -->

<p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="assets/logo.png" alt="Bot logo"></a>
</p>

<!-- omit in toc -->
<h3 align="center">Ryuuzaki Ryuusei</h3>

<p align="center"><img src="https://img.shields.io/badge/Interactions.py-5.0.0-blue?style=for-the-badge&logo=python">
<img src="https://img.shields.io/badge/Python-3.10_and_above-blue?style=for-the-badge&logo=python"></p>

---

<p align="center"> 🤖 A Title (Anime, Manga, Game, TV, Movie) Lookup and Member
Verificator Bot for Discord, With Privacy in Mind.
    <br>
</p>

<!-- markdownlint-enable MD013 -->

## 🧐 About <a name = "about"></a>

Ryuuzaki Ryuusei is a Discord bot that can be used to verify MAL club members and advanced media title lookup (anime, manga, games, tv, movie) statically while it keeping simple and easy to use, also respecting users under GDPR, CCPA/CPRA, and other privacy laws.

By inviting this bot to your server or using it, you agree to the [Privacy Policy](PRIVACY.md) and [Terms of Service](TERMS_OF_SERVICE.md).

> **Warning**
> 
> This bot is a rolling release bot, which means that the bot may not be stable and may have bugs. If you find any bugs, please report it to GitHub Issues or on the support server.

## 🎈 Usage <a name = "usage"></a>

To use the bot, invite it to your server using this link:

[![Shield](https://img.shields.io/badge/Invite%20to%20your%20server-7289DA?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com/api/oauth2/authorize?client_id=811887256368840744&permissions=274878221376&scope=bot%20applications.commands)

Next, go to the channel you want to use the bot in and type `/` to see the list of available commands.

Currently the bot was self-hosted, so it's might not available 24/7, but it get the job done. Although, I'll try to keep it online as much as possible.

All data invoked from `/register` will be stored in [database.csv](database/database.csv), user is able to delete their data by using `/unregister` command. Most commands can be used without `/register` command, although it may limit your experience using it.

If you have any questions, feel free to join the [support server](https://nttds.my.id/discord) and ask there.

## 🚀 Features <a name = "features"></a>

> This also will be our to-do list for the bot. :3

- [x] MAL account verification (only for self-hosted bot).
- [x] Privacy-friendly: no data is stored on the bot's server, except for the user's Discord ID and MAL username. See [Privacy Policy](PRIVACY.md) for more information.
- [x] Delete your data from the bot's database at any time as you wish using `/unregister` command.
- [x] Beautiful embed with thumbnail and footer.
- [x] Simple yet powerful anime, manga, and game lookup.
  - [x] Ability to select search result from multiple results rather than automatically selecting the first result. (I'm looking at you, Nadeko)
  - [x] Accurate release date, adapted to your local timezone (based on MyAnimeList).
  - [x] External links (MAL, AniList, AniDB, Kitsu, SIMKL, IMDb, TMDB, Trakt, and more).
  - [x] A lot of information about the media compared to competitors: synopsis, genres and themes, rating with total votes, and more!
  - [x] Know ID of the title you want to search? Use `/command info` command instantly!
- [x] Shows your birthday; including remaining days to your upcoming birthday (based on MyAnimeList user profile).
- [x] Customizable Last.fm scrobble summary.
- [x] Export your data in JSON or Python dictionary format.
- [x] Experience the *"true"* randomness result on `/anime random` and `/random_nekomimi` commands![^1]
- [x] Self-hosting on your phone? No problem! Bot has been tested on Termux on Android 11.
- [x] ~~**100% Approved by Kagamine Len**[^2]~~
- [ ] Does not support dynamic airing reminder. LiveChart + RSS bot is a good alternative.
- [ ] Does not support updating your list to MyAnimeList. You can use [White Cat](https://whitecat.app) instead.
- [ ] Currently does not support character and cast lookup as it can be really complicated if you're using multiple platforms.

## 📣 Available Commands <a name = "commands"></a>

### Anime Commands

> Utilize MyAnimeList via Jikan

- `/anime info` - Get information about an anime using direct MyAnimeList ID
- `/anime random` - Get a random anime from MyAnimeList, powered by [AnimeApi](https://nttds.my.id/discord)
- `/anime search` - Search for an anime, using AniList's search API

### Manga Commands

> Utilize AniList

- `/manga info` - Get information about a manga using direct AniList ID
- `/manga search` - Search for a manga

### Game Commands

> Utilize RAWG

- `/games info` - Get information about a game using direct RAWG ID
- `/games search` - Search for a game

### TV and Movie Commands

> Utilize SIMKL for Metadata and TMDB for NSFW check

- `/movie info` - Get information about a movie using direct SIMKL ID
- `/movie search` - Search for a movie
- `/tv info` - Get information about a TV show using direct SIMKL ID
- `/tv search` - Search for a TV show

### Music Commands

> Utilize Spotify

- `/music album info` - Get information about an album using direct Spotify ID
- `/music album search` - Search for an album
- `/music artist info` - Get information about an artist using direct Spotify ID
- `/music artist search` - Search for an artist
- `/music track info` - Get information about a track using direct Spotify ID
- `/music track search` - Search for a track

### External Link Relation Command

> Utilize nattadasu's AnimeAPI for video type, AniList for manga, and Song.link for music

- `/relations shows` - Get external link relation for an anime, TV, or movie
- `/relations manga` - Get external link relation for a manga, limited to AniList, MyAnimeList, and Shikimori.
- `/relations music track` - Get external link relation for a track.
- `/relations music album` - Get external link relation for an album.

### Last.FM Integration Commands

- `/lastfm` - Get your last.fm profile and the scrobble summary

### Data Control

- `/export_data` - Export your data from the bot in JSON
- `/profile` - Get your MAL profile, statistic available on extended view (passed from option/argument)
- `/register` - Register your MAL account to the bot
- `/unregister` - Unregister your MAL account and drops your settings from the bot
- `/verify` - Verify your MAL account to the server that host the bot (you may need to join the club first)
- `/whois` - Get information about a user, including their MAL account (if any)

### Settings Commands

#### User Settings

- `/usersettings language list` - List all available languages for the bot response
- `/usersettings language set` - Set your preferred language for the bot response

#### Server Settings

- `/serversettings language set` - Set your preferred language for the bot response
- `/serversettings member register` - Register member's MAL account to the bot, used when user can't invoke `/register`
- `/serversettings member unregister` - Unregister member's MAL account from the bot, used when user can't invoke `/unregister`
- `/serversettings member verify` - Verify member's MAL account to the server that host the bot, used when user can't invoke `/verify`

### Miscellaneous Commands

- `/random_nekomimi` - Get a random nekomimi image from the database, powered by [nattadasu/nekomimiDb](https://github.com/nattadasu/nekomimiDb)
  - `/random_nekomimi bois` - Get a random male nekomimi image
  - `/random_nekomimi gurls` - Get a random female nekomimi image
  - `/random_nekomimi true_random` - *Harness the true power of having a random* *nekomimi image*
- `/snowflake` - Convert Discord snowflake to UNIX/Epoch timestamp

### Commons Bot Commands

- `/about` - Get information about the bot
- `/invite` - Get the bot's invite link
- `/ping` - Check the bot latency
- `/privacy` - Get information about the bot's privacy policy

## 🏁 Getting Started <a name = "getting_started"></a>

### Prerequisites

Before you begin, ensure you have met the following requirements:

- You have installed the latest version of `python`, `pip`, and `git`.
- Has a Discord bot token.

### Installing

> Depends on your OS, you may need to use `python3` for the command instead of `python`. You may also need to install packages/modules as superuser/root before continuing to ./firstRun.py

To install Ryuuzaki Ryuusei, follow these steps:

```bash
git clone https://github.com/nattadasu/ryuuRyuusei.git
cd ryuuRyuusei
# you may sudo this command if you're on Linux or macOS to avoid permission error
python -m pip install -r requirements.txt
```

Next, you need to do an initial setup for the bot. Run `firstRun.py` and let the automation intelligently pick the latest version of installed Python and installs `jikanpy` from GitHub repository (we need APIv4 and AioJikan support), install required modules for the bot, and finally prepare databases (bot, `nattadasu/nekomimiDb`, and AnimeAPI).

```bash
python ./firstRun.py
```

> **Note**
> 
> In some cases, you may need to add variable `PYTHON_BINARY` to skip the automatic Python version detection. For example in PowerShell (Windows/Core), if you have multiple versions of Python installed, you can use
> 
> ```pwsh
> $Env:PYTHON_BINARY = "${Env:LOCALAPPDATA}/Programs/Python/Python39/python.exe"
> ```
> 
> to force the script to use Python 3.9.

Then, when `pip` finished installing all of required modules, copy `.env.example` to `.env` and fill the required fields.

```bash
cp .env.example .env
```

> **Note**
> 
> `firstRun.py` already did this for you, but you can do it manually if you want, or if the script unable to do it for you.

Finally, run the bot using `python` command:

```bash
python ./main.py
```

## ⛏️ Built Using <a name = "built_using"></a>

<!-- markdownlint-disable MD013 -->
| Service                                                               | Type     | Description                                                                                                                                  |
| --------------------------------------------------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| [AniList](https://anilist.co)                                         | Database | A database site for anime and manga. Used for anime-manga search, manga information result,  and images.                                     |
| [interactions.py](https://github.com/interactions-py/interactions.py) | Library  | A Python library for Discord's slash commands. A backbone of the bot.                                                                        |
| [jikanpy](https://github.com/abhinavk99/jikanpy)                      | Library  | A Python wrapper for the unofficial MyAnimeList API, [Jikan](https://jikan.moe). Used for anime information, user profile, and anime search. |
| [Kitsu](https://kitsu.io)                                             | Database | A database site for anime and manga. Used only for images and converting Kitsu ID to slug and images.                                        |
| [Last.FM](https://last.fm)                                            | Database | A music tracking site. Used for scrobble summary.                                                                                            |
| [MAL Heatmap](https://malheatmap.com)                                 | Add-on   | A simple heatmap of your MAL anime list.                                                                                                     |
| [nattadasu's AnimeApi relation](https://nttds.my.id/discord)          | Relation | A simple relation database of anime to several database sites, including MAL, AniList, and Kitsu. Used for anime relation.                   |
| [nattadasu/nekomimiDb](https://github.com/nattadasu/nekomimiDb)       | Database | A database site for nekomimi images. Used for random nekomimi image.                                                                         |
| [RAWG](https://rawg.io)                                               | Database | A database site for games. Used for search, information result, and images.                                                                  |
| [SIMKL](https://simkl.com)                                            | Database | A database site for anime. Used for TV-movie metadata, anime relations and images.                                                           |
| [Song.link](https://song.link)                                        | Relation | A relation database for music. Used for music relations.                                                                                     |
| [Spotify](https://spotify.com)                                        | Database | A music streaming site. Used for track, album, and artist information.                                                                       |
| [Trakt](https://trakt.tv)                                             | Relation | A database site for movies, TV shows, and anime. Used only for resolving category for relations to TMDB and TVDB.                            |
<!-- markdownlint-enable MD013 -->

## ✍️ Authors <a name = "authors"></a>

- [@nattadasu](https://github.com/nattadasu) - Idea & Initial work

See also the list of [contributors](https://github.com/nattadasu/ryuuRyuusei/contributors) who participated in this project.

## 🎉 Acknowledgements <a name = "acknowledgement"></a>

- Karasian, for creating the verification bot for The Newbie Club Discord server
- Lacrima, YubiYuub, and Mental Illness, for helping me with the bot
- [White Cat](https://whitecat.app/), for the ability to link MAL account to Discord account and profile can be invoked anywhere.
- And nearly all of the Discord bots with MAL functionalities, for inspiring me to create this bot... as most of bots didn't offer much information about the title compared to some (including this), smh.
- *And finally, a honorable mention to PowerShell, because it's literally my* *real first scripting language I learned, and because of it, I can create* *this bot in python... somehow, cough cough.*

[^1]: The random seed was generated using UUID4 and truncated to 32 bits (`pandas` couldn't able to get a sample using a seed above 32 bits unfortunately), and this seed generation happened ***everytime*** user invoked command. I can not guarantee the randomness as it is not the true random as in cryptographically secure random, but it's good enough that you should have hard time to get the same result twice in a row.
[^2]: This project is not affiliated with Crypton Future Media, Inc. or any of its subsidiaries.

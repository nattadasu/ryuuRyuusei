<!-- markdownlint-disable MD033 MD013 MD041 -->

<p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="https://cdn.discordapp.com/avatars/811887256368840744/20591f3bde09a33594eec07dc4a54ce9.webp" alt="Bot logo"></a>
</p>

<h3 align="center">Ryuuzaki Ryuusei</h3>

<p align="center"><img src="https://img.shields.io/badge/Interactions.py-4.3.4-blue?style=for-the-badge&logo=python">
<img src="https://img.shields.io/badge/Python-3.9_and_above-blue?style=for-the-badge&logo=python"></p>

---

<p align="center"> 🤖 A Discord Bot to verify MAL club members and MAL simple utility commands.
    <br>
</p>

## 🧐 About <a name = "about"></a>

Ryuuzaki Ryuusei is a Discord bot that can be used to verify MAL club members and MAL simple utility commands like user stats and anime lookup while it keeping simple and easy to use, also respecting users under GDPR, CCPA/CPRA, and other privacy laws.

The bot is fully powered by slash commands and is currently in alpha testing.

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
- [x] Privacy-friendly: no data is stored on the bot's server, except for the user's Discord ID and MAL username. See [Privacy Policy](docs/PRIVACY_POLICY.md) for more information.
- [x] Delete your data from the bot's database at any time as you wish using `/unregister` command.
- [x] Beautiful embed with thumbnail and footer.
- [x] Simple yet powerful anime and manga lookup.
  - [x] Accurate release date, adapted to your local timezone (based on MyAnimeList).
  - [x] External links (MAL, AniList, AniDB, Kitsu, SIMKL, IMDb, TMDB, Trakt, and more).
  - [x] A lot of information about the anime compared to competitors: synopsis, genres and themes, rating with total votes, and more!
  - [x] Know ID of the anime you want to search? Use `/anime info` command instantly!
- [x] Shows your birthday; including remaining days to your upcoming birthday (based on MyAnimeList).
- [x] Customizable Last.fm scrobble summary.
- [x] Export your data in JSON or Python dictionary format.
- [x] Experience the *"true"* randomness result on `/anime random` and `/random_nekomimi` commands![^1]
- [x] Self-hosting on your phone? No problem! Bot has been tested on Termux on Android 11.
- [x] ~~**100% Approved by Kagamine Len**[^2]~~

[^1]: The random seed was generated using UUID4 and truncated to 32 bits (`pandas` couldn't able to get a sample using a seed above 32 bits unfortunately), and this seed generation happened ***everytime*** user invoked command. I can not guarantee the randomness as it is not the true random as in cryptographically secure random, but it's good enough that you should have hard time to get the same result twice in a row.
[^2]: This project is not affiliated with Crypton Future Media, Inc. or any of its subsidiaries.

## 📣 Available Commands <a name = "commands"></a>

### Anime Commands

> Utilize MyAnimeList via Jikan

- `/anime info` - Get information about an anime using direct MyAnimeList ID
- `/anime random` - Get a random anime from MyAnimeList, powered by [AnimeApi](https://nttds.my.id/discord)
- `/anime relation` - Show external links for an anime, powered by [AnimeApi](https://nttds.my.id/discord) and SIMKL
- `/anime search` - Search for an anime, using AniList's search API

### Manga Commands

> Utilize AniList

- `/manga info` - Get information about a manga using direct AniList ID
- `/manga search` - Search for a manga

### Last.FM Integration

- `/lastfm` - Get your last.fm profile and the scrobble summary

### Data Control

- `/admin_register` - Register a user's MAL account to the bot (admin only), used for backup process if the user can't register their account
- `/admin_unregister` - Unregister a user's MAL account from the bot (admin only), used for backup process if the user can't unregister their account
- `/admin_verify` - Verify a user's MAL account to the server that host the bot (admin only), used for backup process if the user can't verify their account
- `/export_data` - Export your data from the bot in JSON or Python dictionary format
- `/profile` - Get your MAL profile, statistic available on extended view (passed from option/argument)
- `/register` - Register your MAL account to the bot
- `/unregister` - Unregister your MAL account from the bot
- `/verify` - Verify your MAL account to the server that host the bot (you may need to join the club first)
- `/whois` - Get information about a user, including their MAL account (if any)

### Miscellaneous Commands

- `/random_nekomimi` - Get a random nekomimi image from the database, powered by [nattadasu/nekomimiDb](https://github.com/nattadasu/nekomimiDb)
  - `/random_nekomimi bois` - Get a random male nekomimi image
  - `/random_nekomimi gurls` - Get a random female nekomimi image
  - `/random_nekomimi true_random` - *Harness the true power of having a random nekomimi image*

### Bot Commands

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

To install Ryuuzaki Ryuusei, follow these steps:

```bash
git clone https://github.com/nattadasu/ryuuRyuusei.git
cd ryuuRyuusei
pip install -r requirements.txt
```

> **Note**
> If you're using Termux, you may need to modify `pip` line to:
>
> ```bash
> MATHLIB="m" pip install -r requirements.txt
> ```

> **Note**
> You can also run `firstRun.py` to install all of required modules automatically.

Next, you need to do an initial setup for the bot. Run `firstRun.py` and let the bot create the required files and install dependencies that hosted in GitHub instead of PyPI:

```bash
python ./firstRun.py
```

Then, when `pip` finished installing all of required modules, copy `.env.example` to `.env` and fill the required fields.

```bash
cp .env.example .env
```

Finally, run the bot using `python` command:

```bash
python ./main.py
```

**Note**: You can also use `python3` instead of `python` if you have multiple versions of Python installed. By default (and also `firstRun.py` behavior), the bot will use `python3`/`python` that is currently in your `PATH` environment variable.

## ⛏️ Built Using <a name = "built_using"></a>

- [AniList](https://anilist.co) - A database site for anime and manga. Used for search, information result (manga only), and images.
- [interactions.py](https://github.com/interactions-py/interactions.py) - A Python library for Discord's slash commands. A backbone of the bot.
- [jikanpy](https://github.com/abhinavk99/jikanpy) - A Python wrapper for the unofficial MyAnimeList API, Jikan. Used for anime information, user profile, and anime search.
- [Kitsu](https://kitsu.io) - A database site for anime and manga. Used only for images and converting Kitsu ID to slug.
- [Last.FM](https://last.fm) - A music tracking site. Used for scrobble summary.
- [MAL Heatmap](https://malheatmap.com) - A simple heatmap of your MAL anime list.
- [nattadasu's AnimeApi relation](https://nttds.my.id/discord) - A simple relation database of anime to several database sites, including MAL, AniList, and Kitsu. Used for anime relation.
- [nattadasu/nekomimiDb](https://github.com/nattadasu/nekomimiDb) - A simple open-source image link database of 2D characters with cat ears with better sourcing (and maybe also better legality(?)). Used for random nekomimi image.
- [SIMKL](https://simkl.com) - A database site for TV shows, movies, and anime. Used for relations, and images.
- [Trakt](https://trakt.tv) - A database site for TV shows and movies. Used only for resolving category for relations to TMDB and TVDB.

## ✍️ Authors <a name = "authors"></a>

- [@nattadasu](https://github.com/nattadasu) - Idea & Initial work

See also the list of [contributors](https://github.com/nattadasu/ryuuRyuusei/contributors) who participated in this project.

## 🎉 Acknowledgements <a name = "acknowledgement"></a>

- Karasian, for creating the verification bot for The Newbie Club Discord server
- Lacrima, YubiYuub, and Mental Illness, for helping me with the bot
- [White Cat](https://whitecat.app/), for the ability to link MAL account to Discord account and profile can be invoked anywhere.
- And nearly all of the Discord bots with MAL functionalities, for inspiring me to create this bot... as most of bots didn't offer much information about the title compared to some (including this), smh.
- *And finally, a honorable mention to PowerShell, because it's literally my real first scripting language I learned, and because of it, I can create this bot in python... somehow, cough cough.*

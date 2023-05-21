<!-- markdownlint-disable MD033 MD013 MD041 -->

<p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="assets/logo.png" alt="Bot logo"></a>
</p>

<!-- omit in toc -->
<h2 align="center">Ryuuzaki Ryuusei</h2><br>

<p align="center"><img src="https://img.shields.io/badge/Interactions.py-5.0.0-blue?logo=python">
<img src="https://img.shields.io/badge/Python-3.10_and_above-blue?logo=python"><br>
<a href="https://app.deepsource.com/gh/nattadasu/ryuuRyuusei/?ref=repository-badge}" target="_blank"><img alt="DeepSource" title="DeepSource" src="https://app.deepsource.com/gh/nattadasu/ryuuRyuusei.svg/?label=active+issues&show_trend=true&token=e6p1rkAiFj4re6lheVEBPfd5"/></a>
<a href="https://app.deepsource.com/gh/nattadasu/ryuuRyuusei/?ref=repository-badge}" target="_blank"><img alt="DeepSource" title="DeepSource" src="https://app.deepsource.com/gh/nattadasu/ryuuRyuusei.svg/?label=resolved+issues&show_trend=true&token=e6p1rkAiFj4re6lheVEBPfd5"/></a>
<a href="https://app.codacy.com/gh/nattadasu/ryuuRyuusei/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade"><img src="https://app.codacy.com/project/badge/Grade/8109d97c7cca49ef9dbc96a82796ad66"/></a>
<a title="Crowdin" target="_blank" href="https://crowdin.com/project/ryuuRyuusei"><img src="https://badges.crowdin.net/ryuuRyuusei/localized.svg"></a></p>

---

<p align="center"> 🤖 A Title (Anime, Manga, Game, TV, Movie) Lookup and Member
Verificator Bot for Discord, With Privacy in Mind.
    <br>
</p>

<!-- markdownlint-enable MD013 -->

## 🧐 About <a name = "about"></a>

Ryuuzaki Ryuusei is a Discord bot that can be used to verify MAL club members
and advanced media title lookup (anime, manga, games, tv, movie) statically
while it keeping simple and easy to use, also respecting users under GDPR,
CCPA/CPRA, and other privacy laws.

The underlying bot frameworks are kinda heavily-typed, so it's might be a bit
resilient to breaking changes, even with 3rd party API wrappers that were
written in-house.

By inviting this bot to your server or using it, you agree to the
[Privacy Policy](PRIVACY.md) and [Terms of Service](TERMS_OF_SERVICE.md).

> **Warning**
>
> This bot is a rolling release bot, which means that the bot may not be stable
> and may have bugs. If you find any bugs, please report it to GitHub Issues or
> on the support server.

## 🎈 Usage <a name = "usage"></a>

To use the bot, invite it to your server using this link:

[![Shield](https://img.shields.io/badge/Invite%20to%20your%20server-7289DA?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com/api/oauth2/authorize?client_id=811887256368840744&permissions=274878221376&scope=bot%20applications.commands)

Next, go to the channel you want to use the bot in and type `/` to see the list
of available commands.

All data invoked from `/register` will be stored in
[database.csv](database/database.csv), user is able to delete their data by
using `/unregister` command. Most commands can be used without `/register`
command, although it may limit your experience using it.

If you have any questions, feel free to join the
[support server](https://nttds.my.id/discord) and ask there.

## 🚀 Features <a name = "features"></a>

> This also will be our to-do list for the bot. :3

- [x] MAL account verification (only for self-hosted bot).
- [x] Privacy-friendly: no data is stored on the bot's server, except for the
      user's Discord ID and MAL username. See [Privacy Policy](PRIVACY.md) for
      more information.
- [x] Delete your data from the bot's database at any time as you wish using
      `/unregister` command.
- [x] Beautiful embed with thumbnail and footer.
- [x] Simple yet powerful anime, manga, and game lookup.
  - [x] Ability to select search result from multiple results rather than
        automatically selecting the first result. (I'm looking at you, Nadeko)
  - [x] Accurate release date, adapted to your local timezone (based on
        MyAnimeList).
  - [x] External links (MAL, AniList, AniDB, Kitsu, SIMKL, IMDb, TMDB, Trakt,
        and more).
  - [x] A lot of information about the media compared to competitors: synopsis,
        genres and themes, rating with total votes, and more!
  - [x] Know ID of the title you want to search? Use `/relations` command group
        instantly!
- [x] Shows your birthday; including remaining days to your upcoming birthday
      (based on MyAnimeList user profile).
- [x] Customizable Last.fm scrobble summary.
- [x] Export your data in JSON or Python dictionary format.
- [x] Experience the *"true"* randomness result on `/anime random` and
      `/random_nekomimi` commands![^1]
- [x] Self-hosting on your phone? No problem! Bot has been tested on Termux on
      Android 11.
- [ ] Does not support dynamic airing reminder. LiveChart + RSS bot is a good
      alternative.
- [ ] Does not support updating your list to MyAnimeList. You can use
      [White Cat](https://whitecat.app) instead.
- [ ] Currently does not support character and cast lookup as it can be really
      complicated if you're using multiple platforms.

[^1]: The random seed was generated using UUID4 and truncated to 32 bits (`pandas` couldn't able to get a sample using a seed above 32 bits unfortunately), and this seed generation happened ***everytime*** user invoked command. I can not guarantee the randomness as it is not the true random as in cryptographically secure random, but it's good enough that you should have hard time to get the same result twice in a row.

## 📣 Available Commands <a name = "commands"></a>

> **Note**
>
> Since you're accessing this rewrite branch of the bot...
> Any command that has ⌚ as prefix means that the command is not currently
> available during heavy rewrite. It will be available soon, well... hopefully.

### Anime Commands

> Utilize MyAnimeList via Jikan

- `/anime info` - Get information about an anime using direct MyAnimeList ID
- `/anime search` - Search for an anime, using AniList's search API

### Manga Commands

> Utilize AniList

- ⌚ `/manga info` - Get information about a manga using direct AniList ID
- ⌚ `/manga search` - Search for a manga

### Game Commands

> Utilize RAWG

- ⌚ `/games info` - Get information about a game using direct RAWG ID
- ⌚ `/games search` - Search for a game

### TV and Movie Commands

> Utilize SIMKL for Metadata and TMDB for NSFW check

- ⌚ `/movie info` - Get information about a movie using direct SIMKL ID
- ⌚ `/movie search` - Search for a movie
- ⌚ `/tv info` - Get information about a TV show using direct SIMKL ID
- ⌚ `/tv search` - Search for a TV show

### Music Commands

> Utilize Spotify

- ⌚ `/music album info` - Get information about an album using direct Spotify ID
- ⌚ `/music album search` - Search for an album
- ⌚ `/music artist info` - Get information about an artist using direct Spotify ID
- ⌚ `/music artist search` - Search for an artist
- ⌚ `/music track info` - Get information about a track using direct Spotify ID
- ⌚ `/music track search` - Search for a track

### External Link Relation Command

> Utilize nattadasu's AnimeAPI for video type, AniList for manga, and Song.link
> for music

- ⌚ `/relations manga` - Get external link relation for a manga, limited to
  AniList, MyAnimeList, and Shikimori
- ⌚ `/relations music album` - Get external link relation for an album
- ⌚ `/relations music track` - Get external link relation for a track
- ⌚ `/relations shows` - Get external link relation for an anime, TV, or movie

### Profile Lookup Commands

> Shows your profile information from supported platforms.

- ⌚ `/profile anilist` - Get your AniList profile
- `/profile discord` - Get your Discord profile
- `/profile lastfm` - Get your Last.fm profile
- ⌚ `/profile myanimelist` - Get your MyAnimeList profile
- ⌚ `/whoami` - Show stored information and settings about you on the bot
  graphically and interactively.

### Data Control

- ⌚ `/export data` - Export your data from the bot in JSON
- ⌚ `/register` - Register your MAL account to the bot
- ⌚ `/unregister` - Unregister your MAL account and drops your settings from the
  bot
- ⌚ `/verify` - Verify your MAL account to the server that host the bot (you may
  need to join the club first)

### Settings Commands

#### User Settings

- `/usersettings language list` - List all available languages for the bot
  response
- `/usersettings language set` - Set your preferred language for the bot
  response

#### Server Settings

- `/serversettings language set` - Set your preferred language for the bot
  response
- ⌚ `/serversettings member register` - Register member's MAL account to the bot,
  used when user can't invoke `/register`
- ⌚ `/serversettings member unregister` - Unregister member's MAL account from the
  bot, used when user can't invoke `/unregister`
- ⌚ `/serversettings member verify` - Verify member's MAL account to the server
  that host the bot, used when user can't invoke `/verify`

### Randomization Commands

> Collection of commands that returns random result.

- `/random anime` - Get a random anime from MyAnimeList, powered by
  [AnimeApi](https://nttds.my.id/discord)
- ⌚ `/random movie` - Get a random movie from SIMKL
- `/random nekomimi` - Get a random nekomimi image from nattadasu's nekomimiDb
  - `/random nekomimi boy` - Show an image of a boy in nekomimi
  - `/random nekomimi girl` - Show an image of a girl in nekomimi
  - `/random nekomimi randomize` - Show an image of a character in nekomimi
    regardless the gender.
- `/random number` - Get a random number from Random.org
- `/random string` - Get a random string from Random.org
- ⌚ `/random tv` - Get a random TV show from SIMKL

### Utility Commands

> Collection of commands that are (might be) useful for everyday use.

- ⌚ `/utilities avatar` - Get a user's avatar
- `/utilities base64` - Encode or decode a string to or from Base64
- `/utilities color` - Get a color's information
- `/utilities math` - Evaluate a mathematical expression
- `/utilities qrcode` - Generate a QR code from a string
- `/utilities snowflake` - Get a snowflake's information

### Commons Bot Commands

- `/about` - Get information about the bot
- `/invite` - Get the bot's invite link
- `/ping` - Check the bot latency
- `/privacy` - Get information about the bot's privacy policy
- `/support` - Support the bot by donating or contributing to the bot's
  development

## 🏁 Getting Started <a name = "getting_started"></a>

### Prerequisites

Before proceeding, ensure that you have installed dependencies installed on your
system:

- Git
- Python (version 3.10 or higher)

You can verify your Python version by running `python --version` or
`python3 --version` in your terminal/command prompt.

Also, you might need Discord account and Discord Bot Token.

### Cloning the Repository

1. Clone the `ryuuRyuusei` repository by executing the following command:

   ```bash
   git clone https://github.com/nattadasu/ryuuRyuusei
   ```

2. Change your current working directory to the cloned repository:

   ```bash
   cd ryuuRyuusei
   ```

### Setting up a Virtual Environment

1. Create a virtual environment to isolate the bot's dependencies:

   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment based on your operating system and shell:

   - **Windows (PowerShell)**:

     ```powershell
     & .\venv\Scripts\Activate.ps1
     ```

   - **Windows (Command Prompt)**:

     ```batch
     venv\Scripts\activate.bat
     ```

   - **Unix-like Systems (bash)**:

     ```bash
     source venv/bin/activate
     ```

   If you encounter any issues activating the virtual environment, make sure you
   have the appropriate permissions (root access might be required on Unix-like
   systems).

### Installing Dependencies

Before running the bot, you need to install its dependencies. Execute the
following command:

```bash
pip install aiohttp langcodes pyyaml pandas
```

- If you are using Termux on Android, add `MATHLIB="m"` before the `pip`
  command, as there's known issue installing `pandas` dependencies:

  ```bash
  MATHLIB="m" pip install aiohttp langcodes pyyaml pandas
  ```

### Running the Bot

1. Run the initial setup script by executing the following command:

   ```bash
   python firstRun.py
   ```

   The following script will try to install the required dependencies, updating
   them, initialize database, download additional featured data, converting
   i18n files from YAML to JSON, and copy `.env.example` file as `.env`.

2. If the `.env` file does not exist, follow this step, otherwise skip:

   - Copy the `.env.example` file to create a new `.env` file:

     ```bash
     cp .env.example .env
     ```

3. Fill in the required credentials in the `.env` file.

4. Finally, execute the following command to run the bot:

   ```bash
   python main.py
   ```

Congratulations! You have successfully set up and launched the Discord bot.

## ⛏️ Built Using <a name = "built_using"></a>

<!-- markdownlint-disable MD013 -->
| Service/Package/Module Name                                         | FOSS?        | Scope                              | Type              | Description                                                                                 |
| ------------------------------------------------------------------- | ------------ | ---------------------------------- | ----------------- | ------------------------------------------------------------------------------------------- |
| [AniList](https://anilist.co/)                                      | -            | Anime, Censorship, Manga, Relation | Database          | Mainly used for Manga commands, anime for searching                                         |
| [AnimeAPI](https://github.com/nattadasu/animeApi)                   | AGPL-3.0     | Anime, Random, Relation            | Relation          | Linking ID from a database to another database                                              |
| [emoji](https://pypi.org/project/emoji/)                            | MIT          | Language, Utility                  | Module            | Used for converting emoji to Unicode                                                        |
| [goQr](https://goqr.me/api)                                         | -            | Utility                            | API               | Used for generating QR code                                                                 |
| [Interactions.py](https://pypi.org/project/discord-py-interactions) | MIT          | Base                               | Wrapper           | The backend of this bot!                                                                    |
| [Is It Down Right Now?](https://isitdownrightnow.com/)              | -            | Utility                            | API               | Used for checking if a website is down                                                      |
| [Jikan](https://jikan.moe/)                                         | MIT          | Anime, Profile, Verify             | 3rd Party MAL API | Used for showing anime information, verify user, and show user's profile                    |
| [Kitsu](https://kitsu.io/)                                          | Apache-2.0   | Anime                              | Database          | Used for adding additional information to anime information, mainly background and poster   |
| [langcodes](https://pypi.org/project/langcodes/)                    | MIT          | Language                           | Wrapper           | Used for getting language name from language code                                           |
| [Last.fm](https://www.last.fm/)                                     | -            | Profile                            | Database          | Used for getting user's last.fm profile and scrobble summary                                |
| [MyAnimeList](https://myanimelist.net/)                             | -            | Anime                              | Database          | Search and show anime information                                                           |
| [nattadasu/nekomimiDb](https://github.com/nattadasu/nekomimiDb)     | MIT          | Random                             | Database          | Used for getting random nekomimi image                                                      |
| [PronounDB](https://pronoundb.org/)                                 | BSD-3-Clause | Profile                            | Database          | Used for getting user's pronouns                                                            |
| [Random.org](https://www.random.org/)                               | -            | Random                             | Generator         | Used for generating (true) random number and string                                         |
| [Rawg](https://rawg.io/)                                            | -            | Game                               | Database          | Used for searching and showing game information                                             |
| [SIMKL](https://simkl.com/)                                         | -            | Anime, Movie, Show, Relation       | Database          | Used for searching and showing movie and show information, anime for additional information |
| [The Color API](https://github.com/andjosh/thecolorapi)             | ?            | Utility                            | API               | Used for getting color information                                                          |
| [The Movie Database](https://www.themoviedb.org/)                   | -            | Censorship                         | Database          | Used for getting movie and show censorship information                                      |
| [Trakt](https://trakt.tv/)                                          | -            | Relation                           | Database          | Used for linking anime, movie, and show IMDb ID (provided by SIMKL and AniAPI) to Trakt ID  |
<!-- markdownlint-enable MD013 -->

## ✍️ Authors <a name = "authors"></a>

- [@nattadasu](https://github.com/nattadasu) - Idea & Initial work

See also the list of [contributors](https://github.com/nattadasu/ryuuRyuusei/contributors)
who participated in this project.

## 🎉 Acknowledgements <a name = "acknowledgement"></a>

- Karasian, for creating the verification bot for The Newbie Club Discord server
- Lacrima, YubiYuub, and Mental Illness, for helping me with the bot
- [White Cat](https://whitecat.app/), for the ability to link MAL account to
  Discord account and profile can be invoked anywhere.
- And nearly all of the Discord bots with MAL functionalities, for inspiring me
  to create this bot... as most of bots didn't offer much information about the
  title compared to some (including this), smh.
- *And finally, a honorable mention to PowerShell, because it's literally my*
  *real first scripting language I learned, and because of it, I can create*
  *this bot in python... somehow, cough cough.*

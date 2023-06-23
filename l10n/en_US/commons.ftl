# Ryuuzaki Ryuusei Internationalization File in Fluent Language Syntax

-brand-name = Ryuuzaki Ryuusei
    .gender = male
       .age = 18

### About Bot Command
about =
    {-brand-name} is a rolling release Discord bot that uses interactions.py and
    Python to offer a variety of features and commands for Discord users. You can
    look up your profile from Discord, AniList, Shikimori, MyAnimeList, and Last.fm
    and customize your summary for each platform. You can also search for anime,
    manga, games, TV shows, and movies from platforms like MyAnimeList, AniList,
    SIMKL, Spotify, and more. You can also export your data in different formats
    and enjoy true randomness with some commands.

    If you want to know more about {-brand-name}, you can visit the official
    repository at {$repository}.

    Authors: {$authors}

    Bot version, in Git commit hash: [{$version}]({$commit})

### Ping Command
ping-title = Ping
ping-description = Pinging.... Please wait till I get the results from my tests!
pong-title = Pong!
pong-description = Here's the results from my tests!
bot-title = Bot
bot-description =
    Compares message timestamp to current timestamp, might not reliable as
    benchmark per se
websocket-title = Websocket API
websocket-description = Discord Websocket API latency
database-title = Database Read
database-description = Read time from CSV database
language-title = Language Load
language-description = Load time from language file
python-time = Python Time
python-description = Time taken to run Python code based on CPU clock speed
uptime-title = Uptime
uptime-description = Bot has been running for {$uptime}

### Invite Command
invite-title = Thanks for the interest to invite me!
invite-button = Invite Me!
invite-server = Join the Support Server
invite-description =
    You can invite me to your server by clicking {invite-button} button below.

    If you have any questions or suggestions, you can join the support server by
    clicking {invite-server} button below.
invite-access-title = Required Permissions/Access
invite-access-description =
    I need the following permissions to work properly:

    - Read Messages
    - Send Messages
    - Send Messages in Threads
    - Embed Links
    - Attach Files
    - Use External Emojis
    - Add Reactions
invite-scope-title = Required Scopes
invite-scope-description =
    I need the following scopes to work properly:

    - `bot`
    - `applications.commands`

### Privacy Command
privacy-title = Privacy Policy for {-brand-name} in a Nutshell
privacy-description =
    Hello and thank you for your interest to read this tl;dr version of
    Privacy Policy.

    In this message we shortly briefing which content we collect, store, and
    use, including what third party services we used for bot to function as
    expected. You can read the full version of
    [Privacy Policy here at anytime you wish]({$privacy-url}).

    ### We collect, store, and use following data
    - Discord: username, discriminator, user snowflake ID, joined date,
    guild/server ID of registration, server name, date of registration, user
    referral (if any)
    - MyAnimeList: username, user ID, joined date

    ### We shared limited personal information about you to 3rd Party:
    This is required for the bot to function as expected, with the following
    services:
    Discord, Last.FM, MAL Heatmap, MyAnimeList

    ### We cached data for limited features of the bot:
    Used to reduce the amount of API calls to 3rd party services, and to
    reduce the amount of time to process the data and no information tied to
    you.

    ### We do not collect, however, following data:
    Any logs of messages sent by system about you under any circumstances.
    Logging of messages only occurs when you invoked general commands (such as
    `/help`, `/anime`, `/manga`, etc.) and during the bot's development
    process. Maintenance will announced in the Bot status channel in Support
    Server and Bot Activity.

    Data stored locally to Data Maintainer's (read: owner) server/machine of
    this bot as CSV. To read your profile that we've collected, type
    `/export_data` following your username.

    As user, you have right to access, know, data portability, modify/rectify,
    delete, restrict, limit, opt-out, and/or withdraw your consent to use your
    data.

    For any contact information, type `/about`.

support-title = Support {-brand-name}'s Development
support-description =
    Thanks for your interest in supporting me!

    You can support me on [Ko-Fi]({$kofi}), [PayPal]({$paypal}}),
    [Patreon]({$patreon}),or [GitHub Sponsors]({$github}).

    For Indonesian users, you can use [Trakteer]({$trakteer}) or
    [Saweria]({$saweria}).

    Or, are you a developer? You can contribute to the bot's code on
    [GitHub]({$repo}).

    If you have any questions (or more payment channels), please join my
    [support server]({$support})!

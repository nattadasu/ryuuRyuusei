<!-- cSpell:words Ryuuzaki Ryuusei nattadasu atsine geolocation -->

# Ryuuzaki Ryuusei Privacy Policy

|                  |                |
| ---------------- | -------------- |
| **Effective**    | April 1, 2023  |
| **Last Updated** | March 17, 2023 |

Hello, and welcome to Ryuuzaki Ryuusei's Privacy Policy. This Privacy Policy
explains how we collect, use, store, protect, and share your personal
information through our services.

[nattadasu][gh-nattadasu] is the data controller of your personal information,
data were collected under Indonesia jurisdiction while respecting
[EU General Data Protection Regulation][gdpr] and
[California Consumer Privacy Act][ccpa]. If you have any questions or concerns
about this Privacy Policy, please contact data controller in the
[About Us](#about-us) section.

Although we encourage you to read this Privacy Policy in full, here is a summary
of what we collect, store, and use:

* **We collect personal information tied about you**, with your consent, the
  following data:
  * [Discord][discord]: username, discriminator, user snowflake ID, joined date,
    guild/server ID of registration, server name, date of registration, user
    referral (if any)
  * [MyAnimeList][mal]: username, user ID, joined date
* **We share limited personal information about you and/or other**, required for
  the bot to function as expected, with the following services:
  > **Warning**
  >
  > Although we do not collect, store, or use any logs of messages sent by
  > system about you under any circumstances, the following services may collect
  > and store information you have provided to them.
  >
  > You can read their privacy policy for more information, and you can opt-out
  > from their services by deleting your account from the service.
  * [MyAnimeList][mal] (via [Jikan][jikan]): MyAnimeList Username
  * [Last.FM][lastfm]: Last.FM Username
  * [MAL-Heatmap][malh]: MyAnimeList Username
  * [Discord][discord]: Message Author Identifier
* **We store information for caching**. No information is being transmitted
  about you than bot's IP address and/or query request. We used the following
  services for caching:
  * [AniList][al]: Title information
  * [AnimeAPI][aniapi]: ID relation mapping
  * [MyAnimeList][mal] (via [Jikan][jikan]): Title information
  * [SIMKL][simkl]: Title information
  * [The Movie Database][tmdb]: Title information
  * [Trakt][trakt]: Title information
* **We do not collect, store, or use any logs of messages sent by system about
  you under any circumstances**. Logging of messages only occurs when you
  invoked general commands (such as `/help`, `/anime`, `/manga`, etc.) and
  during the bot's development process. Maintenance will announced in the Bot
  status channel in Support Server and Bot Activity.

## Definitions

* **Ryuuzaki Ryuusei/Bot/System/Service** is a software that is used to provide
  a service to you.
* **Data Controller** is a person or organization that determines the purposes
  and means of the processing of Personal Information.
* **We/Us/Our/Owner** refers to [nattadasu][gh-nattadasu], the Data Controller.

---

* **You/Author/User**, unless otherwise specified, refers to a person who
  invoked the bot command.
* **Discriminator** is a unique number that is assigned to each user on Discord.
* **Personal Information** is any information that can be used to identify you,
  such as your name, email address, or user identifier.
* **Sensitive Personal Information** is a specific subset of personal
  information that includes certain government  (such as social security
  numbers); an account log-in, financial account, debit card, or credit card
  number with any required security code, password, or credentials allowing
  access to an account; precise geolocation; contents of mail, email, and text
  messages; genetic data; biometric data; information processed to identify a
  consumer; information concerning a consumer’s health, sex life, or sexual
  orientation; or information about racial or ethnic origin, religious or
  philosophical beliefs, or union membership.
* **Server/Guild** is a Discord digital space made up of different types of
  channels that users can join and interact with each other.
* **Title**, unless otherwise specified, refers to a media content, such as
  anime, manga, TV, movie, music, etc.
* **User Referral** is a user who referred or added you to the bot through admin
  commands.

## About Us

Ryuuzaki Ryuusei is a Discord bot that is developed by [nattadasu][gh-nattadasu]
which aims better privacy for title
(anime, manga, tv, movie, music) lookup.

For inquiries, please contact Data Controller at:

```text
hello [atsine] nattadasu [dot] my [dot] id
```

## User Consent

By using Ryuuzaki Ryuusei, you consent to the collection, use, storage, and
sharing of your limited personal information as described in this Privacy
Policy.

## User Data Collection and Usage

Ryuuzaki Ryuusei collects the following data, and uses it to provide
functionality, under User's consent:

### Discord: User

Ryuuzaki Ryuusei collects Discord User data, such as username, discriminator,
User snowflake ID, joined date, guild/server ID of registration, server name,
date of registration, and user referral (if any).

This data is used to provide the following functionality:

* `/export_data` command
* `/profile` command
* `/register` command
* `/unregister` command
* `/whois` command

### MyAnimeList: User

Similar to Discord, Ryuuzaki Ryuusei collects MyAnimeList User data, such as
username, User ID, and joined date.

This data is used to provide the following functionality:

* `/export_data` command
* `/profile` command
* `/register` command
* `/whois` command

## User Data Sharing

Ryuuzaki Ryuusei shares limited personal information about you and/or other,
required for the bot to function as expected.

User may opt-out from the following services by deleting their account from the
service listed below and/or by deleting their data from the bot.

### MyAnimeList: Global

Bot shares MyAnimeList username with [Jikan][jikan], which is a third party
software (API) to access [MyAnimeList][mal] to retrieve information about User's
profile. The information is only used to provide information in `/profile`,
`/admin_register`, `/register`, and `/verify` commands.

### Last.FM

Bot shares Last.FM username with [Last.FM][lastfm] to retrieve information about
User's profile and recent tracks. The information is only used to provide
information in `/lastfm` command.

### MAL-Heatmap

Bot shares MyAnimeList username with [MAL-Heatmap][malh] to retrieve information
about User's history in visualized heatmap format. The information is only used
to provide information in `/profile` command.

### Discord: Global

Bot utilize Discord to get message author identifier to retrieve information
about User's profile and write command actor for server audit log. The
information is used to provide the following functionality:

* `/admin_register` command
* `/admin_verify` actor
* `/profile` command
* `/register` command
* `/unregister` command
* `/verify` command
* `/whois` command

## Data Caching

Ryuuzaki Ryuusei stores information for caching, this feature is used to reduce
the number of requests to external services, and to reduce the amount of time
needed to retrieve information.

Only information related to a Title is being cached, and no information is being
transmitted about you than Bot's IP address and/or query request.

This data is used to provide the following functionality:

* `/anime` commands group
* `/manga` commands group

Services that are being used for caching:

* [AniList][al]: Title information
* [AnimeAPI][aniapi]: ID relation mapping
* [MyAnimeList][mal] (via [Jikan][jikan]): Title information
* [SIMKL][simkl]: Title information
* [The Movie Database][tmdb]: Title information
* [Trakt][trakt]: Title information

## Data Logging

Ryuuzaki Ryuusei does not log any information related to you. Logging is only
enabled during development, bug fix, and testing, limited to general information
such as bot startup, command execution, API process and error, and will be
removed once the bot is ready for production.

Bot maintenance and development is done by Data Controller, and user will be
informed/noticed if logging is enabled by Support Server announcement and
Bot Activity status.

## Access to User Data

User can access their data by utilizing `/export_data` command, which will
generate a JSON file containing all the data that Bot has collected about User.

User also able to read information stored in bot interactively by utilizing
`/whois` command.

Data is stored in a database written in CSV ("Comma Separated Value"), and is
only accessible by the Data Controller.

## User Rights

You have the following rights under the
[EU General Data Protection Regulation][gdpr] and
[California Consumer Privacy Act][ccpa] as listed below:

### Right to Opt-Out

As Bot does not have ability to share your personal information with third
parties for advertising purposes, this right applies globally.

However, if you wish to remove access to your data using Bot, please utilize
`/unregister` command and remove bot from your server.

### Right to Non-Discrimination

You have the right to not be discriminated against for exercising any of your
rights.

### Right to Access, Know, and Data Portability

You have the right to access your personal information. If you wish to exercise
this right, please utilize `/export_data` command.

To see information about your data interactively, please utilize `/whois`
command.

### Right to Modify, Rectify, Delete, or Restrict Processing

You have the right to modify, rectify, delete, or restrict processing of your
personal information. If you wish to exercise this right, please utilize
`/unregister` command. To modify your data, please utilize `/register` command.

However, if the bot unable to modify your data automatically, please contact
Data Controller in the [About Us](#about-us) section.

### Right to Limit

You have the right to limit processing of your personal information. If you wish
to exercise this right, please contact Data Controller in the
[About Us](#about-us) section.

### Right to Stop Processing on Your Server

You have the right stop processing of information passed to the bot. If you wish
to exercise this right, please contact Data Controller in the
[About Us](#about-us) section to remove all data related to your server, this
will includes members that registered to the bot on your server.

Additionally, you can also remove the bot from your server, which will remove
functionality of the bot on your server.

## Changes to this Privacy Policy

We may update this Privacy Policy from time to time. We will notify you of any
changes by posting the new Privacy Policy on this page and announcing the change
on our Discord server.

<!-- References -->
[al]: https://anilist.co
[aniapi]: https://aniapi.nattadasu.my.id
[discord]: https://discord.com
[gh-nattadasu]: https://github.com/nattadasu
[gdpr]: https://gdpr.eu
[ccpa]: https://www.oag.ca.gov/privacy/ccpa
[jikan]: https://jikan.moe/
[lastfm]: https://last.fm
[mal]: https://myanimelist.net
[malh]: https://malheatmap.com
[simkl]: https://simkl.com
[tmdb]: https://www.themoviedb.org
[trakt]: https://trakt.tv

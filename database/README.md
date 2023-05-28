# `database` directory: where you can smell your money burning from far away

This directory contains the database files for the bot. It contains user data,
other related 1st party data, and server configuration data.

> **Note**
>
> For anyone who wanted to self-host the bot, please read below:
>
> As data maintainer, you are responsible for maintaining the data in this
> directory. Any data loss, leaks, or corruption is your responsibility, and
> I do not liable for any of those, as stated in the [LICENSE](../LICENSE),
> [Terms of Service](../TERMS_OF_SERVICE.md), and
> [Privacy Policy](../PRIVACY_POLICY.md).
>
> Well, I guess [LICENSE](../LICENSE) enough to cover this, as ToS and Privacy
> Policy are written for source bot only, and you can easily modify them to
> suit your needs.

## What is the purpose of this directory?

Well, to store the data, of course.

## What is the purpose of the data in this directory?

*could you st...* well, as stated above, this directory contains the data for the
bot.

## Well then, what kind of data that is stored in this directory?

...really?

## Why the database is stored in CSV format?

Skill issue. I wanted to integrate serverless database like Xata or MongoDB,
but I found several issues during testing, like very slow response time, or
didn't work at all.

## Why won't the bot encrypt the database?

It'd take a while to encrypt and decrypt the database from my understanding,
and if I can encrypt the database, why don't I integrate full-heck SQL database
instead for better performance and maybe better security?

## What files I should expect in this directory?

* `database.csv`

  Main database file. It contains registered user data

* `mal.csv`

  List of known anime on MyAnimeList, grabbed from AnimeAPI's
  MyAnimeList array endpoint. used for random anime command

* `member.csv`

  List of user settings, separated from `database.csv` to allow
  unregistered users to add their settings on the bot

* `nekomimiDb.tsv`

  From [nattadasu/nekomimiDb][nekomimiDb], contains list of
  url to character with nekomimi images, as well the attribution of the
  artwork

* `server.csv`

  List of settings for each server the bot is in, set by server admins

Note that this folder is not tracked by Git, so you won't see any of those
files in the repository.

And also, those list is not definitive, and may change in the future.

## How to use the database?

Use pandas, set delimiter as `\t`, encoding as `utf-8`.

[nekomimiDb]: https://github.com/nattadasu/nekomimiDb

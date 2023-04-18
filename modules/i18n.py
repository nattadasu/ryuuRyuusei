"""# Internationalization Bot Module

All language files are stored in the i18n folder. Strings to change and view languages must be in English."""


import csv
from json import load
from json import loads as jlo

import pandas as pd
from fuzzywuzzy import fuzz
from interactions import Client, Embed, EmbedField, InteractionContext
from interactions.ext.paginators import Paginator

from modules.const import LANGUAGE_CODE


def lang(code: str, useRaw: bool = False) -> dict:
    """Get the language strings for a given language code"""
    try:
        with open(f"i18n/{code}.json", "r", encoding="utf-8") as f:
            data = jlo(f.read())
            if useRaw:
                return data
            else:
                return data['strings']
    except FileNotFoundError:
        return lang(LANGUAGE_CODE)


def readUserLang(ctx) -> str:
    """Read the user's language preference from the database"""
    user_df = pd.read_csv("database/member.csv", sep="\t")

    # find the row in the user DataFrame that matches the user's ID
    user_row = user_df.loc[user_df["discordId"] == ctx.author.id]

    # check if a match was found and return the language if it was
    if len(user_row) > 0:
        return user_row["language"].iloc[0]

    try:
        with open("database/server.csv", "r", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter="\t")
            next(reader)  # skip header row
            for row in reader:
                if row[0] == str(ctx.guild.id):
                    language = row[1]
                    break
            else:
                language = LANGUAGE_CODE
    except:
        language = LANGUAGE_CODE

    return language


async def paginateLanguage(bot: Client, ctx: InteractionContext) -> None:
    """Paginate the language list"""
    with open("i18n/_index.json", "r") as f:
        langs = jlo(f.read())
    pages = []
    for i in range(0, len(langs), 15):
        paged = []
        for lang in langs[i:i+15]:
            flag = lang['code'].split('_')[1].lower()
            match flag:
                case "sp":
                    flag = "rs"
                case _:
                    flag = flag
            paged += [EmbedField(
                name=f":flag_{flag}: `{lang['code']}` - {lang['name']}",
                value=f"{lang['native']}",
                inline=True
            )]
        pages += [Embed(
            title="Languages",
            description="List of all available languages.\nUse `/usersettings language set code:<code>` by replacing `<code>` with the language code (for example `en_US`) to change your language.\n\nIf you want to contribute, visit [Crowdin page](https://crowdin.com/project/ryuuRyuusei).",
            color=0x996422,
            fields=paged,
        )]
    pagin = Paginator.create_from_embeds(bot, *pages, timeout=60)
    await pagin.send(ctx)


def searchLanguage(query: str) -> list[dict]:
    with open('i18n/_index.json') as f:
        data = load(f)
    results = []
    for item in data:
        name_ratio = fuzz.token_set_ratio(query, item['name'])
        native_ratio = fuzz.token_set_ratio(query, item['native'])
        dialect_ratio = fuzz.token_set_ratio(query, item['dialect'])
        max_ratio = max(name_ratio, native_ratio, dialect_ratio)
        if max_ratio >= 70:  # minimum similarity threshold of 70%
            results.append(item)
    return results


def checkLangExist(code: str) -> bool:
    """Check if a language exists"""
    with open("i18n/_index.json", "r") as f:
        langs = jlo(f.read())
    for lang in langs:
        if lang["code"] == code:
            return True
    return False


async def setLanguage(code: str, ctx: InteractionContext, isGuild: bool = False) -> None:
    """Set the user's/guild's language preference"""
    if isGuild is True:
        if checkLangExist(code) is False:
            raise Exception(
                "Language not found, recheck the spelling and try again")
        # check if guild is already in database
        try:
            df = pd.read_csv("database/server.csv", sep="\t")
            if df.query(f"serverId == {ctx.guild.id}").empty:
                df = pd.DataFrame([[ctx.guild.id, code]], columns=[
                                  "serverId", "language"])
                df = df.append(df, ignore_index=True)
                df.to_csv("database/server.csv", sep="\t", index=False)
            else:
                # if it is, update it
                df.loc[df["serverId"] == ctx.guild.id, "language"] = code
                df.to_csv("database/server.csv", sep="\t", index=False)
        except:
            # if the database doesn't exist, create it
            with open("database/server.csv", "w", newline="") as csvfile:
                writer = csv.writer(csvfile, delimiter="\t")
                writer.writerow(["serverId", "language"])
                writer.writerow([ctx.guild.id, code])
    else:
        if checkLangExist(code) is False:
            raise Exception(
                "Language not found, recheck the spelling and try again")

        try:
            df = pd.read_csv("database/member.csv", sep="\t",
                             encoding="utf-8", dtype={"discordId": str})

            if df.query(f"discordId == '{str(ctx.author.id)}'").empty:
                df = pd.DataFrame([[str(ctx.author.id), code]], columns=[
                                  "discordId", "language"])
                df = df.append(df, ignore_index=True)
                df.to_csv("database/member.csv", sep="\t", index=False)
            else:
                # if it is, update it
                df.loc[df["discordId"] == str(
                    ctx.author.id), "language"] = f"{code}"
                df.to_csv("database/member.csv", sep="\t", index=False)
        except:
            # if the database doesn't exist, create it
            with open("database/member.csv", "w", newline="") as csvfile:
                writer = csv.writer(csvfile, delimiter="\t")
                writer.writerow(["discordId", "language"])
                writer.writerow([str(ctx.author.id), code])

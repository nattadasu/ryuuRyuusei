from datetime import datetime, timezone
from typing import Literal

import cutlet
import interactions as ipy
import pykakasi

from modules.commons import (generate_commons_except_embed, sanitize_markdown,
                             save_traceback_to_file)


class NihongoCog(ipy.Extension):
    """Extension for Japanese tools"""

    nihongo_head = ipy.SlashCommand(
        name="nihongo",
        description="Japanese tools",
        cooldown=ipy.Cooldown(
            cooldown_bucket=ipy.Buckets.CHANNEL,
            rate=1,
            interval=60,
        ),
    )

    @nihongo_head.subcommand(
        sub_cmd_name="romajinize",
        sub_cmd_description="Convert Japanese scripts to Romaji/Latin script",
        options=[
            ipy.SlashCommandOption(
                name="source",
                description="The source text",
                type=ipy.OptionType.STRING,
                required=True,
            ),
            ipy.SlashCommandOption(
                name="spelling_type",
                description="The spelling type",
                type=ipy.OptionType.STRING,
                required=False,
                choices=[
                    ipy.SlashCommandChoice(
                        name="Modified Hepburn (default)",
                        value="hepburn",
                    ),
                    ipy.SlashCommandChoice(
                        name="Kunreisiki",
                        value="kunrei",
                    ),
                    ipy.SlashCommandChoice(
                        name="Nihonsiki",
                        value="nihon",
                    ),
                    ipy.SlashCommandChoice(
                        name="Passport",
                        value="passport",
                    ),
                ]
            ),
            ipy.SlashCommandOption(
                name="use_foreign",
                description="Use foreign spelling, default is true",
                type=ipy.OptionType.BOOLEAN,
                required=False,
            ),
        ],
    )
    async def nihongo_romajinize(
        self,
        ctx: ipy.SlashContext,
        source: str,
        spelling_type: Literal["hepburn", "kunrei",
                               "nihon", "passport"] = "hepburn",
        use_foreign: bool = True,
    ) -> None:
        """Convert kana to romaji"""
        try:
            await ctx.defer()

            send = await ctx.send(
                embed=ipy.Embed(
                    title="Kana to Romaji",
                    description="Converting...\nThis may take a while",
                    color=0x168821,
                    timestamp=datetime.now(tz=timezone.utc),
                )
            )

            kks = pykakasi.kakasi()
            katsu = cutlet.Cutlet(
                system=spelling_type if spelling_type != "passport" else "hepburn",
                ensure_ascii=False,
                use_foreign_spelling=use_foreign,
            )
            result = kks.convert(source)
            hira: list[str] = []
            kata: list[str] = []
            refined: list[str] = []
            passport: list[str] = []
            for token in result:
                token: dict[str, str]
                orig_str = token["orig"]
                hira_str = token["hira"].strip()
                kana_str = token["kana"].strip()
                passport_str = token["passport"].strip()
                hira.append(hira_str)
                kata.append(kana_str)
                passport.append(passport_str)
                if orig_str in [hira_str, kana_str]:
                    refined.append(orig_str)
                else:
                    refined.append(" " + hira_str)

            if spelling_type != "passport":
                romaji: str = katsu.romaji(
                    text="".join(refined),
                    capitalize=True,
                )
                splitted = romaji.split(".")
            else:
                splitted = " ".join(passport)
                splitted = splitted.split(".")

            romaji_list = []
            for token in splitted:
                token: str = token.strip()
                romaji_list.append(token.capitalize())
            romaji = ". ".join(romaji_list)

            # Sanitize markdown
            source = sanitize_markdown(source)
            romaji = sanitize_markdown(romaji)
            hira = sanitize_markdown(" ".join(hira))
            kata = sanitize_markdown(" ".join(kata))

            footer = [
                "Powered by",
                "Cutlet and" if spelling_type != "passport" else "",
                "PyKakasi, romanization may not be accurate, please use with",
                "caution",
            ]

            footer = " ".join(footer)

            embed = ipy.Embed(
                title="Kana to Romaji",
                color=0x168821,
                fields=[
                    ipy.EmbedField(name="Source",
                                   value=source,
                                   inline=False),
                    ipy.EmbedField(name="Romaji",
                                   value=romaji,
                                   inline=False),
                    ipy.EmbedField(name="Hiragana",
                                   value=hira,
                                   inline=False),
                    ipy.EmbedField(name="Katakana",
                                   value=kata,
                                   inline=False),
                ],
                footer=ipy.EmbedFooter(
                    text=footer.replace("  ", " "),
                ),
                timestamp=datetime.now(tz=timezone.utc),
            )
            await send.edit(embed=embed)
        except Exception as e:
            embed = generate_commons_except_embed(
                description="Failed to convert Japanese script to romaji",
                error=e,
            )
            embed.add_field(
                name="Source",
                # limit to 1024 chars
                value=source[:1020] + "..." if len(source) >= 1024 else source,
            )
            embed.timestamp = datetime.now(tz=timezone.utc)
            await send.edit(embed=embed)
            save_traceback_to_file("nihongo_romajinize", ctx.author, e)


def setup(bot: ipy.Client | ipy.AutoShardedClient) -> None:
    """Load the extension"""
    NihongoCog(bot)

from datetime import datetime, timezone

import cutlet
import interactions as ipy
import pykakasi

from modules.commons import sanitize_markdown


class NihongoCog(ipy.Extension):
    """Extension for Japanese tools"""

    nihongo_head = ipy.SlashCommand(
        name="nihongo",
        description="Japanese tools",
        cooldown=ipy.Cooldown(
            cooldown_bucket=ipy.Buckets.CHANNEL,
            rate=1,
            interval=10,
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
        spelling_type: str = "hepburn",
        use_foreign: bool = True,
    ) -> None:
        """Convert kana to romaji"""
        await ctx.defer()
        katsu = cutlet.Cutlet(
            system=spelling_type,
            ensure_ascii=False,
            use_foreign_spelling=use_foreign,
        )
        romaji: str = katsu.romaji(
            text=source,
            capitalize=True,
        )
        kks = pykakasi.kakasi()
        result = kks.convert(source)
        hira: str = " ".join([item["hira"] for item in result])
        kata: str = " ".join([item["kana"] for item in result])

        # Sanitize markdown
        source = sanitize_markdown(source)
        romaji = sanitize_markdown(romaji)
        hira = sanitize_markdown(hira)
        kata = sanitize_markdown(kata)

        await ctx.send(
            embed=ipy.Embed(
                title="Kana to Romaji",
                color=0x168821,
                fields=[
                    ipy.EmbedField(
                        name="Source",
                        value=source,
                        inline=False,
                    ),
                    ipy.EmbedField(
                        name="Romaji",
                        value=romaji,
                        inline=False,
                    ),
                    ipy.EmbedField(
                        name="Hiragana",
                        value=hira,
                        inline=False,
                    ),
                    ipy.EmbedField(
                        name="Katakana",
                        value=kata,
                        inline=False,
                    ),
                ],
                footer=ipy.EmbedFooter(
                    text="Powered by Cutlet and PyKakasi, romanization may not be accurate, please use with caution",
                ),
                timestamp=datetime.now(tz=timezone.utc),
            )
        )


def setup(bot: ipy.Client | ipy.AutoShardedClient) -> None:
    """Load the extension"""
    NihongoCog(bot)

import interactions as ipy
from modules.i18n import lang, readUserLang
from plusminus import BaseArithmeticParser as BAP
from modules.commons import utilitiesExceptionEmbed, snowflake_to_datetime
from base64 import b64encode, b64decode
import re
from urllib.parse import urlencode as urlenc
from classes.thecolorapi import TheColorApi


class Utilities(ipy.Extension):
    @ipy.slash_command(
        name="utilities",
        description="Get some utilities you might need",
    )
    async def utilities(self, ctx: ipy.SlashContext):
        pass


    @utilities.subcommand(
        sub_cmd_name="math",
        sub_cmd_description="Evaluate a (safe) math expression",
        options=[
            ipy.SlashCommandOption(
                name="expression",
                description="The expression to evaluate",
                type=ipy.OptionType.STRING,
                required=True
            )
        ]
    )
    async def utilities_math(self, ctx: ipy.SlashContext, expression: str):
        await ctx.defer()
        ul = readUserLang(ctx)
        l_ = lang(ul)['utilities']
        try:
            exp = BAP().evaluate(expression)
            await ctx.send(embed=ipy.Embed(
                title=l_['commons']['result'],
                color=0x996422,
                fields=[
                    ipy.EmbedField(
                        name=l_['math']['expression'],
                        value=f"```py\n{expression}```",
                        inline=False
                    ),
                    ipy.EmbedField(
                        name=l_['commons']['result'],
                        value=f"```py\n{exp}```",
                        inline=False
                    )
                ]
            ))
        except Exception as e:
            await ctx.send(embed=utilitiesExceptionEmbed(
                language=ul,
                description=l_['math']['exception'],
                field_name=l_['math']['expression'],
                field_value=f"```py\n{expression}```",
                error=e
            ))


    @utilities.subcommand(
        sub_cmd_name="base64",
        sub_cmd_description="Encode/decode a string to/from base64",
        options=[
            ipy.SlashCommandOption(
                name="mode",
                description="The mode to use",
                type=ipy.OptionType.STRING,
                required=True,
                choices=[
                    ipy.SlashCommandChoice(
                        name="Encode",
                        value="encode"
                    ),
                    ipy.SlashCommandChoice(
                        name="Decode",
                        value="decode"
                    )
                ]
            ),
            ipy.SlashCommandOption(
                name="string",
                description="The string to encode/decode",
                type=ipy.OptionType.STRING,
                required=True
            )
        ]
    )
    async def utilities_base64(self, ctx: ipy.SlashContext, mode: str, string: str):
        await ctx.defer()
        ul = readUserLang(ctx)
        l_ = lang(ul)['utilities']
        try:
            if mode == "encode":
                res = b64encode(string.encode()).decode()
                strVal = f"""```md
    {string}
    ```"""
                resVal = f"""```{res}```"""
            else:
                res = b64decode(string.encode()).decode()
                strVal = f"""```{string}```"""
                resVal = f"""```md
    {res}
    ```"""
            await ctx.send(embed=ipy.Embed(
                title=l_['commons']['result'],
                color=0x996422,
                fields=[
                    ipy.EmbedField(
                        name=l_['base64']['string'],
                        value=strVal,
                        inline=False
                    ),
                    ipy.EmbedField(
                        name=l_['commons']['result'],
                        value=resVal,
                        inline=False
                    )
                ]
            ))
        except Exception as e:
            await ctx.send(embed=utilitiesExceptionEmbed(
                language=ul,
                description=l_['base64']['exception'],
                field_name=l_['commons']['string'],
                field_value=f"```{string}```",
                error=e
            ))


    @utilities.subcommand(
        sub_cmd_name="color",
        sub_cmd_description="Get information about a color",
        options=[
            ipy.SlashCommandOption(
                name="format",
                description="The format to use",
                type=ipy.OptionType.STRING,
                required=True,
                choices=[
                    ipy.SlashCommandChoice(
                        name="Hex",
                        value="hex"
                    ),
                    ipy.SlashCommandChoice(
                        name="RGB",
                        value="rgb"
                    ),
                    ipy.SlashCommandChoice(
                        name="HSL",
                        value="hsl"
                    ),
                    ipy.SlashCommandChoice(
                        name="CMYK",
                        value="cmyk"
                    ),
                ],
            ),
            ipy.SlashCommandOption(
                name="color",
                description="The color to get information about",
                type=ipy.OptionType.STRING,
                required=True
            ),
        ]
    )
    async def utilities_color(self, ctx: ipy.SlashContext, format: str, color: str):
        await ctx.defer()
        ul = readUserLang(ctx)
        l_ = lang(ul)['utilities']
        res: dict = {}
        try:
            if format == "hex" and re.match(r"^#?(?:[0-9a-fA-F]{3}){1,2}$", color) is None:
                raise ValueError("Invalid hex color")
            elif format == "hex" and re.match(r"^#", color) is None:
                color = f"#{color}"
            async with TheColorApi() as tca:
                match format:
                    case "hex":
                        res = await tca.color(hex=color)
                    case "rgb":
                        res = await tca.color(rgb=color)
                    case "hsl":
                        res = await tca.color(hsl=color)
                    case "cmyk":
                        res = await tca.color(cmyk=color)
                # await tca.close()
            rgb: dict = res['rgb']
            col: int = (rgb['r'] << 16) + (rgb['g'] << 8) + rgb['b']
            fields = [
                ipy.EmbedField(
                    name=l_['color']['name'],
                    value=f"{res['name']['value']}",
                    inline=False
                ),
            ]
            for f in ['hex', 'rgb', 'hsl', 'cmyk', 'hsv']:
                fields.append(ipy.EmbedField(
                    name=f"{f.upper()}",
                    value=f"```css\n{res[f]['value']}\n```",
                    inline=True
                ))
            fields.append(ipy.EmbedField(
                name="DEC",
                value=f"```py\n{col}\n```",
                inline=True
            ))
            await ctx.send(embed=ipy.Embed(
                title=l_['commons']['result'],
                color=col,
                fields=fields,
                thumbnail=ipy.EmbedAttachment(
                    url=res['image']['bare']
                ),
                footer=ipy.EmbedFooter(
                    text=l_['color']['powered']
                )
            ))
        except Exception as e:
            await ctx.send(embed=utilitiesExceptionEmbed(
                language=ul,
                description=l_['color']['exception'],
                field_name=l_['color']['color'],
                field_value=f"```{color}```",
                error=e,
            ))


    @utilities.subcommand(
        sub_cmd_name="qrcode",
        sub_cmd_description="Generate a QR code",
        options=[
            ipy.SlashCommandOption(
                name="string",
                description="The string to encode",
                type=ipy.OptionType.STRING,
                required=True
            ),
            ipy.SlashCommandOption(
                name="error_correction",
                description="The error correction level",
                type=ipy.OptionType.STRING,
                required=False,
                choices=[
                    ipy.SlashCommandChoice(
                        name="Low (~7%, default)",
                        value="L"
                    ),
                    ipy.SlashCommandChoice(
                        name="Medium (~15%)",
                        value="M"
                    ),
                    ipy.SlashCommandChoice(
                        name="Quality (~25%)",
                        value="Q"
                    ),
                    ipy.SlashCommandChoice(
                        name="High (~30%)",
                        value="H"
                    ),
                ],
            ),
        ]
    )
    async def utilities_qrcode(self, ctx: ipy.SlashContext, string: str, error_correction: str = "L"):
        await ctx.defer()
        ul = readUserLang(ctx)
        l_ = lang(ul)['utilities']
        try:
            params = {
                "data": string,
                "size": "500x500",
                "ecc": error_correction,
                "format": "jpg",
            }
            # convert params object to string
            params = urlenc(params)
            await ctx.send(embed=ipy.Embed(
                title=l_['commons']['result'],
                color=0x000000,
                fields=[
                    ipy.EmbedField(
                        name=l_['commons']['string'],
                        value=f"```{string}```",
                        inline=False
                    ),
                ],
                images=[ipy.EmbedAttachment(
                    url=f"https://api.qrserver.com/v1/create-qr-code/?{params}"
                )],
                footer=ipy.EmbedFooter(
                    text=l_['qrcode']['powered']
                )
            ))
        except Exception as e:
            await ctx.send(embed=utilitiesExceptionEmbed(
                language=ul,
                description=l_['qrcode']['exception'],
                field_name=l_['commons']['string'],
                field_value=f"```{string}```",
                error=e,
            ))


    @utilities.subcommand(
        sub_cmd_name="snowflake",
        sub_cmd_description="Convert a Discord Snowflake to a timestamp",
        options=[
            ipy.SlashCommandOption(
                name="snowflake",
                description="The snowflake to convert",
                required=True,
                type=ipy.OptionType.STRING,
            )
        ]
    )
    async def utilities_snowflake(self, ctx: ipy.SlashContext, snowflake: str):
        """Convert a Discord Snowflake to a timestamp"""
        await ctx.defer()
        ul = readUserLang(ctx)
        l_ = lang(ul)['utilities']['snowflake']
        tmsp = int(snowflake_to_datetime(int(snowflake)))
        await ctx.send(embed=ipy.Embed(
            title=l_['title'],
            description=l_['text'],
            color=0x1F1F1F,
            fields=[
                ipy.EmbedField(
                    name=l_['snowflake'],
                    value=f"```py\n{snowflake}\n```",
                    inline=False
                ),
                ipy.EmbedField(
                    name=l_['timestamp'],
                    value=f"```py\n{tmsp}\n```",
                    inline=False
                ),
                ipy.EmbedField(
                    name=l_['date'],
                    value=f"<t:{tmsp}:D>",
                    inline=True
                ),
                ipy.EmbedField(
                    name=l_['full_date'],
                    value=f"<t:{tmsp}:F>",
                    inline=True
                ),
                ipy.EmbedField(
                    name=l_['relative'],
                    value=f"<t:{tmsp}:R>",
                    inline=True
                ),
            ]
        ))

def setup(bot):
    Utilities(bot)

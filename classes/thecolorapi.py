from dataclasses import dataclass

import aiohttp

from classes.cache import Caching
from classes.excepts import ProviderHttpError
from modules.const import USER_AGENT

Cache = Caching("cache/thecolorapi", 604800)


@dataclass
class BaseValue:
    """Base value dataclass"""

    value: str
    """Value string"""


@dataclass
class RGBFractions:
    """RGB Fractions dataclass"""

    r: float | None = None
    """Red fraction in RGB"""
    g: float | None = None
    """Green fraction in RGB"""
    b: float | None = None
    """Blue fraction in RGB"""


@dataclass
class HSVFractions:
    """HSV Fractions dataclass"""

    h: float | None = None
    """Hue fraction in HSV"""
    s: float | None = None
    """Saturation fraction in HSV"""
    v: float | None = None
    """Value fraction in HSV"""


@dataclass
class HSLFractions:
    """HSL Fractions dataclass"""

    h: float | None = None
    """Hue fraction in HSL"""
    s: float | None = None
    """Saturation fraction in HSL"""
    l: float | None = None
    """Lightness fraction in HSL"""


@dataclass
class CMYKFractions:
    """CMYK Fractions dataclass"""

    c: float | None = None
    """Cyan fraction in CMYK"""
    m: float | None = None
    """Magenta fraction in CMYK"""
    y: float | None = None
    """Yellow fraction in CMYK"""
    k: float | None = None
    """Key fraction in CMYK"""


@dataclass
class XYZFractions:
    """XYZ Fractions dataclass"""

    X: float | None = None
    """X fraction in XYZ"""
    Y: float | None = None
    """Y fraction in XYZ"""
    Z: float | None = None
    """Z fraction in XYZ"""


@dataclass
class HexValue(BaseValue):
    """Hex value dataclass"""

    clean: str
    """Clean value string"""


@dataclass
class RGBValue(BaseValue):
    """RGB value dataclass"""

    fraction: RGBFractions
    """Fractions"""
    r: int
    """Red value"""
    g: int
    """Green value"""
    b: int
    """Blue value"""


@dataclass
class HSLValue(BaseValue):
    """HSL value dataclass"""

    fraction: HSLFractions
    """Fractions"""
    h: int
    """Hue value"""
    s: int
    """Saturation value"""
    l: int
    """Lightness value"""


@dataclass
class HSVValue(BaseValue):
    """HSV value dataclass"""

    fraction: HSVFractions
    """Fractions"""
    h: int
    """Hue value"""
    s: int
    """Saturation value"""
    v: int
    """Value value"""


@dataclass
class CMYKValue(BaseValue):
    """CMYK value dataclass"""

    fraction: CMYKFractions
    """Fractions"""
    c: int
    """Cyan value"""
    m: int
    """Magenta value"""
    y: int
    """Yellow value"""
    k: int
    """Key value"""


@dataclass
class XYZValue(BaseValue):
    """XYZ value dataclass"""

    fraction: XYZFractions
    """Fractions"""
    X: int
    """X value"""
    Y: int
    """Y value"""
    Z: int
    """Z value"""


@dataclass
class Metadata(BaseValue):
    """Metadata dataclass"""

    closest_named_hex: str
    """Closest named hex value"""
    exact_match_name: bool
    """Exact match name"""
    distance: int
    """Distance"""


@dataclass
class Image:
    """Image dataclass"""

    bare: str
    """Bare image URL"""
    named: str
    """Named image URL"""


@dataclass
class Contrast:
    """Contrast dataclass"""

    value: str
    """Contrast value"""


@dataclass
class Links:
    """Links dataclass"""

    self: dict[str, str]
    """Self link"""


@dataclass
class Color:
    """Color dataclass"""

    hex: HexValue
    """Hex value"""
    rgb: RGBValue
    """RGB value"""
    hsl: HSLValue
    """HSL value"""
    hsv: HSVValue
    """HSV value"""
    cmyk: CMYKValue
    """CMYK value"""
    XYZ: XYZValue
    """XYZ value"""
    name: Metadata
    """Name value"""
    image: Image
    """Image value"""
    contrast: Contrast
    """Contrast value"""
    _links: Links
    """Links"""
    _embedded: dict[str, dict[str, str]] | None = None


class TheColorApi:
    """
    The Color API wrapper

    This module is a wrapper for The Color API, which is used to get color information from hex, rgb, hsl, hsv, and cmyk values.
    """

    def __init__(self):
        """Initialize the class"""
        self.base_url = "https://www.thecolorapi.com"
        self.session = None

    async def __aenter__(self):
        """Create a session if class invoked with `with` statement"""
        self.session = aiohttp.ClientSession(
            headers={"User-Agent": USER_AGENT})
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Close the session if class invoked with `with` statement"""
        await self.session.close()

    async def close(self) -> None:
        """Close the session"""
        await self.session.close()

    @staticmethod
    def dict_to_dataclass(data: dict) -> Color:
        """Convert data dict to dataclass"""
        data["rgb"]["fraction"] = RGBFractions(**data["rgb"]["fraction"])
        data["hsl"]["fraction"] = HSLFractions(**data["hsl"]["fraction"])
        data["hsv"]["fraction"] = HSVFractions(**data["hsv"]["fraction"])
        data["cmyk"]["fraction"] = CMYKFractions(**data["cmyk"]["fraction"])
        data["XYZ"]["fraction"] = XYZFractions(**data["XYZ"]["fraction"])
        data["hex"] = HexValue(**data["hex"])
        data["rgb"] = RGBValue(**data["rgb"])
        data["hsl"] = HSLValue(**data["hsl"])
        data["hsv"] = HSVValue(**data["hsv"])
        data["cmyk"] = CMYKValue(**data["cmyk"])
        data["XYZ"] = XYZValue(**data["XYZ"])
        data["name"] = Metadata(**data["name"])
        data["image"] = Image(**data["image"])
        data["contrast"] = Contrast(**data["contrast"])
        data["_links"] = Links(**data["_links"])

        return Color(**data)

    async def color(self, **color: str) -> Color:
        """
        Get color information from hex, rgb, hsl, hsv, or cmyk values

        Args:
            **color (kwargs[str]): Color values
                Supported kwargs:
                    hex: Hexadecimal color value
                    rgb: RGB color value
                    hsl: HSL color value
                    hsv: HSV color value
                    cmyk: CMYK color value

        Raises:
            ProviderHttpError: If The Color API returns an error

        Returns:
            dict: Color information
        """
        if color["hex"].startswith("#"):
            color["hex"] = color["hex"][1:]
        filename = "-".join([f"{k}_{v}" for k, v in color.items()]) + ".json"
        cache_file_path = Cache.get_cache_file_path(filename)
        cached_data = Cache.read_cached_data(cache_file_path)
        if cached_data is not None:
            return self.dict_to_dataclass(cached_data)

        async with self.session.get(f"{self.base_url}/id", params=color) as response:
            if response.status == 200:
                data = await response.json()
                Cache.write_data_to_cache(data, cache_file_path)
                return self.dict_to_dataclass(data)
            error_message = await response.text()
            raise ProviderHttpError(error_message, response.status)

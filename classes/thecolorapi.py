import json
import os
import time
from dataclasses import dataclass

import aiohttp

from classes.excepts import ProviderHttpError
from modules.const import USER_AGENT


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
        self.cache_directory = "cache/thecolorapi"
        self.cache_expiration_time = 604800  # 1 week in seconds

    async def __aenter__(self):
        """Create a session if class invoked with `with` statement"""
        self.session = aiohttp.ClientSession(headers={"User-Agent": USER_AGENT})
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
        return Color(
            hex=HexValue(
                value=data["hex"]["value"],
                clean=data["hex"]["clean"],
            ),
            rgb=RGBValue(
                fraction=RGBFractions(
                    r=data["rgb"]["fraction"]["r"],
                    g=data["rgb"]["fraction"]["g"],
                    b=data["rgb"]["fraction"]["b"],
                ),
                r=data["rgb"]["r"],
                g=data["rgb"]["g"],
                b=data["rgb"]["b"],
                value=data["rgb"]["value"],
            ),
            hsl=HSLValue(
                fraction=HSLFractions(
                    h=data["hsl"]["fraction"]["h"],
                    s=data["hsl"]["fraction"]["s"],
                    l=data["hsl"]["fraction"]["l"],
                ),
                h=data["hsl"]["h"],
                s=data["hsl"]["s"],
                l=data["hsl"]["l"],
                value=data["hsl"]["value"],
            ),
            hsv=HSVValue(
                fraction=HSVFractions(
                    h=data["hsv"]["fraction"]["h"],
                    s=data["hsv"]["fraction"]["s"],
                    v=data["hsv"]["fraction"]["v"],
                ),
                h=data["hsv"]["h"],
                s=data["hsv"]["s"],
                v=data["hsv"]["v"],
                value=data["hsv"]["value"],
            ),
            cmyk=CMYKValue(
                fraction=CMYKFractions(
                    c=data["cmyk"]["fraction"]["c"],
                    m=data["cmyk"]["fraction"]["m"],
                    y=data["cmyk"]["fraction"]["y"],
                    k=data["cmyk"]["fraction"]["k"],
                ),
                c=data["cmyk"]["c"],
                m=data["cmyk"]["m"],
                y=data["cmyk"]["y"],
                k=data["cmyk"]["k"],
                value=data["cmyk"]["value"],
            ),
            XYZ=XYZValue(
                fraction=XYZFractions(
                    X=data["XYZ"]["fraction"]["X"],
                    Y=data["XYZ"]["fraction"]["Y"],
                    Z=data["XYZ"]["fraction"]["Z"],
                ),
                X=data["XYZ"]["X"],
                Y=data["XYZ"]["Y"],
                Z=data["XYZ"]["Z"],
                value=data["XYZ"]["value"],
            ),
            name=Metadata(
                value=data["name"]["value"],
                closest_named_hex=data["name"]["closest_named_hex"],
                exact_match_name=data["name"]["exact_match_name"],
                distance=data["name"]["distance"],
            ),
            image=Image(
                bare=data["image"]["bare"],
                named=data["image"]["named"],
            ),
            contrast=Contrast(
                value=data["contrast"]["value"],
            ),
            _links=Links(
                self={
                    "href": data["_links"]["self"]["href"],
                },
            ),
            _embedded=data["_embedded"] if "_embedded" in data else None,
        )

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
        cache_file_path = self.get_cache_file_path(color)
        cached_data = self.read_cached_data(cache_file_path)
        if cached_data is not None:
            return self.dict_to_dataclass(cached_data)

        async with self.session.get(f"{self.base_url}/id", params=color) as response:
            if response.status == 200:
                data = await response.json()
                self.write_data_to_cache(data, cache_file_path)
                return self.dict_to_dataclass(data)
            error_message = await response.text()
            raise ProviderHttpError(error_message, response.status)

    def get_cache_file_path(self, color_params):
        """
        Get the cache file from path

        Args:
            color_params (dict): Color parameters
        """
        filename = "-".join([f"{k}_{v}" for k, v in color_params.items()]) + ".json"
        return os.path.join(self.cache_directory, filename)

    def read_cached_data(self, cache_file_path) -> dict | None:
        """
        Read cached data from file

        Args:
            cache_file_path (str): Cache file path

        Returns:
            dict: Cached data
            None: If cache file does not exist or cache is expired
        """
        if os.path.exists(cache_file_path):
            with open(cache_file_path, "r") as cache_file:
                cache_data = json.load(cache_file)
                cache_age = time.time() - cache_data["timestamp"]
                if cache_age < self.cache_expiration_time:
                    return cache_data["data"]
        return None

    @staticmethod
    def write_data_to_cache(data, cache_file_path: str):
        """
        Write data to cache

        Args:
            data (any): Data to write to cache
            cache_file_path (str): Cache file path
        """
        cache_data = {"timestamp": time.time(), "data": data}
        os.makedirs(os.path.dirname(cache_file_path), exist_ok=True)
        with open(cache_file_path, "w") as cache_file:
            json.dump(cache_data, cache_file)

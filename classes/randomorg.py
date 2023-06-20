"""Random.org True Random Number Generator API Wrapper"""

from enum import Enum

import aiohttp

from classes.excepts import ProviderHttpError, ProviderTypeError
from modules.const import USER_AGENT


class RandomOrg:
    """Random.org True Random Number Generator API Wrapper

    Functions
    ---------
    integers(num: int, min: int, max: int, base: int = 10)
        Generate random integers

        Example
        -------
        >>> async with RandomOrg() as random:
        >>>     data = await random.integers(10, 1, 100)
        >>>     print(data)
        [42, 69, 13, 37, 100, 1, 2, 3, 4, 5]

    sequences(min: int, max: int)
        Generate random sequences

        Example
        -------
        >>> async with RandomOrg() as random:
        >>>     data = await random.sequences(1, 100)
        >>>     print(data)
        [42, 69, 13, 37, 100, 1, 2, 3, 4, 5]

    strings(num: int, length: int = 10, digits: str = "on", upperalpha: str = "on", loweralpha: str = "on", unique: str = "on")
        Generate random strings

        Example
        -------
        >>> async with RandomOrg() as random:
        >>>     data = await random.strings(10, 10)
        >>>     print(data)
        ["1jzfbKJ5dt", "UjkWKcV64m", "9HExGr4qC1", "g441kmnisQ", "UDbWOeo2gI", "JTNorfmXft", "myqApMnhcq", "uR8dWQ8UdZ", "3pEWE0UeHL", "EoqGthvMzD"]
    """

    def __init__(self):
        """Initialize the Random.org True Random Number Generator API Wrapper"""
        self.base_url = "https://www.random.org"
        self.session = None
        self.params = {"format": "plain", "rnd": "new"}

    async def __aenter__(self):
        """Enter the async context manager"""
        self.session = aiohttp.ClientSession(
            headers={"User-Agent": USER_AGENT})
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the async context manager"""
        await self.close()

    async def close(self) -> None:
        """Close the aiohttp session"""
        await self.session.close()

    class OnOff(Enum):
        """OnOff enum"""

        ON = "on"
        OFF = "off"

    async def integers(
        self, num: int, min_val: int, max_val: int, base: int = 10
    ) -> list[int]:
        """
        Generate random integers

        Args:
            num (int): Number of integers to generate
            min_val (int): Minimum value
            max_val (int): Maximum value
            base (int): Base of the integers, defaults to 10

        Returns:
            list[int]: List of random integers
        """
        if base not in [2, 8, 10, 16]:
            raise ProviderTypeError("Base must be 2, 8, 10, or 16", "base")
        if num > 10000 or num < 1:
            raise ProviderTypeError(
                "Number must be between 1 and 10000", "num")
        if min_val > max_val:
            raise ProviderTypeError(
                "Min must be less than or equal to max", "minmax")
        params = self.params.copy()
        params["num"] = num
        params["min"] = min_val
        params["max"] = max_val
        params["col"] = 1
        params["base"] = base
        async with self.session.get(
            f"{self.base_url}/integers", params=params
        ) as response:
            if response.status == 200:
                data = await response.text()
                data = data.splitlines()
                data = [int(i) for i in data]
                return data
            error_message = await response.text()
            raise ProviderHttpError(error_message, response.status)

    async def sequences(self, min_val: int, max_val: int) -> list[int]:
        """
        Generate random sequences

        Args:
            min_val (int): Minimum value
            max_val (int): Maximum value

        Returns:
            list[int]: List of random sequences
        """
        if min_val > max_val:
            raise ProviderTypeError(
                "Min must be less than or equal to max", "minmax")
        params = self.params.copy()
        params["min"] = min_val
        params["max"] = max_val
        async with self.session.get(
            f"{self.base_url}/sequences", params=params
        ) as response:
            if response.status == 200:
                data = await response.text()
                data = data.splitlines()
                data = [int(i) for i in data]
                return data
            error_message = await response.text()
            raise ProviderHttpError(error_message, response.status)

    async def strings(
        self,
        num: int,
        length: int = 10,
        digits: str | OnOff = "on",
        upperalpha: str | OnOff = "on",
        loweralpha: str | OnOff = "on",
        unique: str | OnOff = "on",
    ) -> list[str]:
        """
        Generate random strings

        Args:
            num (int): Number of strings to generate
            length (int): Length of the strings, defaults to 10
            digits (str | OnOff): Include digits, defaults to "on"
            upperalpha (str | OnOff): Include uppercase letters, defaults to "on"
            loweralpha (str | OnOff): Include lowercase letters, defaults to "on"
            unique (str | OnOff): Unique strings, defaults to "on"

        Raises:
            ProviderTypeError: If arguments are invalid
            ProviderHttpError: If the API returns an error

        Returns:
            list[str]: List of random strings
        """
        if length > 20:
            raise ProviderTypeError(
                "Length must be less than or equal to 20", "length")
        if num > 10000 or num < 1:
            raise ProviderTypeError(
                "Number must be between 1 and 10000", "num")
        if isinstance(digits, self.OnOff):
            digits = digits.value
        if isinstance(upperalpha, self.OnOff):
            upperalpha = upperalpha.value
        if isinstance(loweralpha, self.OnOff):
            loweralpha = loweralpha.value
        if isinstance(unique, self.OnOff):
            unique = unique.value
        if (
            isinstance(digits, str)
            or isinstance(upperalpha, str)
            or isinstance(loweralpha, str)
            or isinstance(unique, str)
        ):
            if digits not in ["on", "off"]:
                raise ProviderTypeError("Digits must be on or off", "digits")
            if upperalpha not in ["on", "off"]:
                raise ProviderTypeError(
                    "Upperalpha must be on or off", "upperalpha")
            if loweralpha not in ["on", "off"]:
                raise ProviderTypeError(
                    "Loweralpha must be on or off", "loweralpha")
            if unique not in ["on", "off"]:
                raise ProviderTypeError("Unique must be on or off", "unique")
        params = self.params.copy()
        params["num"] = num
        params["len"] = length
        params["digits"] = digits
        params["upperalpha"] = upperalpha
        params["loweralpha"] = loweralpha
        params["unique"] = unique
        async with self.session.get(
            f"{self.base_url}/strings", params=params
        ) as response:
            if response.status == 200:
                data = await response.text()
                data = data.splitlines()
                return data
            error_message = await response.text()
            raise ProviderHttpError(error_message, response.status)


__all__ = ["RandomOrg"]

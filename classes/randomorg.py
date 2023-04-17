"""Random.org True Random Number Generator API Wrapper"""

import aiohttp

from classes.excepts import ProviderHttpError, ProviderTypeError


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
        self.base_url = "https://www.random.org"
        self.session = None
        self.params = {
            "format": "plain",
            "rnd": "new"
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def close(self) -> None:
        await self.session.close()

    async def integers(self, num: int, min: int, max: int, base: int = 10):
        """Generate random integers"""
        if base not in [2, 8, 10, 16]:
            raise ProviderTypeError("Base must be 2, 8, 10, or 16", "base")
        if num > 10000 or num < 1:
            raise ProviderTypeError("Number must be between 1 and 10000", "num")
        if min > max:
            raise ProviderTypeError("Min must be less than or equal to max", "minmax")
        params = self.params.copy()
        params["num"] = num
        params["min"] = min
        params["max"] = max
        params["col"] = 1
        params["base"] = base
        async with self.session.get(f"{self.base_url}/integers", params=params) as response:
            if response.status == 200:
                data = await response.text()
                data = data.splitlines()
                data = [int(i) for i in data]
                return data
            else:
                error_message = await response.text()
                raise ProviderHttpError(error_message, response.status)

    async def sequences(self, min: int, max: int):
        """Generate random sequences"""
        if min > max:
            raise ProviderTypeError("Min must be less than or equal to max", "minmax")
        params = self.params.copy()
        params["min"] = min
        params["max"] = max
        async with self.session.get(f"{self.base_url}/sequences", params=params) as response:
            if response.status == 200:
                data = await response.text()
                data = data.splitlines()
                data = [int(i) for i in data]
                return data
            else:
                error_message = await response.text()
                raise ProviderHttpError(error_message, response.status)

    async def strings(self, num: int, length: int = 10, digits: str = "on", upperalpha: str = "on", loweralpha: str = "on", unique: str = "on"):
        """Generate random strings"""
        if length > 20:
            raise ProviderTypeError("Length must be less than or equal to 20", "length")
        if num > 10000 or num < 1:
            raise ProviderTypeError("Number must be between 1 and 10000", "num")
        params = self.params.copy()
        params["num"] = num
        params["len"] = length
        params["digits"] = digits
        params["upperalpha"] = upperalpha
        params["loweralpha"] = loweralpha
        params["unique"] = unique
        async with self.session.get(f"{self.base_url}/strings", params=params) as response:
            if response.status == 200:
                data = await response.text()
                data = data.splitlines()
                return data
            else:
                error_message = await response.text()
                raise ProviderHttpError(error_message, response.status)


__all__ = ["RandomOrg"]

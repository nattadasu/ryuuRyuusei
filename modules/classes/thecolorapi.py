import aiohttp
from modules.classes.excepts import TheColorApiHttpError

class TheColorApi:
    """The Color API"""

    def __init__(self):
        """Constructor method for TheColorApi class. Initializes base_url and session attributes."""
        self.base_url = "https://www.thecolorapi.com"
        self.session = None

    async def __aenter__(self):
        """Async context manager entry method. Creates a new aiohttp ClientSession object and returns the current instance of the class."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit method. Closes the aiohttp ClientSession object."""
        await self.close()

    async def close(self) -> None:
        """Closes the aiohttp ClientSession object."""
        await self.session.close()

    async def color(self, **color):
        """
        Retrieves color information from The Color API based on the given parameters.

        Parameters:
        **color (dict): A dictionary containing the color information.

        Returns:
        The JSON data from the response.

        Raises:
        TheColorApiHttpError: If the response has a non-200 status code, the error message and status code will be included in the exception.
        """
        async with self.session.get(f"{self.base_url}/id", params=color) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                error_message = await response.text()
                raise TheColorApiHttpError(error_message, response.status)

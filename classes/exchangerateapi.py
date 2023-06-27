"""
ExchangeRateAPI wrapper

Get exchange rates from https://www.exchangerate-api.com/

Example:
    >>> import asyncio
    >>> from classes.exchangerateapi import ExchangeRateAPI
    >>> async def main():
    ...     async with ExchangeRateAPI() as api:
    ...         rates = await api.get_exchange_rate("USD", "EUR", 1)
    ...         print(rates)
    >>> asyncio.run(main())
    0.821
"""

from dataclasses import dataclass
from typing import Literal

import aiohttp

from classes.cache import Caching
from classes.excepts import ProviderHttpError
from modules.const import EXCHANGERATE_API_KEY, USER_AGENT

accepted_currencies = Literal[
    "AED", "AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AUD", "AWG", "AZN", "BAM", "BBD",
    "BDT", "BGN", "BHD", "BIF", "BMD", "BND", "BOB", "BRL", "BSD", "BTN", "BWP", "BYN",
    "BZD", "CAD", "CDF", "CHF", "CLP", "CNY", "COP", "CRC", "CUP", "CVE", "CZK", "DJF",
    "DKK", "DOP", "DZD", "EGP", "ERN", "ETB", "EUR", "FJD", "FKP", "FOK", "GBP", "GEL",
    "GGP", "GHS", "GIP", "GMD", "GNF", "GTQ", "GYD", "HKD", "HNL", "HRK", "HTG", "HUF",
    "IDR", "ILS", "IMP", "INR", "IQD", "IRR", "ISK", "JEP", "JMD", "JOD", "JPY", "KES",
    "KGS", "KHR", "KID", "KMF", "KRW", "KWD", "KYD", "KZT", "LAK", "LBP", "LKR", "LRD",
    "LSL", "LYD", "MAD", "MDL", "MGA", "MKD", "MMK", "MNT", "MOP", "MRU", "MUR", "MVR",
    "MWK", "MXN", "MYR", "MZN", "NAD", "NGN", "NIO", "NOK", "NPR", "NZD", "OMR", "PAB",
    "PEN", "PGK", "PHP", "PKR", "PLN", "PYG", "QAR", "RON", "RSD", "RUB", "RWF", "SAR",
    "SBD", "SCR", "SDG", "SEK", "SGD", "SHP", "SLE", "SOS", "SRD", "SSP", "STN", "SYP",
    "SZL", "THB", "TJS", "TMT", "TND", "TOP", "TRY", "TTD", "TVD", "TWD", "TZS", "UAH",
    "UGX", "USD", "UYU", "UZS", "VES", "VND", "VUV", "WST", "XAF", "XCD", "XDR", "XOF",
    "XPF", "YER", "ZAR", "ZMW", "ZWL"
]
"""The accepted currencies for the ExchangeRate-API"""

Cache = Caching(cache_directory="cache/exchangerateapi",
                cache_expiration_time=86400)


@dataclass
class ExchangeRate:
    """A dataclass to represent an exchange rate."""

    result: str
    """The result of the exchange rate."""
    documentation: str
    """The documentation of the exchange rate."""
    terms_of_use: str
    """The terms of use of the exchange rate."""
    time_last_update_unix: int
    """The time of the last update of the exchange rate in UNIX format."""
    time_last_update_utc: str
    """The time of the last update of the exchange rate in readable format."""
    time_next_update_unix: int
    """The time of the next update of the exchange rate in UNIX format."""
    time_next_update_utc: str
    """The time of the next update of the exchange rate in readable format."""
    base_code: accepted_currencies
    """The base code of the exchange rate."""


@dataclass
class SingleExchangeRate(ExchangeRate):
    """A dataclass to represent an exchange rate for a single conversion."""

    conversion_rates: dict[accepted_currencies, float]
    """The conversion rates of the exchange rate."""


@dataclass
class PairConversionExchangeRate(ExchangeRate):
    """A dataclass to represent an exchange rate for a pair conversion."""

    target_code: accepted_currencies
    """The target code of the exchange rate."""
    conversion_rate: float
    """The conversion rate of the exchange rate."""
    conversion_result: float | None = None
    """The conversion result of the exchange rate."""


class ExchangeRateAPI:
    """ExchangeRate-API wrapper"""

    def __init__(self, api_key: str = EXCHANGERATE_API_KEY) -> None:
        self.base_url = "https://v6.exchangerate-api.com/v6"
        self.session = None
        self.api_key = api_key
        self.headers = {"User-Agent": USER_AGENT}

    async def __aenter__(self) -> "ExchangeRateAPI":
        """Enter the async context manager"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the async context manager"""
        await self.close()

    async def close(self) -> None:
        """Close the aiohttp session"""
        await self.session.close()

    @staticmethod
    def _define_error_message(error_type: str) -> str:
        """
        Define the error message from the error type

        Args:
            error_type (str): The error type

        Returns:
            str: The error message
        """
        match error_type:
            case "unsupported-code":
                return "The currency code is not supported."
            case "malformed-request":
                return "The request was not formatted correctly."
            case "invalid-key":
                return "The API key is not valid."
            case "inactive-account":
                return "The API key is not active."
            case "quota-reached":
                return "The monthly request limit has been reached."
            case _:
                return "An unknown error has occurred."

    async def _get_base_currency_rates(self, base_currency: accepted_currencies) -> SingleExchangeRate:
        """
        Get the exchange rates for a base currency

        Args:
            base_currency (accepted_currencies): The base currency to get the exchange rates for

        Raises:
            ProviderHttpError: If the request to the API fails

        Returns:
            SingleExchangeRate: The exchange rates for the base currency
        """
        async with self.session.get(f"{self.base_url}/{self.api_key}/latest/{base_currency}") as resp:
            cache_file_path = Cache.get_cache_file_path(
                f"{base_currency}.json")
            cached_data = Cache.read_cached_data(cache_file_path)
            if cached_data is not None:
                return SingleExchangeRate(**cached_data)
            if resp.status != 200:
                try:
                    data = await resp.json()
                    err_type = self._define_error_message(data["error-type"])
                    raise ProviderHttpError(err_type, resp.status)
                except BaseException as exc:
                    raise ProviderHttpError(resp.text(), resp.status) from exc
            data = await resp.json()
            if data["result"] == "error":
                err_type = self._define_error_message(data["error-type"])
                raise ProviderHttpError(err_type, resp.status)
            Cache.write_data_to_cache(data, cache_file_path)
            return SingleExchangeRate(**data)

    async def get_exchange_rate(self, base_currency: accepted_currencies, target_currency: accepted_currencies, amount: float) -> PairConversionExchangeRate:
        """
        Get the exchange rate for a pair conversion

        Args:
            base_currency (accepted_currencies): The base currency to get the exchange rate for
            target_currency (accepted_currencies): The target currency to get the exchange rate for
            amount (float): The amount to convert

        Raises:
            ProviderHttpError: If the request to the API fails

        Returns:
            PairConversionExchangeRate: The exchange rate for the pair conversion
        """
        try:
            base_currency_rates = await self._get_base_currency_rates(base_currency)
        except ProviderHttpError as exc:
            raise ProviderHttpError(exc.message, exc.status_code) from exc
        if target_currency not in base_currency_rates.conversion_rates:
            raise ProviderHttpError("The currency code is not supported.", 400)
        return PairConversionExchangeRate(
            result=base_currency_rates.result,
            documentation=base_currency_rates.documentation,
            terms_of_use=base_currency_rates.terms_of_use,
            time_last_update_unix=base_currency_rates.time_last_update_unix,
            time_last_update_utc=base_currency_rates.time_last_update_utc,
            time_next_update_unix=base_currency_rates.time_next_update_unix,
            time_next_update_utc=base_currency_rates.time_next_update_utc,
            base_code=base_currency_rates.base_code,
            target_code=target_currency,
            conversion_rate=base_currency_rates.conversion_rates[target_currency],
            conversion_result=amount *
            base_currency_rates.conversion_rates[target_currency],
        )

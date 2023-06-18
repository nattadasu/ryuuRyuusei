import os
import sys
import unittest

try:
    from classes.exchangeratesapi import (ExchangeRatesAPI,
                                          PairConversionExchangeRate)
except ImportError:
    sys.path.insert(0, os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")))
    from classes.exchangeratesapi import (ExchangeRatesAPI,
                                          PairConversionExchangeRate)


class ExchangeRatesAPITest(unittest.IsolatedAsyncioTestCase):
    """ExchangeRatesAPI test class"""

    async def test_get_exchange_rate(self):
        """Test getting an exchange rate"""
        async with ExchangeRatesAPI() as api:
            rate = await api.get_exchange_rate("USD", "IDR", 1)
            print(f"Rp. {rate.conversion_result}")
            self.assertIsInstance(rate, PairConversionExchangeRate)


if __name__ == "__main__":
    unittest.main()

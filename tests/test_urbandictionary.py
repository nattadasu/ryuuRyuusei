import os
import sys
import unittest

try:
    from classes.urbandictionary import UrbanDictionary, UrbanDictionaryEntry
except ImportError:
    # add the path to the 'modules' directory to the system path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from classes.urbandictionary import UrbanDictionary, UrbanDictionaryEntry


class UrbanDictionaryTest(unittest.IsolatedAsyncioTestCase):
    """UrbanDictionary API test class"""

    async def test_get_random_word(self):
        """Test getting random word"""
        async with UrbanDictionary() as ud:
            res = await ud.get_random_word()
            self.assertIsInstance(res, UrbanDictionaryEntry)

    async def test_get_word_of_the_day(self):
        """Test getting word of the day"""
        async with UrbanDictionary() as ud:
            res = await ud.get_word_of_the_day()
            self.assertIsInstance(res, UrbanDictionaryEntry)

    async def test_lookup_definition(self):
        """Test looking up definition"""
        async with UrbanDictionary() as ud:
            res = await ud.lookup_definition("python")
            self.assertIsInstance(res, list)
            self.assertIsInstance(res[0], UrbanDictionaryEntry)


if __name__ == "__main__":
    unittest.main(verbosity=2)

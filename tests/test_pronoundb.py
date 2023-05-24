import os
import unittest
import sys

try:
    from classes.pronoundb import PronounDB, PronounData
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from classes.pronoundb import PronounDB, PronounData


class PronounDbTest(unittest.IsolatedAsyncioTestCase):
    """Test the PronounDB class"""

    async def test_get_pronouns(self):
        """Test getting pronouns from PronounDB"""
        async with PronounDB() as pdb:
            pronoun = await pdb.get_pronouns(pdb.Platform.DISCORD, "384089845527478272")
        self.assertIsInstance(pronoun, PronounData)

    async def test_get_pronouns_bulk(self):
        """Test getting pronouns from PronounDB in bulk"""
        async with PronounDB() as pdb:
            pronouns = await pdb.get_pronouns_bulk(
                pdb.Platform.DISCORD, ["384089845527478272"]
            )
        self.assertIsInstance(pronouns, dict)


if __name__ == "__main__":
    unittest.main(verbosity=2)

import os
import sys
import unittest

try:
    from classes.anibrain import AniBrainAI
except ImportError:
    # add the path to the 'modules' directory to the system path
    sys.path.insert(
        0,
        os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..")))
    from classes.anibrain import AniBrainAI


class AniBrainAITest(unittest.IsolatedAsyncioTestCase):
    """AniBrainAI test class"""

    async def test_anime(self):
        """Test anime"""
        async with AniBrainAI() as ab:
            data = await ab.get_anime()
        self.assertTrue(data is not None)

    async def test_manga(self):
        """Test manga"""
        async with AniBrainAI() as ab:
            data = await ab.get_manga()
        self.assertTrue(data is not None)

    async def test_light_novel(self):
        """Test light novel"""
        async with AniBrainAI() as ab:
            data = await ab.get_light_novel()
        self.assertTrue(data is not None)

    async def test_one_shot(self):
        """Test one shot"""
        async with AniBrainAI() as ab:
            data = await ab.get_one_shot()
        self.assertTrue(data is not None)


if __name__ == "__main__":
    unittest.main(verbosity=2)

import json
import os
import sys
import unittest

try:
    from modules.i18n import (
        check_lang_exist,
        fetch_language_data,
        read_user_language,
        search_language,
        set_default_language,
    )
except ImportError:
    # add the path to the 'modules' directory to the system path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from modules.i18n import (
        check_lang_exist,
        fetch_language_data,
        read_user_language,
        search_language,
        set_default_language,
    )


class ctx:
    """Mock context class"""

    class author:
        """Mock author class"""

        id = None

    class guild:
        """Mock guild class"""

        id = None


class LanguageTest(unittest.IsolatedAsyncioTestCase):
    """Language test class"""

    def test_check_english(self):
        """Test checking if English exists"""
        self.assertTrue(check_lang_exist("en_US"))

    def test_search_english(self):
        """Test searching for English"""
        base = [
            {
                "code": "en_US",
                "name": "English",
                "native": "English",
                "dialect": "United States",
            },
        ]
        self.assertTrue(
            any(lang in base for lang in search_language("English")),
            "No matching language found",
        )

    def test_user_language(self):
        """Test reading user language"""
        ctx.author.id = 384089845527478272
        ctx.guild.id = 589128995501637655
        self.assertTrue(read_user_language(ctx) in ["en_US", "id_ID"])

    def test_language_json(self):
        """Test reading language JSON"""
        with open("i18n/en_US.json", "r") as f:
            base = json.load(f)
        self.assertEqual(fetch_language_data("en_US", useRaw=True), base)

    async def test_set_default_language(self):
        """Test setting default language"""
        ctx.author.id = 384089845527478272
        self.assertTrue(await set_default_language("en_US", ctx) is None)


if __name__ == "__main__":
    unittest.main(verbosity=2)

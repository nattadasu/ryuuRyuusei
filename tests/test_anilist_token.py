import os
import stat
import sys
import tempfile
import time
import unittest

try:
    from modules.anilist_token import (
        AniListToken,
        clear_token,
        ensure_fresh_token,
        get_authorize_url,
        get_valid_access_token,
        load_token,
        save_token,
        token_needs_refresh,
    )
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from modules.anilist_token import (
        AniListToken,
        clear_token,
        ensure_fresh_token,
        get_authorize_url,
        get_valid_access_token,
        load_token,
        save_token,
        token_needs_refresh,
    )


def _make_token(**overrides):
    now = time.time()
    data = {
        "access_token": "access123",
        "refresh_token": "refresh123",
        "expires_at": now + 86400,
        "updated_at": now,
    }
    data.update(overrides)
    return AniListToken(**data)


class AniListTokenTest(unittest.IsolatedAsyncioTestCase):
    """AniList token store test class (offline)"""

    def setUp(self):
        fd, self.path = tempfile.mkstemp()
        os.close(fd)
        os.unlink(self.path)
        self._env_backup = dict(os.environ)
        for key in (
            "ANILIST_ACCESS_TOKEN",
            "ANILIST_OAUTH_REFRESH",
            "ANILIST_OAUTH_EXPIRY",
            "ANILIST_REFRESH_TOKEN",
            "ANILIST_TOKEN_EXPIRY",
        ):
            os.environ.pop(key, None)

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)
        os.environ.clear()
        os.environ.update(self._env_backup)

    def test_save_load_roundtrip(self):
        """Test saving then loading a token"""
        token = _make_token()
        save_token(token, self.path)
        loaded = load_token(self.path)
        self.assertIsNotNone(loaded)
        assert loaded is not None
        self.assertEqual(loaded.access_token, "access123")
        self.assertEqual(loaded.refresh_token, "refresh123")
        self.assertAlmostEqual(loaded.expires_at or 0, token.expires_at or 0, places=3)

    def test_file_permissions(self):
        """Test token file is owner-only"""
        save_token(_make_token(), self.path)
        mode = stat.S_IMODE(os.stat(self.path).st_mode)
        self.assertEqual(mode, 0o600)

    def test_load_missing_returns_none(self):
        """Test loading without a token returns None"""
        self.assertIsNone(load_token(self.path))

    def test_clear_token(self):
        """Test logout deletes the token"""
        self.assertFalse(clear_token(self.path))
        save_token(_make_token(), self.path)
        self.assertTrue(clear_token(self.path))
        self.assertIsNone(load_token(self.path))

    def test_expires_in(self):
        """Test expiry math"""
        now = time.time()
        self.assertLess(_make_token(expires_at=now - 10).expires_in() or 0, 0)
        self.assertGreater(_make_token(expires_at=now + 100).expires_in() or 0, 0)
        self.assertIsNone(_make_token(expires_at=None).expires_in())

    def test_needs_refresh(self):
        """Test refresh decision matrix"""
        now = time.time()
        self.assertTrue(token_needs_refresh(_make_token(expires_at=now - 10)))
        self.assertTrue(token_needs_refresh(_make_token(expires_at=now + 100)))
        self.assertFalse(token_needs_refresh(_make_token(expires_at=now + 86400 * 30)))
        self.assertTrue(token_needs_refresh(_make_token(expires_at=None)))
        self.assertFalse(
            token_needs_refresh(_make_token(expires_at=None, refresh_token=""))
        )
        self.assertFalse(
            token_needs_refresh(_make_token(expires_at=now - 10, refresh_token=""))
        )

    def test_migrate_from_env(self):
        """Test one-time migration from legacy .env names"""
        os.environ["ANILIST_ACCESS_TOKEN"] = "env_access"
        os.environ["ANILIST_REFRESH_TOKEN"] = "env_refresh"
        os.environ["ANILIST_TOKEN_EXPIRY"] = str(int(time.time()) + 5000)
        loaded = load_token(self.path)
        self.assertIsNotNone(loaded)
        assert loaded is not None
        self.assertEqual(loaded.access_token, "env_access")
        self.assertEqual(loaded.refresh_token, "env_refresh")
        self.assertTrue(os.path.exists(self.path))
        os.environ.clear()
        reloaded = load_token(self.path)
        assert reloaded is not None
        self.assertEqual(reloaded.access_token, "env_access")

    def test_migrate_old_oauth_names(self):
        """Test migration also honors the ANILIST_OAUTH_* names"""
        os.environ["ANILIST_ACCESS_TOKEN"] = "old_access"
        os.environ["ANILIST_OAUTH_REFRESH"] = "old_refresh"
        os.environ["ANILIST_OAUTH_EXPIRY"] = str(int(time.time()) + 5000)
        loaded = load_token(self.path)
        assert loaded is not None
        self.assertEqual(loaded.refresh_token, "old_refresh")

    def test_authorize_url(self):
        """Test authorize URL shape"""
        url = get_authorize_url()
        self.assertIn("anilist.co/api/v2/oauth/authorize", url)
        self.assertIn("response_type=code", url)
        self.assertIn("client_id=", url)

    async def test_ensure_fresh_no_token(self):
        """Test task entrypoint without a token"""
        refreshed, message = await ensure_fresh_token(path=self.path)
        self.assertFalse(refreshed)
        self.assertIn("No AniList token", message)

    async def test_ensure_fresh_valid_token(self):
        """Test task entrypoint with a fresh token (no network)"""
        save_token(_make_token(expires_at=time.time() + 86400 * 30), self.path)
        refreshed, message = await ensure_fresh_token(path=self.path)
        self.assertFalse(refreshed)
        self.assertIn("still valid", message)

    async def test_valid_token_passthrough(self):
        """Test lazy accessor returns stored token without refresh"""
        save_token(_make_token(expires_at=time.time() + 86400 * 30), self.path)
        self.assertEqual(await get_valid_access_token(self.path), "access123")

    async def test_valid_token_missing(self):
        """Test lazy accessor without a token"""
        self.assertIsNone(await get_valid_access_token(self.path))


if __name__ == "__main__":
    unittest.main(verbosity=2)

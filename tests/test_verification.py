import os
import sys
import unittest

try:
    from classes.verificator import Verificator, VerificatorUser
except ImportError:
    # add the path to the 'modules' directory to the system path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from classes.verificator import Verificator, VerificatorUser


class AccountUuid(unittest.TestCase):
    """Account Verification test class"""

    def test_assign_uuid(self):
        """Test create UUID"""
        with Verificator() as verificator:
            user = verificator.save_user_uuid(123456789, "nattadasu")
            self.assertIsInstance(user, VerificatorUser)

    def test_get_user(self):
        """Test get user"""
        with Verificator() as verificator:
            user = verificator.get_user_uuid(123456789)
        self.assertTrue(user is not None)

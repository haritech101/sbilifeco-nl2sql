import sys

sys.path.append("./src")

from os import getenv
from unittest import IsolatedAsyncioTestCase
from dotenv import load_dotenv

# Import the necessary service(s) here
from sbilifeco.models.base import Response


class Test(IsolatedAsyncioTestCase):
    async def test_exc(self) -> None:
        try:
            x = 1 / 0
        except Exception as e:
            response = Response.error(e)
            self.assertFalse(response.is_success)
            self.assertEqual(response.code, 500)
            self.assertIn("division", response.message.lower())
            print(response.message)

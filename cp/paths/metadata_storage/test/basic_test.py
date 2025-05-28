import sys

sys.path.append("./src")

from unittest import TestCase
from sbilifeco.cp.paths.metadata_storage import Paths


class BasicTest(TestCase):
    def test_paths(self):
        self.assertTrue(Paths.BASE)

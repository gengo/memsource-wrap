import unittest
import random
import os


class ApiTestCase(unittest.TestCase):
    def gen_random_int(self):
        return random.randint(-100, 100)

    def setCleanUpFiles(self, clean_up_file_paths):
        self.clean_up_file_paths = clean_up_file_paths

    def tearDown(self):
        self._cleanUpFiles()

    def _cleanUpFiles(self):
        if hasattr(self, 'clean_up_file_paths'):
            remove_if_exists = lambda f: os.remove(f) if os.path.isfile(f) else None
            [remove_if_exists(f) for f in self.clean_up_file_paths]

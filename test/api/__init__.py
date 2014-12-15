import unittest
import random


class ApiTestCase(unittest.TestCase):
    def gen_random_int(self):
        return random.randint(-100, 100)

from memsource import models
import unittest


class TestModelsAsynchronousResponse(unittest.TestCase):
    def make_model(self, source):
        return models.AsynchronousResponse(source)

    def test_is_complete(self):
        self.assertFalse(self.make_model({}).is_complete())

        self.assertTrue(self.make_model({'error': None}).is_complete())

    def test_has_error(self):
        self.assertFalse(self.make_model({}).has_error())

        self.assertFalse(self.make_model({'error': None}).has_error())

        self.assertTrue(self.make_model({'error': {}}).has_error())

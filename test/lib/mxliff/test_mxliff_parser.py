import unittest
import os.path

from memsource.lib.mxliff import MxliffParser
from memsource import models


class TestMxliffParser(unittest.TestCase):
    def setUp(self):
        # Read test.mxliff file from same directory with this file.
        file_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(file_dir, 'test.mxliff')) as f:
            self.mxliff_text = f.read().encode()

        with open(os.path.join(file_dir, 'test_meta.mxliff')) as f:
            self.mxliff_text_meta = f.read().encode()

    def test_parse_no_meta(self):
        mxliff_units = MxliffParser().parse(self.mxliff_text)

        self.assertEqual(len(mxliff_units), 2)

        self.assertIsInstance(mxliff_units[0], models.MxliffUnit)

        self.assertEqual(mxliff_units[0], {
            'id': 'fj4ewiofj3qowjfw:0',
            'score': 0.0,
            'gross_score': 0.0,
            'source': 'Hello World.',
            'target': None,
            'machine_trans': None,
            'memsource_tm': None,
            'tunit_metadata': [],
        })

        self.assertIsInstance(mxliff_units[1], models.MxliffUnit)
        self.assertEqual(mxliff_units[1], {
            'id': 'fj4ewiofj3qowjfw:1',
            'score': 1.01,
            'gross_score': 1.01,
            'source': 'This library wraps Memsoruce API for Python.',
            'target': 'このライブラリはMemsourceのAPIをPython用にラップしています。',
            'machine_trans': 'This is machine translation.',
            'memsource_tm': 'This is memsource translation memory.',
            'tunit_metadata': [],
        })

    def test_parse_with_meta(self):
        mxliff_units = MxliffParser().parse(self.mxliff_text_meta)

        self.assertEqual(len(mxliff_units), 1)

        self.assertIsInstance(mxliff_units[0], models.MxliffUnit)

        self.assertEqual(mxliff_units[0], {
            'id': 'fj4ewiofj3qowjfw:0',
            'score': 0.0,
            'gross_score': 0.0,
            'source': 'Hello World.',
            'target': None,
            'machine_trans': None,
            'memsource_tm': None,
            'tunit_metadata': [{
                'id': '1',
                'type': 'term',
                'content': '<term>This is term.</term>',
            }, {
                'id': '2',
                'type': 'bracket',
                'content': '<bracket>This is bracket.</bracket>',
            }],
        })

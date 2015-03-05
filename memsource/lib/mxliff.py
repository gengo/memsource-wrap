from memsource import models
from lxml import objectify


class MxliffParser(object):
    """
    Parse xliff file of Memsource.
    """

    def parse(self, resource: {'XML file content as bytes': bytes}):
        root = objectify.fromstring(resource)
        memsource_namespace = root.nsmap['m']

        def to_memsouce_key(s: str) -> str:
            return '{{{}}}{}'.format(memsource_namespace, s)

        self.score_key = to_memsouce_key('score')
        self.gloss_score_key = to_memsouce_key('gross-score')
        self.tunit_metadata_key = to_memsouce_key('tunit-metadata')
        self.mark_key = to_memsouce_key('mark')
        self.type_key = to_memsouce_key('type')
        self.content_key = to_memsouce_key('content')

        return [
            self.parse_group(group) for group in root.file.body.getchildren()
        ]

    def parse_group(self, group: objectify.ObjectifiedElement) -> models.MxliffUnit:
        # Because we cannot write 'group.trans-unit'.
        trans_unit = getattr(group, 'trans-unit')
        source = {
            'id': trans_unit.attrib['id'],
            'score': float(trans_unit.attrib[self.score_key]),
            'gross_score': float(trans_unit.attrib[self.gloss_score_key]),
            'source': trans_unit.source.text,
            'target': trans_unit.target.text,
            'tunit_metadata': self.parse_tunit_metadata(trans_unit),
        }

        for alt_trans in getattr(trans_unit, 'alt-trans'):
            # machine-trans, memsource-tm -> machine_trans, memsource_tm
            source[alt_trans.attrib['origin'].replace('-', '_')] = alt_trans.target.text

        return models.MxliffUnit(source)

    def parse_tunit_metadata(self, trans_unit: objectify.ObjectifiedElement) -> list:
        tunit_metadata = getattr(trans_unit, self.tunit_metadata_key, None)

        # There is no meta data.
        if tunit_metadata is None:
            return []

        return [{
            'id': mark.attrib['id'],
            'type': getattr(mark, self.type_key).text,
            'content': getattr(mark, self.content_key).text,
        } for mark in getattr(tunit_metadata, self.mark_key)]

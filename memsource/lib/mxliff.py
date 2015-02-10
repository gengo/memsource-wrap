from memsource import models
from lxml import objectify


class MxliffParser(object):
    """
    Parse xliff file of Memsource.
    """

    def parse(self, resource: {'XML file content as bytes': bytes}):
        root = objectify.fromstring(resource)
        memsource_namespace = root.nsmap['m']

        return [
            self.parse_group(group, memsource_namespace) for group in root.file.body.getchildren()
        ]

    def parse_group(
            self,
            group: {objectify.ObjectifiedElement},
            memsource_namespace: {str}
    ) -> models.MxliffUnit:
        to_memsouce_key = lambda s: '{{{}}}{}'.format(memsource_namespace, s)

        # Because we cannot write 'group.trans-unit'.
        trans_unit = getattr(group, 'trans-unit')
        source = {
            'id': trans_unit.attrib['id'],
            'score': float(trans_unit.attrib[to_memsouce_key('score')]),
            'gross_score': float(trans_unit.attrib[to_memsouce_key('gross-score')]),
            'source': trans_unit.source.text,
            'target': trans_unit.target.text,
        }

        for alt_trans in getattr(trans_unit, 'alt-trans'):
            # machine-trans, memsource-tm -> machine_trans, memsource_tm
            source[alt_trans.attrib['origin'].replace('-', '_')] = alt_trans.target.text

        return models.MxliffUnit(source)

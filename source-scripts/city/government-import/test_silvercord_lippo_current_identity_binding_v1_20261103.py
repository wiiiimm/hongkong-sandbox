"""Adverse checks against the real frozen reviewed source/route records."""
import copy
import unittest
import silvercord_lippo_current_identity_binding_v1_20261103 as subject
from run import read


class CurrentIdentityBinding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read(subject.BASE/subject.RUNTIME/'selection.json.gz')['rows']

    def inputs(self, row):
        proof = read(subject.BASE/subject.IDENTITIES/row['uid'].split('/')[1]/'identity.json')
        return [proof, copy.deepcopy(row), [copy.deepcopy(r['source']) for r in self.rows],
                copy.deepcopy(proof['exactRouteTileHashes']), 'current-test-manifest',
                dict(path='historical-proof', sha256='historical-sha')]

    def test_both_complete_real_identities_rebind_without_altering_old_proof(self):
        for row in self.rows:
            args = self.inputs(row)
            old = copy.deepcopy(args[0])
            result = subject.bind_identity(*args)
            self.assertEqual(args[0], old)
            self.assertEqual(result['exactRouteManifestSHA256'], 'current-test-manifest')
            self.assertFalse(result['providerObjectIdExact'])
            self.assertFalse(result['physicalAccepted'])
            self.assertEqual(result['rawCurrentIdentity'], old['rawCurrentIdentity'])

    def test_changed_source_route_tile_or_record_rejected(self):
        for row in self.rows:
            for kind in ['source', 'tile', 'record', 'duplicate', 'missing']:
                args = self.inputs(row)
                if kind == 'source': args[1]['sourceSHA256'] = 'changed'
                elif kind == 'tile': args[3][next(iter(args[3]))] = 'changed'
                elif kind == 'record':
                    next(s for s in args[2] if s['building']['uid'] == row['uid'])['building']['rings'] = []
                elif kind == 'duplicate': args[2].append(copy.deepcopy(args[1]['source']))
                else: args[2] = [s for s in args[2] if s['building']['uid'] != row['uid']]
                with self.assertRaises(AssertionError, msg=kind): subject.bind_identity(*args)

    def test_failed_identity_and_false_provider_equality_cannot_gain_credit(self):
        for key, value in [('passed', False), ('identityAccepted', False),
                           ('providerObjectIdExact', True), ('completeRecordProjection', False)]:
            args = self.inputs(self.rows[0]); args[0][key] = value
            with self.assertRaises(AssertionError, msg=key): subject.bind_identity(*args)


if __name__ == '__main__': unittest.main()

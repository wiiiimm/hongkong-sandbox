"""Validation plus opt-in Neon tests; fixtures are unique and never delete shared history."""
import concurrent.futures
import os
import time
import unittest
import uuid

import reservations as r
from db import connect


class ValidationTests(unittest.TestCase):
    def test_sorted_stable_keys(self):
        self.assertEqual(r.normalise(['building:b','building:a','building:b']), ['building:a','building:b'])
        for resources in ([], [''], [' building:a'], ['a'] * 0):
            with self.assertRaises(ValueError): r.normalise(resources)

    def test_ttl_and_owner_required(self):
        for owner, ttl in (('', 900), ('owner', 0), ('owner', 3601), ('owner', 1.5), ('owner', True)):
            with self.assertRaises(ValueError): r.validate(owner, ttl)

    def test_takeover_requires_reason_and_full_snapshot(self):
        with self.assertRaises(ValueError): r.takeover('new', ['fixture:a'], {'fixture:a': None}, '')
        with self.assertRaises(ValueError): r.takeover('new', ['fixture:a'], {}, 'Operator request')


@unittest.skipUnless(os.getenv('MODELLING_INTEGRATION_TEST') == '1', 'Live tests require opt-in')
class NeonReservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): r.migrate()

    def setUp(self):
        self.prefix = 'reservation-test:' + uuid.uuid4().hex
        self.receipts = []

    def claim(self, owner, keys, **kwargs):
        result = r.claim(owner, keys, **kwargs)
        if result['ok']: self.receipts.append(result['reservation'])
        return result

    def tearDown(self):
        # Release only still-owned fixture groups. Expired or superseded audit history remains.
        for receipt in self.receipts: r.release(receipt)

    def test_cross_batch_parallel_claim_and_all_or_nothing(self):
        a, b = self.prefix + ':a', self.prefix + ':b'
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(lambda n: r.claim('session-' + str(n), [a, b], batch='batch-' + str(n)), range(2)))
        winners = [result['reservation'] for result in outcomes if result['ok']]
        self.receipts.extend(winners)
        self.assertEqual(len(winners), 1)
        self.assertEqual([result['error'] for result in outcomes if not result['ok']], ['reserved'])
        c = self.prefix + ':c'
        self.assertFalse(self.claim('partial', [a, c])['ok'])
        self.assertEqual(r.status([c])['resources'], [])
        self.assertTrue(r.heartbeat(winners[0])['ok'])
        self.assertTrue(r.owns(winners[0]))
        forged = {**winners[0], 'owner': 'other-session'}
        self.assertFalse(r.release(forged)['ok'])

    def test_expiry_reclaim_fences_old_token(self):
        key = self.prefix + ':expire'
        old = self.claim('same-owner', [key], ttl=1)['reservation']
        time.sleep(1.2)
        new = self.claim('same-owner', [key])['reservation']
        self.assertNotEqual(new['token'], old['token'])
        self.assertGreater(new['generations'][key], old['generations'][key])
        self.assertFalse(r.heartbeat(old)['ok'])
        self.assertFalse(r.release(old)['ok'])
        self.assertFalse(r.owns(old))
        self.assertTrue(r.owns(new))
        with connect() as con:
            self.assertEqual(con.execute('SELECT action FROM astra_modelling.reservation_events WHERE token=%s', (new['token'],)).fetchone()[0], 'reclaim')

    def test_takeover_partial_group_fences_heartbeat_and_audits_reason(self):
        a, b = self.prefix + ':a', self.prefix + ':b'
        old = self.claim('missing-agent', [a, b])['reservation']
        before = r.status([a])
        new = r.takeover('operator-session', [a], before['expectedTokens'], 'User requested recovery of missing agent')
        self.assertTrue(new['ok'])
        self.receipts.append(new['reservation'])
        self.assertFalse(r.heartbeat(old)['ok'])
        self.assertFalse(r.release(old)['ok'])
        self.assertFalse(r.owns(old))
        self.assertTrue(r.owns(new['reservation']))
        # The untouched member is neither stolen nor renewed by a lost group's heartbeat.
        remaining = r.status([b])['resources'][0]
        self.assertEqual(remaining['token'], old['token'])
        self.assertEqual(remaining['lease_until'], old['lease_until'])
        with connect() as con:
            action, actor, reason, previous = con.execute('SELECT action,actor,reason,previous FROM astra_modelling.reservation_events WHERE token=%s', (new['reservation']['token'],)).fetchone()
        self.assertEqual((action, actor), ('takeover', 'operator-session'))
        self.assertIn('missing agent', reason)
        self.assertEqual(previous[0]['token'], str(old['token']))
        # Deliberately reclaim remaining fixture member using its current snapshot, then release.
        cleanup = r.takeover('fixture-cleanup', [b], r.status([b])['expectedTokens'], 'Release this test fixture only')
        self.receipts.append(cleanup['reservation'])

    def test_compare_and_swap_race_and_no_partial_takeover(self):
        a, b = self.prefix + ':a', self.prefix + ':b'
        self.claim('original', [a, b])
        expected = r.status([a, b])['expectedTokens']
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(lambda n: r.takeover('replacement-' + str(n), [a, b], expected, 'Recovery race fixture'), range(2)))
        winners = [result['reservation'] for result in outcomes if result['ok']]
        self.receipts.extend(winners)
        self.assertEqual(len(winners), 1)
        self.assertEqual([result['error'] for result in outcomes if not result['ok']], ['ownership-changed'])
        current = r.status([a,b])['expectedTokens']
        self.assertEqual(len(set(current.values())), 1)
        stale = {**current, b: expected[b]}
        self.assertFalse(r.takeover('stale', [a, b], stale, 'Stale scope fixture')['ok'])
        self.assertEqual(r.status([a,b])['expectedTokens'], current)


if __name__ == '__main__': unittest.main()

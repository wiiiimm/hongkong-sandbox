import concurrent.futures
import json
import pathlib
import sqlite3
import tempfile
import subprocess
import sys
import time
import unittest
import inventory
import selection
import runner


class TrialTest(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root = pathlib.Path(t.name)
        self.db = self.root/'test.sqlite'
        self.buildings = [dict(uid=f'landsd/{i}:0', id=f'landsd/{i}', objectId=i, buildingCSUID=f'cs{i}',
                              name='Landmark' if i == 1 else '', tile='0_0', centre=[i, 1], base=0,
                              height=5, heightSource='estimated', rings=[[[i-1, 0], [i+1, 0], [i, 2]]]) for i in [1, 2]]
        self.write('city/data/tile.json', dict(id='0_0', buildings=self.buildings))
        self.write('city/data/manifest.json', dict(counts={'buildings': 2}, tiles=[dict(id='0_0', url='city/data/tile.json', counts={'buildings': 2})]))
        self.write('city/data/review-sections.json', dict(sections=[dict(id='01.1', polygons=[dict(rings=[[[0, 0], [2, 0], [2, 2], [0, 2]]])])]))
        inventory.sync(self.root, self.db)
        self.config = dict(name='trial', areas=[dict(id='a', title='A', bounds=[0, 0, 1, 2]), dict(id='b', title='B', section='01.1')], landmarks=[dict(id='l', title='Landmark', records=[dict(uid='landsd/1:0', objectId=1, csuid='cs1', name='Landmark')])])

    def write(self, path, data):
        p = self.root/path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data))

    def selected(self):
        return selection.select(self.db, self.config)[0]

    def test_intersections_overlap_and_ids(self):
        s = self.selected()
        self.assertEqual(s['buildings'], 2)  # Includes a footprint whose centre is outside A.
        self.assertEqual(s['areas'][0]['count'], 2)
        self.assertFalse(s['exceptions'])
        self.assertEqual(self.selected()['membershipSHA256'], s['membershipSHA256'])
        self.config['landmarks'][0]['records'][0]['csuid'] = 'wrong'
        self.assertEqual(self.selected()['exceptions'][0]['reason'], 'identity-missing-or-changed')

    def test_hole_does_not_select_inner_building(self):
        self.config['areas'] = [dict(id='hole', title='Hole', bounds=[.8, .8, 1.2, 1.2])]
        self.buildings[0]['rings'] = [[[0, 0], [2, 0], [2, 2], [0, 2]], [[.5, .5], [1.5, .5], [1.5, 1.5], [.5, 1.5]]]
        self.write('city/data/tile.json', dict(id='0_0', buildings=self.buildings))
        inventory.sync(self.root, self.db)
        s = self.selected()
        self.assertNotIn('landsd/1:0', s['areas'][0]['uids'])  # Explicit landmark still included separately.

    def test_plan_noop_and_overlap_jobs_shared(self):
        self.selected()
        self.assertEqual(runner.plan(self.db, 'trial', dry_run=True)['new'], 2)
        runner.plan(self.db, 'trial')
        self.assertEqual(runner.run(self.db, 'trial')['status'], {'complete': 2})
        self.assertEqual(runner.plan(self.db, 'trial')['alreadyComplete'], 2)
        self.config['name'] = 'adjacent'
        self.selected()
        self.assertEqual(runner.plan(self.db, 'adjacent')['alreadyComplete'], 2)

    def test_process_crash_recovered_after_lease_expiry(self):
        self.selected()
        runner.plan(self.db, 'trial')
        code = "import runner,sys,os; runner.claim(sys.argv[1], 'trial', 'crashed-process'); os._exit(23)"
        child = subprocess.run([sys.executable, '-c', code, str(self.db)], cwd=pathlib.Path(runner.__file__).parent)
        self.assertEqual(child.returncode, 23)
        # Advance claim time rather than making the test sleep through a real lease.
        recovered = runner.claim(self.db, 'trial', 'recovery', now=time.time()+31)
        self.assertEqual(recovered['owner'], 'crashed-process')
        self.assertTrue(runner.finish(self.db, recovered, 'recovery', result=runner.audit_input(json.loads(recovered['payload']))))
        self.assertEqual(runner.run(self.db, 'trial')['status'], {'complete': 2})
        self.assertEqual(runner.plan(self.db, 'trial')['alreadyComplete'], 2)

    def test_concurrent_claims_and_expired_owner(self):
        self.selected()
        runner.plan(self.db, 'trial')
        with concurrent.futures.ThreadPoolExecutor(2) as e:
            jobs = list(e.map(lambda owner: runner.claim(self.db, 'trial', owner, now=100), ['a', 'b']))
        self.assertNotEqual(jobs[0]['id'], jobs[1]['id'])
        reclaimed = runner.claim(self.db, 'trial', 'new', now=200)
        old_owner = 'a' if reclaimed['id'] == jobs[0]['id'] else 'b'
        self.assertFalse(runner.finish(self.db, reclaimed, old_owner, result={}))
        self.assertTrue(runner.finish(self.db, reclaimed, 'new', result={}))

    def test_changed_input_invalidates_only_changed_job(self):
        self.selected()
        runner.plan(self.db, 'trial')
        runner.run(self.db, 'trial')
        self.buildings[0]['height'] = 6
        self.write('city/data/tile.json', dict(id='0_0', buildings=self.buildings))
        inventory.sync(self.root, self.db)
        with self.assertRaisesRegex(ValueError, 'stale'):
            runner.run(self.db, 'trial')
        self.selected()
        with self.assertRaisesRegex(ValueError, 'stale'):
            runner.run(self.db, 'trial')
        p = runner.plan(self.db, 'trial')
        self.assertEqual((p['new'], p['alreadyComplete']), (1, 1))

    def test_attempt_limit_and_permanent_failure(self):
        self.selected()
        runner.plan(self.db, 'trial')
        j = runner.claim(self.db, 'trial', 'a', now=100)
        runner.finish(self.db, j, 'a', error='invalid input')
        for n in range(3):
            j = runner.claim(self.db, 'trial', 'b', now=1000+n*100)
            self.assertIsNotNone(j)
        self.assertIsNone(runner.claim(self.db, 'trial', 'b', now=2000))
        self.assertEqual(runner.report(self.db, 'trial')['status'], {'failed': 2})


if __name__ == '__main__':
    unittest.main()

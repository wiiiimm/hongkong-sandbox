"""Actual saved finalization refs/commands/schemas; no source geometry calculations."""
import copy,unittest
from pathlib import Path
import heritage165054_owned_saved_output_finalization_v1_20261014 as a

class SavedFinalization(unittest.TestCase):
    def test_every_diagnostic_reference_resolves_actual_saved_bytes(self):
        refs=a.referenced_files();self.assertEqual(len(refs),10)
        for q in refs:self.assertTrue(a.check(q).is_file())
        d=a.diagnostic_refs();self.assertEqual(d['all22PriorSourceBelowMinus05WarningsRetained'],a.ref(a.prior.nomination.CONTEXT))
        self.assertTrue(str(a.prior.nomination.CONTEXT).endswith('exact-saved-source-clamp-and-lowrim-context.json.gz'))
    def test_actual_complete_command_arrays_and_no_wrong_or_failed_command_credit(self):
        rows=[a.read(a.prior.DOC/('command-'+str(i).zfill(3)+'.json')) for i in range(2)];a.bind_completed_commands(rows)
        for key,value in [('exitCode',1),('command',['node','other.mjs'])]:
            changed=copy.deepcopy(rows);changed[0][key]=value
            with self.assertRaises(AssertionError):a.bind_completed_commands(changed)
    def test_actual_failed_released_terminal_binding_and_lease_lost_failclosed(self):
        t=a.read(a.TERMINAL);a.bind_terminal(t);t['leaseStillOwned']=True
        with self.assertRaises(AssertionError):a.bind_terminal(t)
    def test_saved_strict_true_does_not_erase_numeric_reason(self):
        m,v,strict,clear,reasons=a.assess_saved();self.assertTrue(strict);self.assertTrue(clear)
        self.assertEqual(reasons,['terrain-intersects-source-over-0.5m']);self.assertEqual(m['rows'][0]['checks'],59406)
        self.assertEqual(m['rows'][0]['missingTerrain'],0);self.assertEqual(v['results'][0]['concerns'],[])
if __name__=='__main__':unittest.main()

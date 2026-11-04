"""Saved scope and actual preclaim failure control flow; no DB/source math."""
import contextlib,io,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import heritage165054_authentic_tin_owned_ordinary_v3_20261014 as a
import heritage165054_authentic_tin_owned_ordinary_v2_20261014 as v2

class OwnedResources(unittest.TestCase):
    def actors(self):
        return a.read(a.nomination.prior.north.DOC/'proposal-input.json')['scope']['allActorsForNominationLease']
    def test_exact_saved45_context_retained_and_only_owned3_leased(self):
        actors=self.actors();p=a.read(a.V2_PROPOSAL/'draft-pins.json')
        self.assertEqual(v2.resources(actors),p['canonicalResources']);self.assertEqual(len(p['canonicalResources']),91)
        keys=a.resources(actors);self.assertEqual(keys,sorted(['building:'+a.UID,'terrain-patch:'+a.UID,'immutable-source-proof:'+a.BATCH]))
        self.assertEqual(len(a.qualification_resources(actors)),91)
        rows=a.read(a.V2_PROPOSAL/'ROOT-reservation-overlap.json')
        active={q['resource'] for q in rows if q['active']}
        self.assertEqual(len(active),6);self.assertFalse(active.intersection(keys))
        self.assertEqual({q['batch'] for q in rows if q['active']},{'government-xl-polyu-complete-saved-actor-finite-v1-20261014'})
    def test_missing_owned_actor_fails_closed(self):
        actors=self.actors();actors[actors.index(a.UID)]='landsd/999999999:0'
        with self.assertRaises(AssertionError):a.resources(sorted(actors))
    def test_actual_main_claim_denial_preserves_only_safe_diagnostics(self):
        import run
        claim=dict(ok=False,error='reserved',conflicts=[dict(resource='building:landsd/193086:0',batch='active-batch',owner='secret-owner',token='secret-token')])
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/'proposal').mkdir();out=io.StringIO()
            with patch.object(a,'PROPOSAL',p/'proposal'),patch.object(a,'DOC',p/'doc'),patch.object(a,'LOCAL',p/'local'),patch.object(a,'load',return_value=({'canonicalResources':a.resources(self.actors())},None)),patch.object(a,'read',return_value={'passed':True}),patch.object(run.reservations,'claim',return_value=claim) as mock,patch.object(a.sys,'argv',['caller','--check-owned-on-private-authentic-tin-only']),contextlib.redirect_stdout(out):
                with self.assertRaisesRegex(RuntimeError,'reservation denied'):a.main()
            mock.assert_called_once();saved=json.loads((p/'proposal'/'claim-denied-attempt.json').read_text())
            self.assertEqual(saved['conflicts'],[dict(resource='building:landsd/193086:0',batch='active-batch')]);self.assertFalse(saved['workerOwnedPhaseStarted']);self.assertFalse(saved['modelFailure'])
            self.assertNotIn('secret',out.getvalue());self.assertNotIn('secret',json.dumps(saved));self.assertFalse((p/'doc').exists());self.assertFalse((p/'local').exists())
if __name__=='__main__':unittest.main()

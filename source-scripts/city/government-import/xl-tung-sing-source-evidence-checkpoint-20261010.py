"""Freeze exact Tung Sing raw/current/primary/source/HA identity inputs."""
import importlib.util
from run import ROOT,HERE,read,save,digest
from yoho_eight_current_bound_identity_20261009 import stream_pin
from test_tung_sing_adjacent_original_envelope_identity_20261010 import EVIDENCE,D,ROW,REL,DOC
BATCH=REL.name

def main():
 assert not (REL/'result.json').exists()
 raw=read(DOC/'selection.json.gz');forms=read(DOC/'all-current-forms.json.gz');podium=HERE/'local/xl-terrain-recovery-20261009-support-original-recovery/assets/368ec3bcb2b011f8db942a2e294f500043762b15851e55113c95443a48ff5f15.glb.gz'
 save(REL/'current-inputs.json.gz',{'manifestSHA256':raw['manifestSHA256'],'forms':forms['forms'],'tileHashes':forms['tileHashes'],'podiumOriginalPath':str(podium.relative_to(ROOT))})
 save(REL/'original-source-lookup.json.gz',EVIDENCE)
 save(REL/'complete-original-stream-pins.json.gz',{'tower':stream_pin((ROOT/ROW['candidate']['path']).read_bytes(),ROW['modelId'],11445),'podium':stream_pin(podium.read_bytes(),'B341711135802063C0',432)})
 save(REL/'selection.json.gz',raw)
 (REL/'README.md').write_text("""# Tung Sing / Lei Tung exact original relationship inputs

The Housing Authority's 2021 estate layout uniquely names Tung Sing House as Block E next to the Commercial Complex (Carpark Under); the separate floor/key plan corroborates the complete trident building shape. These primary plans support only the named adjacent envelope interpretation. They establish no legal ownership, occupation-permit relationship, surveyed vertical precision or load-bearing support. Exact current government queries return no OP structure relationships.

The untouched original Tower has 11,445 faces and 365 components; every one of its 65 faces contributing to the 20.583241 m² raw current podium overlap belongs to the complete 3,878-face original mainbody. The complete original 432-face commercial source has 21 positive-dimensional line interfaces with that mainbody. Contact is not physical acceptance.

Fresh ordinary whole-cell identity fails only the two unrelated-overlap reasons; current/provider 95% coverage and 10 m extent remain strict. Source/root/BIN/all stream pins, complete nearby current forms, current manifest/tiles, native source versions and primary provider raw/decoded requests are captured. All source surfaces, other current actors and raw failures remain unchanged. The named contract and its negative tests are separately reviewable; this input checkpoint accepts no identity, physics or installation.

Primary source URLs:
- https://www.housingauthority.gov.hk/hdw/content/static/file/b5/residential/plans/estate/Lei%20Tung%20Estate.pdf
- https://www.housingauthority.gov.hk/hdw/content/static/file/b5/residential/plans/leitungestate_tungsinghouse.pdf
- https://www.linkreit.com/-/media/corporate-website/investor-relations/financial-report/2007/an_rpt_2007_en.pdf
""")
 s=importlib.util.spec_from_file_location('tung_sing_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 paths=[q for q in DOC.rglob('*') if q.is_file()]+[ROOT/k for k in D['inputHashes']]+[ROOT/ROW['candidate']['path'],Path(__file__)]
 paths+=[HERE/q for q in ['xl-tung-sing-lei-tung-source-relationship-20261010.py','xl-tung-sing-original-overlap-visuals-20261010.py','xl-tung-sing-current-full-cell-preflight-20261010.py','tung_sing_adjacent_original_envelope_identity_20261010.py','test_tung_sing_adjacent_original_envelope_identity_20261010.py']]
 m.freeze(BATCH,'exact-original-primary-ha-envelope-inputs-v1',paths,{'uids':D['uids'],'identityAccepted':False,'physicalAccepted':False,'rawIdentityReasons':read(DOC/'raw-full-cell-proof.json')['reasons'],'completeOriginalFaces':[11445,432],'completeTowerComponents':365,'exactOriginalPositiveContacts':21,'allRawOverlapFacesRetained':65,'sourceIdentityReviewUsedAI':True,'remainingReason':'named-source-envelope-current-bound-adapter-and-full-physical-checks-not-yet-complete'})
if __name__=='__main__':
 from pathlib import Path
 main()

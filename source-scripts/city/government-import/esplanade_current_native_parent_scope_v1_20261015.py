"""Rebind complete cached native bounds against Esplanade's whole parent cells."""
from pathlib import Path
import importlib.util
from run import ROOT,HERE,read,save,digest,connect
from heritage_saved_native_bounds_binding_v1_20261014 import encoded,closed_disjoint
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-esplanade-current-native-parent-scope-v1-20261015';DOC=BASE/BATCH
PRIOR=BASE/'government-xl-heritage165054-saved-current-native-bounds-reconciliation-v1-20261014';PHYSICAL=BASE/'government-xl-esplanade-pair-current-physical-v3-20261015'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 saved=read(PRIOR/'complete6653-current-native-bounds-reconciliation.json.gz');manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==saved['currentManifestSHA256'];entries={};paths=[Path(__file__),PRIOR/'result.json',PRIOR/'complete6653-current-native-bounds-reconciliation.json.gz',manifest,HERE/'heritage_saved_native_bounds_binding_v1_20261014.py']
 for url in read(manifest)['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;paths.append(p);cat=read(p);assert cat['rootTranslation']==[-834500,0,816500]
  for e in cat['models']:assert e['uid']not in entries;entries[e['uid']]=e
 assert len(entries)==len(saved['rows'])==6653 and set(entries)=={x['uid']for x in saved['rows']}
 candidate=read(PHYSICAL/'terrain-candidates.json')[0];patch=read(ROOT/candidate['path']);assert digest((ROOT/candidate['path']).read_bytes())==candidate['sha256'];parent=ROOT/'3d-viewer/city/data/terrain.json';spec=importlib.util.spec_from_file_location('esplanade_extent',HERE/'xl-second-pass.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);domain=m.resolution.extent(patch['coarseCells'],read(parent));assert list(domain)==candidate['bounds'];rows=[]
 for x in saved['rows']:
  assert encoded(entries[x['uid']])==encoded(x['currentRawEntry']);boxes=x['completeFourUnusedWorldBoundsVerbatim'];rows.append(dict(uid=x['uid'],sourceSHA256=x['sourceSHA256'],wholeUnusedFourWorldBounds=boxes,strictlyOutsideParentDomain=closed_disjoint(boxes,domain)))
 touching=[x['uid']for x in rows if not x['strictlyOutsideParentDomain']];save(DOC/'scope.json.gz',dict(currentManifestSHA256=digest(manifest.read_bytes()),parentCoarseCells=patch['coarseCells'],parentDomain=domain,completeCurrentNativeModels=6653,touchingNativeUids=touching,rows=rows,nativeBoundsNominationOnly=True,fullBASICAndExteriorRegressionStillRequired=True,installationApproved=False))
 paths +=[PHYSICAL/'terrain-candidates.json',ROOT/candidate['path'],parent,HERE/'xl-second-pass.py',Path(m.resolution.__file__)]
 for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 spec=importlib.util.spec_from_file_location('esplanade_scope_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);f.freeze(BATCH,'whole-parent-complete-current-native-bounds-scope-v1',paths,dict(uids=['landsd/268828:0','landsd/309385:0'],completeCurrentNativeModels=6653,touchingNativeUids=touching,fullAcceptance=False));print('Touching native actors:',touching,flush=True)
if __name__=='__main__':main()

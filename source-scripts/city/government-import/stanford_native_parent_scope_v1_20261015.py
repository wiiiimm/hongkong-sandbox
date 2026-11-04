"""Bind complete current native bounds to the full Stanford replacement rectangle."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from heritage_saved_native_bounds_binding_v1_20261014 import bind_record,closed_disjoint
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-stanford-native-parent-scope-v1-20261015';DOC=BASE/BATCH
PRIOR=BASE/'government-xl-complete-current-native-actual-position-matrix-bounds-v6-20261015'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 refs=[Path(__file__),PRIOR/'result.json',HERE/'heritage_saved_native_bounds_binding_v1_20261014.py'];pins={}
 for q in r['evidenceRefs']:
  p=ROOT/q['path'];assert digest(p.read_bytes())==q['sha256'];refs.append(p);pins[q['path']]=q['sha256']
 inv=read(PRIOR/'inventory.json.gz');decl=read(PRIOR/'input.json.gz');manifestpath=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifestpath.read_bytes())==decl['currentManifest']['sha256'];manifest=read(manifestpath);entries={}
 for url in manifest['officialModelCatalogues']:
  for e in read(ROOT/'3d-viewer'/url)['models']:assert e['uid']not in entries;entries[e['uid']]=e
 assert len(entries)==inv['successfullyCapturedActors']==len(inv['rows'])==6662 and not inv['errors'];assert inv['startAndEndInputHashesVerified']
 for p,h in inv['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 declarations={x['uid']:x for x in decl['rows']};inputpath=BASE/'government-xl-stanford-basic-ground-capture-v1-20261015/input.json.gz';inp=read(inputpath);domain=inp['domain'];refs.append(inputpath);rows=[]
 for x in inv['rows']:
  d=declarations[x['uid']];boxes=bind_record(entries[x['uid']],d,x);rows.append({'uid':x['uid'],'sourceSHA256':x['sourceSHA256'],'completeUnusedFourWorldBounds':boxes,'strictlyOutsideParentDomain':closed_disjoint(boxes,domain)})
 touching=[x['uid']for x in rows if not x['strictlyOutsideParentDomain']];DOC.mkdir();save(DOC/'scope.json.gz',{'domain':domain,'cells':inp['cells'],'rows':rows,'completeCurrentNativeModels':6662,'touchingNativeUids':touching,'installationApproved':False})
 module('freeze_stanford_native_scope',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-current6662-native-parent-domain-nomination-v1',refs,{'uids':['landsd/305584:0','landsd/335875:0'],'touchingNativeUids':touching,'fullAcceptance':False});print({'touchingNativeUids':touching},flush=True)
if __name__=='__main__':main()

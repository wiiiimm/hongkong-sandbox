"""Associate one exact original with its pinned viewer record; no placement approval."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-fuying181489-exact-source-association-review-v1-20261029';UID='landsd/181489:0';SHA='bffdf5653f4dd01917b4028e0cd2f0559fcdb3ce960a4d7cabd5a0392b9ae163'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={};evidence={}
 def take(n,p):
  if n not in pins:r,pins[n]=authenticate(BASE/n);refs.append(BASE/n/'result.json');evidence[n]=r['jobId']
  assert ref(p)['sha256']==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 runtime='government-xl-fuying181489-five-member-runtime-v2-20261029';selection=take(runtime,BASE/runtime/'selection.json.gz');row=next(r for r in selection['rows']if r['uid']==UID);assert row['sourceSHA256']==SHA==digest((ROOT/row['candidate']['path']).read_bytes());refs.append(ROOT/row['candidate']['path'])
 old='government-xl-fuying-peninsula-after-depot-current-v1-20261029-identity';identity=take(old,BASE/old/'181489:0/identity.json');assert identity['sourceSHA256']==SHA and identity['exactCurrentComponentRoute']['qualified']
 form=row['source']['building'];path=ROOT/'3d-viewer'/row['source']['tile'];assert ref(path)['sha256']==row['source']['tileSHA256']and [b for b in read(path)['buildings']if b['uid']==UID]==[form];refs.append(path)
 route=identity['exactCurrentComponentRoute'];assert route['source']['building']==form and route['official']['objectId']==form['objectId']==181489 and route['official']['buildingCSUID']==form['buildingCSUID']=='3400521011T20050430'
 assert identity['geographicCell']['targetCoversWholeCell']and identity['geographicCell']['originalProjectionCoversWholeCell']and identity['exactWholeCellCoverage']['covered']
 assert form['structureType']=='Tower'and row['candidate']['entry']['modelId']==row['native']['model']['modelId']=='B340052101101063C0'and row['native']['model']['triangles']==14692
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s',(row['native']['cacheKey'],)).fetchone()==(row['native']['resultSha'],)
 profile='government-xl-fuying181489-complete-excess-height-context-v1-20261029';distance=take(profile,BASE/profile/'summary.json');assert distance['sourceSHA256']==SHA and distance['allVerticesAccounted']and distance['wholeOriginalFaces']==14692
 viewed=[]
 for name in ['government-xl-fuying233291-basic-contact-views-v1-20261029','government-xl-fuying50662-native-contact-views-v1-20261029']:
  take(name,BASE/name/'summary.json')
  for image in (BASE/name).glob('*.png'):assert ref(image)['sha256']==pins[name][str(image.relative_to(ROOT))];refs.append(image);viewed.append(ref(image))
 assert len(viewed)==2
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)['sha256']==selection['manifestSHA256'];refs.append(manifest)
 result=dict(uids=[UID],sourceSHA256ByUid={UID:SHA},currentManifest=ref(manifest),sourceForm=ref(path),sourceCSUID=form['buildingCSUID'],sourceBuildingId=form['buildingId'],sourceModelId=row['native']['model']['modelId'],wholeOriginalFaces=14692,exactSourceAssociationAccepted=True,sourceEvidenceInterpretationUsedAI=True,sourceGeometryChanges=0,sourcePoseChanges=0,rawIdentityReasons=identity['reasons'],evidence=evidence,imagesActuallyViewed=viewed,identityAccepted=False,physicalAcceptance=False,visualAcceptance=False,installationApproved=False,publication=False,qualification='Exact pinned original root/file/GeoRef Tower route, source SHA/face count/current viewer UID-CSUID-buildingId and whole1m cell establish source association. This is not a live CSDI lookup or blanket spatial-identity override. All4raw footprint/excess warnings remain for physical/source-role review. ROOT inspected the full source/native and focused BASIC-post diagrams; low authored canopies explain the long-distance source vertex profile but do not by themselves approve contacts, whole facet roles, walking collision or visual placement. No source, metadata, scale or height edits and no publication approval.')
 save(out/'summary.json',result);module('fuying_source_association_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-pinned-original-source-association-only-no-placement-approval',refs,result)
if __name__=='__main__':main()

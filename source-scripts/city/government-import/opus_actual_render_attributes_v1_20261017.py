"""Lossless companion preparation and complete three-part renderer capture."""
from pathlib import Path
import sys,zipfile,subprocess,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from require_remaining_xl import require_remaining
sys.path.insert(0,str(HERE.parent/'enhancement-screening'))
from shape_prepare import _convert_one
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-opus-actual-render-attributes-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PAIR=BASE/'government-xl-opus-pair-foundation-v2-20261016';COMP=BASE/'government-xl-opus-companion-original-v1-20261016';UID='landsd/319559:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists() and not LOCAL.exists()
 count=BASE/'government-xl-sham-shui-po-pool-original-installed-v1-20261017/full-xl-current-count.json'
 require_remaining(count,'landsd/322573:0','e3c4ad4fff2acda8844233c83b6885dbbd73c1da9acb0a0efc7ec9778f57d764')
 pins={};evidence=[]
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [PAIR,COMP]:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);evidence.append(ref(d/'result.json'))
   for x in r['evidenceRefs']:pins.setdefault(x['path'],set()).add(x['sha256'])
 def consume(p):
  r=ref(p);assert r['sha256'] in pins[r['path']],r['path'];evidence.append(r);return read(p)
 selection=consume(PAIR/'selection.json.gz')['rows'];original=consume(COMP/'original-geometry.json.gz')
 actors=BASE/'government-xl-opus-basic-ground-capture-v1-20261016/basic-actors.json.gz';building=next(x['building'] for x in consume(actors)['rows'] if x['uid']==UID)
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);tileurl=next(t['url'] for t in manifest['tiles'] if t['id']==building['tile']);tile=ROOT/'3d-viewer'/tileurl;assert building in read(tile)['buildings'];evidence.append(ref(tile))
 claim=reservations.claim('opus-render-'+str(uuid.uuid4()),['building:'+x for x in [UID,'landsd/248432:0','landsd/322573:0']],batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();LOCAL.mkdir();packed=LOCAL/'packed';packed.mkdir()
  archivepath=HERE/'local'/COMP.name/'original/11-SW-14D.zip'
  with zipfile.ZipFile(archivepath) as z:
   for info in z.infolist():
    if info.is_dir():continue
    old=HERE/'local'/COMP.name/'decoded'/info.filename
    assert digest(z.read(info)) in pins[str(old.relative_to(ROOT))];assert ref(old)['sha256'] in pins[str(old.relative_to(ROOT))];evidence.append(ref(old))
   entry=next(i for i in z.infolist() if i.filename.endswith('.gltf'))
   converted=_convert_one(z,entry,LOCAL/'decoded',packed,{},dict(modelId='B359791447501063C0'))
  assert converted['triangles']==208 and all(converted['runtimeFormatChecks'].values())
  asset=packed/converted['asset']['asset'];tri=decode_original_world_triangles(asset.read_bytes());old=np.array(original['position']).reshape(-1,3)[np.array(original['index']).reshape(-1,3)];assert np.array_equal(tri,old)
  save(DOC/'companion-conversion.json',converted)
  ce={**converted['asset'], 'uid':UID,'modelId':converted['modelId'],'buildingCSUID':building['buildingCSUID'],'objectId':building['objectId'],'sourceTile':'11-SW-14D','triangles':208,'worldBounds':converted['worldBounds'],'rootTranslation':[-834500,0,816500],'placementReviewed':False,'publicationApproved':False,'sourceIdentityReviewed':False,'priority':'unreviewed'}
  rows=[]
  for s in selection:
   p=ROOT/s['candidate']['path'];assert digest(p.read_bytes())==s['sourceSHA256'];b=s['source']['building'];t=ROOT/'3d-viewer'/next(t['url'] for t in manifest['tiles'] if t['id']==b['tile']);assert b in read(t)['buildings'];evidence.append(ref(t));rows.append(dict(uid=s['uid'],entry=s['candidate']['entry'],building=b,path=str(p.relative_to(ROOT))))
  rows.append(dict(uid=UID,entry=ce,building=building,path=str(asset.relative_to(ROOT))))
  save(DOC/'input.json.gz',dict(rows=rows,expected={r['uid']:[r['entry']['sha256'],r['entry']['triangles']] for r in rows},currentManifest=ref(manifestpath),currentCatalogueRefs=[ref(ROOT/'3d-viewer'/u) for u in manifest['officialModelCatalogues']],evidenceRefs=evidence,qualification='Read-only renderer capture; companion UID is a diagnostic candidate, not identity or publication approval.'))
  tool=HERE/'opus_actual_render_attributes_v1_20261017.mjs'
  with (DOC/'capture.log').open('w') as log:subprocess.run(['node',str(tool),str((DOC/'input.json.gz').relative_to(ROOT)),str((DOC/'attributes.json.gz').relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
  out=read(DOC/'attributes.json.gz');assert out['startEndAllInputsVerified'] and sum(len(r['completeOriginalIndex'])//3 for r in out['rows'])==13557
  refs=[Path(__file__),tool,HERE/'exact_packed_world_geometry_20261009.py',HERE/'require_remaining_xl.py',count,HERE.parent/'citywide-native/convert.py',*[ROOT/x['path'] for x in evidence],*[p for p in LOCAL.rglob('*') if p.is_file()]]
  for p,h in out['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
  assert reservations.owns(lease)
  r=module('opus_attributes_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-opus-three-part-renderer-attributes-v1',list(dict.fromkeys(refs)),dict(uids=[r['uid'] for r in rows],completeFaces=13557,companionOriginalGeometryExact=True,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=r['jobId'],completeFaces=13557,companionOriginalGeometryExact=True),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

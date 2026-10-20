"""Current full-source identity checks; no acceptance waiver or source edits."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sol-city-neighbour-identity-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;SRC=BASE/'government-xl-sol-city-companion-sources-v1-20261021'
def main():
 assert not DOC.exists();refs=[Path(__file__)];rows=[];summary=[];hashes={};nominations=[]
 recovery=BASE/'government-xl-sol-city-remaining-recovery-v1-20261021';_,rpins=authenticate(recovery);rp=recovery/'recovery.json';assert digest(rp.read_bytes())==rpins[str(rp.relative_to(ROOT))];refs.extend([recovery/'result.json',rp]);assets={r['uid']:r for r in read(rp)['rows']}
 for version in [1,2]:
  folder=BASE/f'government-xl-sol-city-remaining-neighbours-v{version}-20261021';_,pins=authenticate(folder);p=folder/'nominations.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.extend([folder/'result.json',p]);nominations.extend(read(p)['rows'])
 assert len(nominations)==4
 for n in nominations:
  uid=n['uid'];m=n['model'];b=n['source']['building'];source=dict(n['source']);tile=ROOT/'3d-viewer'/source['tile'];assert next(x for x in read(tile)['buildings']if x['uid']==uid)==b;source['tileSHA256']=digest(tile.read_bytes());refs.append(tile);hashes[str(tile.relative_to(ROOT))]=source['tileSHA256']
  path=ROOT/assets[uid]['assetPath'];assert digest(path.read_bytes())==m['asset']['sha256'];refs.append(path);hashes[str(path.relative_to(ROOT))]=m['asset']['sha256']
  entry=dict(n['candidate'],**m['asset'],uid=uid,modelId=m['modelId'],worldBounds=m['worldBounds'],triangles=m['triangles'],rootTranslation=[-834500,0,816500],recordedBaseHeight=b.get('baseHeightHKPD'),recordedTopHeight=b.get('topHeightHKPD'),placementReviewed=False,publicationApproved=False)
  row=dict(uid=uid,modelId=m['modelId'],sourceSHA256=m['asset']['sha256'],triangles=m['triangles'],source=source,native=dict(cacheKey=n['nativeStageKey'],resultSha=n['nativeStageSHA256'],model=m),candidate=dict(path=str(path.relative_to(ROOT)),entry=entry));rows.append(row)
  tri=decode_original_world_triangles(path.read_bytes());assert len(tri)==row['triangles'];final=module('siu_identity_context',HERE/'xl-final-script-pass.py');lo,hi=tri.min((0,1)),tri.max((0,1));near=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);tiles={t:digest((ROOT/'3d-viewer'/t).read_bytes())for _,_,t in near};context=dict(sourceSHA256=row['sourceSHA256'],identity=final.identity_context(row,tri,near),neighbourTileHashes=tiles);folder=DOC/uid.split('/')[1];save(folder/'context.json',context)
  proof=verify_files(row,context,LOCAL/uid.split('/')[1]);save(folder/'identity.json',proof);summary.append(dict(uid=uid,passed=proof['passed'],reasons=proof['reasons']));print(summary[-1],flush=True)
  for t,h in tiles.items():hashes['3d-viewer/'+t]=h;refs.append(ROOT/'3d-viewer'/t)
 save(DOC/'selection.json.gz',dict(rows=rows,manifestSHA256=digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())))
 for p,h in hashes.items():assert digest((ROOT/p).read_bytes())==h
 refs.extend(p for p in LOCAL.rglob('*')if p.is_file());refs.extend([HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'china_ferry_current_foundations_v1_20261020.py'])
 result=dict(uids=[r['uid']for r in rows],rows=summary,installationApproved=False);save(DOC/'summary.json',result);module('siu_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'four-neighbour-fresh-complete-original-identity',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()

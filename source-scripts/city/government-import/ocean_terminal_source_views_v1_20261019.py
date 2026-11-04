"""Source-only Ocean Terminal views; preserves raw failures, grants no acceptance."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-ocean-terminal-source-views-v1-20261019'
DOC=BASE/BATCH
CAP=BASE/'government-xl-ocean-terminal-private-ground-v2-20261018'
FACES=BASE/'government-xl-ocean-terminal-contact-faces-v1-20261018'
UID='landsd/205767:0'
def main():
 assert not DOC.exists()
 refs=[Path(__file__)]; pins={}
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [CAP,FACES]:
   receipt=read(folder/'result.json')
   assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
   refs.append(folder/'result.json')
   for e in receipt['evidenceRefs']:
    pins.setdefault(e['path'],set()).add(e['sha256'])
 # Bind exact historical source/diagnostic inputs only; old manifest/terrain
 # results are context, not evidence of present-day installation acceptance.
 selection=CAP/'selection.json.gz';facespath=FACES/'faces.json'
 for p in [selection,facespath]:
  assert digest(p.read_bytes()) in pins[str(p.relative_to(ROOT))]
  refs.append(p)
 row=read(selection)['rows'][0];assert row['uid']==UID
 faces=read(facespath);assert faces['sourceSHA256']==row['sourceSHA256']
 buried=[f for f in faces['faces'] if f['fullyBuried']]
 assert [f['faceId'] for f in buried]==[27545,27546,27547,27548]
 asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
 final=module('ocean_views_forms',HERE/'xl-final-script-pass.py')
 forms=final.load_forms([500,-960,940,-750]); refs.append(HERE/'xl-final-script-pass.py')
 for _,_,tile in forms: refs.append(ROOT/'3d-viewer'/tile)
 source=dict(assetPath=row['candidate']['path'],sourceSHA256=row['sourceSHA256'],worldBounds=row['candidate']['entry']['worldBounds'],triangles=row['triangles'])
 models=[]
 for name,frame,direction in [('whole',None,[.7,.8,1]),('whole-reverse',None,[-.7,.8,-1]),('landward',[[820,0,-945],[920,42,-765]],[1,.7,0]),('buried-front',[[898,1,-837],[913,12,-822]],[1,.4,1]),('buried-reverse',[[898,1,-837],[913,12,-822]],[-1,.3,-1])]:
  models.append(dict(**source,uid='review/'+name,forms=[b for b,_,_ in forms],reviewFrame=frame,viewDirection=direction,highlightFaces=[f['vertices'] for f in buried]))
 tool=HERE/'ocean_terminal_source_views_v1_20261019.mjs';refs.append(tool)
 refs=list(dict.fromkeys(refs)); hashes={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in refs}
 save(DOC/'input.json',dict(models=models,inputHashes=hashes,historicalPlacementOnly=True))
 subprocess.run(['node',str(tool),'--inputs',str((DOC/'input.json').relative_to(ROOT)),'--out',str(DOC.relative_to(ROOT))],cwd=ROOT,check=True)
 report=read(DOC/'render.json');assert len(report['views'])==5 and not report['errors']
 for p,h in {**hashes,**report['inputHashes']}.items():
  assert digest((ROOT/p).read_bytes())==h,p
  refs.append(ROOT/p)
 module('ocean_source_view_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'ocean-terminal-original-landward-and-buried-face-views',list(dict.fromkeys(refs)),dict(uids=[UID],views=5,installationApproved=False,rawBuriedFaceIds=faces['fullyBuriedFaceIds'],historicalPlacementOnly=True))
if __name__=='__main__':main()

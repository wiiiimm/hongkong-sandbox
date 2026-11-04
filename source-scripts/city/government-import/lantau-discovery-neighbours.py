"""Freeze every source form intersecting the bounded Discovery Bay patch for regression checks."""
import gzip,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/government-import/government-lantau-discovery-native-probe-20260921';UID='landsd/176056:0'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(gzip.compress((json.dumps(v,sort_keys=True)+'\n').encode(),mtime=0))
def main():
 patch=read(HERE/'local/government-lantau-discovery-native-probe-20260921/government-native-176056-0.json');g=patch['meta']['georef'];x=g['bE']-834500;z=816500-g['bN'];extent=[min(x,x+(patch['w']-1)*g['aE']),min(z,z-(patch['h']-1)*g['aN']),max(x,x+(patch['w']-1)*g['aE']),max(z,z-(patch['h']-1)*g['aN'])]
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');installed={m['uid'] for u in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/u)['models']};rows=[];hashes={}
 for tile in manifest['tiles']:
  b=tile['bounds']
  if b[2]<extent[0] or b[0]>extent[2] or b[3]<extent[1] or b[1]>extent[3]:continue
  path=ROOT/'3d-viewer'/tile['url'];hashes['3d-viewer/'+tile['url']]=sha(path)
  for form in read(path)['buildings']:
   if not form.get('rings'):continue
   xs=[p[0] for p in form['rings'][0]];zs=[p[1] for p in form['rings'][0]]
   if max(xs)<extent[0] or min(xs)>extent[2] or max(zs)<extent[1] or min(zs)>extent[3]:continue
   rows.append({'building':form,'patchIndexes':[0],'existingNative':form['uid'] in installed})
 terrain=read(DOC/'terrain-candidates.json')[0];out={'candidateIds':[UID],'inputHashes':hashes,'patches':[{'path':terrain['path'],'sha256':terrain['sha256'],'uids':[UID]}],'rows':rows,'extent':extent,'aiCalls':0}
 save(DOC/'neighbour-inputs.json.gz',out);print(json.dumps({'forms':len(rows),'existingNative':sum(r['existingNative'] for r in rows),'extent':extent}))
if __name__=='__main__':main()

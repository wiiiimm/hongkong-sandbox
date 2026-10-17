"""Keep the prior Club Galaxy grid verbatim while extending native terrain around it."""
import json,pathlib,sys,hashlib,math
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/residual-support-review';sys.path.insert(0,str(ROOT/'source-scripts/city/assembly-support-review'));import terrain_patches as t
read=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();bundle=read(DOC/'terrain-patches.json');exact=read(DOC/'exact-tin.json');oldURL='city/data/terrain-lohas-club-galaxy.json';old=read(ROOT/'3d-viewer'/oldURL);oldBB=t.bounds(old);oldSampler=t.fine.DemSampler(old,rendered=True);proof=[]
for parent in bundle['bundles']:
 for row in parent['patches']:
  path=ROOT/row['path'];patch=read(path)
  if patch['meta']['targetUids'][0]=='landsd/111608:0':
   g=patch['meta']['georef'];x0,z0,x1,z1=t.bounds(patch);protected=blended=0
   for r in range(patch['h']):
    z=z0+r
    for c in range(patch['w']):
     x=x0+c;i=r*patch['w']+c
     if oldBB[0]<=x<=oldBB[2] and oldBB[1]<=z<=oldBB[3]:
      j=round(z-oldBB[1])*old['w']+round(x-oldBB[0])
      for key in ['elev','renderedElev','vegetation']:patch[key][i]=old[key][j]
      protected+=1
     else:
      cx=max(oldBB[0],min(oldBB[2],x));cz=max(oldBB[1],min(oldBB[3],z));distance=math.hypot(x-cx,z-cz)
      if distance<10 and r not in (0,patch['h']-1) and c not in (0,patch['w']-1):
       weight=distance/10;value=patch['renderedElev'][i]*weight+oldSampler.ground(cx,cz)*(1-weight);patch['renderedElev'][i]=round(value,6)
       if patch['elev'][i]>0:patch['elev'][i]=round(value,6)
       blended+=1
   assert protected==old['w']*old['h'];patch['meta']['replacesExistingManifestPatches']=[oldURL];patch['meta']['preservedTerrain']={'url':oldURL,'sha256':sha(ROOT/'3d-viewer'/oldURL),'nodes':protected,'fields':['elev','renderedElev','vegetation'],'transitionOutsideMetres':10};patch['meta']['source']['policy']+=' Existing Club Galaxy grid nodes remain bit-for-bit equal in all three fields; only the new outside collar blends to that retained edge.';path.write_text(json.dumps(patch,separators=(',',':'))+'\n');row['sha256']=sha(path);row['replacesExistingManifestPatches']=[oldURL];proof.append({'uid':'landsd/111608:0','preservedNodes':protected,'blendedOutsideNodes':blended,'oldSHA256':sha(ROOT/'3d-viewer'/oldURL)})
  elif patch['meta']['targetUids'][0]in ['landsd/234162:0','landsd/265478:0']:
   e=next(p for p in exact['patches']if p['rows'][0]['uid']==patch['meta']['targetUids'][0]);assert e['missingProjectedAreaM2']<1e-6;row['path']=e['path'];row['sha256']=e['sha256']
  check=next(c for c in bundle['checks']if c['rows'][0]['uid']==patch['meta']['targetUids'][0]);check['patch']=row['path']
(DOC/'terrain-bundle.json').write_text(json.dumps(bundle,indent=2)+'\n');(DOC/'preservation.json').write_text(json.dumps({'issue':'HKS-214','rows':proof,'policy':'LOHAS and partial-coverage northern patch use the validated sampled grid with explicit unchanged-context handling. Island Resort and Pacifica retain exact native facets.'},indent=2)+'\n');print(json.dumps(proof))

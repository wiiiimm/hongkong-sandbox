"""Decouple the supported Capitol assembly from the unresolved Le Prestige neighbour."""
import json,pathlib,sys,hashlib,copy,shutil
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/residual-support-review/capitol';DEST=HERE/'capitol';DOC.mkdir(exist_ok=True);DEST.mkdir(exist_ok=True);read=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n');sys.path.insert(0,str(ROOT/'source-scripts/city/assembly-support-review'));import terrain_patches as t
sys.path.insert(0,str(ROOT/'source-scripts/city/shared-modelling'));import reservations;lease=read(pathlib.Path('/tmp/astra-capitol-lease.json'));assert reservations.owns(lease);reservations.heartbeat(lease)
source=HERE/'terrain-patches/support-native-111608-0.json';p=read(source);oldURL='city/data/terrain-lohas-club-galaxy.json';old=read(ROOT/'3d-viewer'/oldURL);parent=read(ROOT/'3d-viewer/city/data/terrain.json');sampler=t.fine.DemSampler(parent,rendered=True);raw=t.fine.DemSampler(parent);before=copy.deepcopy(p);x0,z0,x1,z1=t.bounds(p);oldBB=t.bounds(old);newz1=oldBB[3];h=int(newz1-z0)+1;p['h']=p['meta']['georef']['H']=h;p['coarseCells'][3]-=round((z1-newz1)/70);p['id']='support-native-capitol-decoupled';p['meta']['targetUids']=['landsd/111608:0','landsd/262368:0'];p['meta']['source']['policy']+=' Decoupled on whole parent cells before the unresolved ancillary building; new edge transitions to the current parent except protected prior Club Galaxy nodes.';p['meta']['derivedFrom']={'path':str(source.relative_to(ROOT)),'sha256':sha(source)}
for key in ['elev','renderedElev','vegetation']:p[key]=p[key][:h*p['w']]
changed=0;preserved=0
for r in range(h):
 z=z0+r
 for c in range(p['w']):
  x=x0+c;i=r*p['w']+c
  if oldBB[0]<=x<=oldBB[2] and oldBB[1]<=z<=oldBB[3]:
   j=round(z-oldBB[1])*old['w']+round(x-oldBB[0]);assert all(p[k][i]==old[k][j]for k in ['elev','renderedElev','vegetation']);preserved+=1;continue
  if h-1-r<10:
   alpha=(h-1-r)/10;value=round(p['renderedElev'][i]*alpha+sampler.ground(x,z)*(1-alpha),6);p['renderedElev'][i]=value
   if p['elev'][i]>0:p['elev'][i]=value
   changed+=1
assert preserved==29751;path=DEST/'terrain.json';path.write_text(json.dumps(p,separators=(',',':'))+'\n');bundle={'bundles':[{'parentTerrainURL':'city/data/terrain.json','parentSha256':sha(ROOT/'3d-viewer/city/data/terrain.json'),'patches':[{'path':str(path.relative_to(ROOT)),'sha256':sha(path),'uids':p['meta']['targetUids'],'coarseCells':p['coarseCells'],'replacesExistingManifestPatches':[oldURL]}]}]};support={r['uid']:r for r in read(ROOT/'docs/astra-city/residual-support-review/support-terrain.json')['rows']};fine=t.fine.DemSampler(p,rendered=True);checks=[]
for uid in p['meta']['targetUids']:
 gaps=[q['position'][1]-fine.ground(q['position'][0],q['position'][2])for q in support[uid]['rim']];checks.append({'uid':uid,'samples':len(gaps),'within2m':sum(abs(v)<=2 for v in gaps),'gapRange':[min(gaps),max(gaps)]})
bundle['checks']=[{'patch':str(path.relative_to(ROOT)),'rows':checks,'eligibleForBrowserValidation':all(r['within2m']==r['samples']for r in checks)}];write(DOC/'terrain-bundle.json',bundle);write(DOC/'preservation.json',{'oldNodesPreserved':preserved,'newBoundaryNodesBlended':changed,'excludedAncillaryUid':'landsd/272501:0','oldBounds':[x0,z0,x1,z1],'newBounds':t.bounds(p),'sourceSHA256':sha(source),'newSHA256':sha(path),'oldInstalledSHA256':sha(ROOT/'3d-viewer'/oldURL)})
uids={'landsd/'+str(n)+':0'for n in [111608,262368,109587,109595,109600,109603]};cat=read(HERE/'candidates/catalogue.json');cat['models']=[m for m in cat['models']if m['uid']in uids];cat['counts']['packedModels']=len(cat['models']);assert len(cat['models'])==6
for m in cat['models']:shutil.copyfile(HERE/'candidates'/m['asset'],DEST/m['asset'])
write(DEST/'catalogue.json',cat);selection=read(HERE/'visual-selection.json');selection['parts']=[r for r in selection['parts']if r['uid']in uids];write(DEST/'selection.json',selection)
for name in ['neighbours','browser']:
 s=(HERE/(name+'.mjs')).read_text().replace('docs/astra-city/residual-support-review/terrain-bundle.json','docs/astra-city/residual-support-review/capitol/terrain-bundle.json').replace('docs/astra-city/residual-support-review/neighbours.json','docs/astra-city/residual-support-review/capitol/neighbours.json').replace('source-scripts/city/residual-support-review/visual-selection.json','source-scripts/city/residual-support-review/capitol/selection.json').replace("base='source-scripts/city/residual-support-review/candidates/'","base='source-scripts/city/residual-support-review/capitol/'").replace('docs/astra-city/residual-support-review/framing/','docs/astra-city/residual-support-review/capitol/framing/');(HERE/('capitol-'+name+'.generated.mjs')).write_text(s)
print(json.dumps({'models':6,'bounds':t.bounds(p),'preservedNodes':preserved}))

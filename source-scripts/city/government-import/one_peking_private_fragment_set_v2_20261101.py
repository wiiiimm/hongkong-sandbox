"""Build a private disjoint rectangle partition of two old leaves and validated inset.
No publisher/validator changes, source building edits or acceptance. Exact source
clipping is retained in lineage; all new internal seams are measured separately.
"""
import copy
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from rectangular_native_fragments_v1_20261101 import intersection,subtract,cut,drawn,pack
from coordinated_native_boundary_v1_20261023 import seam_segments,compatible_seam
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-one-peking-after-twin-';BATCH=P+'private-fragment-set-v2-20261101';URL='city/data/government-xl-academy69025-nested-original-terrain-20261029.json'
def extent(n):
 g=n['meta']['georef'];return[g['bE']-834500,816500-g['bN'],g['bE']-834500+(n['w']-1)*g['aE'],816500-g['bN']-(n['h']-1)*g['aN']]
def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
 def take(batch,path):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 cap=P+'two-leaf-parent-capture-v2-20261101';summary=take(cap,BASE/cap/'summary.json');parentpath=ROOT/'3d-viewer'/URL;parent=take(cap,parentpath);assert len(parent['patches'])==17
 rootbatch=P+'root-grid-classification-v1-20261101';root_context=take(rootbatch,BASE/rootbatch/'summary.json');assert root_context['completeFaceAndMultiplicityPartition'];root_grid=take(rootbatch,HERE/'local'/rootbatch/'root-grid.json')
 insetbatch=P+'private-original-inset-v1-20261101';receipt,pins[insetbatch]=authenticate(BASE/insetbatch);refs.append(BASE/insetbatch/'result.json');assert receipt['status']=='private-terrain-validator-passed'and receipt['terrainTriangles']==12578
 inset=take(insetbatch,ROOT/receipt['candidate']['path']);domain=extent(inset);assert domain==[952.5,-1017.5,1092.5,-877.5];source=drawn(inset)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(manifest.read_bytes());assert msha==summary['currentManifestSHA256']==root_context['currentManifestSHA256'];refs.append(manifest);out.mkdir();old={i:drawn(parent['patches'][i])for i in [12,15]};pieces=[];oldboxes=[]
 for i in [12,15]:
  node=parent['patches'][i];box=extent(node);oldboxes.append(box)
  for j,b in enumerate(subtract(box,domain)):pieces.append(dict(name=f'old-{i}-outside-{j}',bounds=b,beforeSource=f'old-{i}',afterSource=f'old-{i}',template=node,beforeKind='exact-current-native-fragment',new=False))
  b=intersection(box,domain);assert b;pieces.append(dict(name=f'inset-in-{i}',bounds=b,beforeSource=f'old-{i}',afterSource='inset',template=inset,beforeKind='exact-current-native-fragment',new=True))
 remaining=[domain]
 for box in oldboxes:remaining=[part for b in remaining for part in subtract(b,box)]
 for j,b in enumerate(remaining):pieces.append(dict(name=f'inset-new-root-{j}',bounds=b,beforeSource='grid',afterSource='inset',template=inset,beforeKind='exact-current-root-grid-fragment',new=True))
 assert len(pieces)==8;rectangles=[shapely.box(*p['bounds'])for p in pieces];union=shapely.union_all(rectangles);expected=shapely.union_all([shapely.box(*b)for b in oldboxes]+[shapely.box(*domain)]);assert union.equals(expected)and sum(r.area for r in rectangles)==union.area
 meshes={**{f'old-{i}':v for i,v in old.items()},'inset':source,'grid':np.asarray(root_grid['triangles'],dtype='<f8')};members={};packed={};lineage={};rootgeo=parent['meta']['georef'];parent_sha=digest(parentpath.read_bytes())
 def node_for(piece,faces,kind):
  b=piece['bounds'];template=piece['template'];g=template['meta']['georef'];cell=template['cell'];assert cell>0 and g['aE']==cell and g['aN']==-cell
  c0=(b[0]+834500-g['bE'])/cell;r0=(b[1]-816500+g['bN'])/cell;w=(b[2]-b[0])/cell+1;h=(b[3]-b[1])/cell+1;assert all(float(v).is_integer()for v in [c0,r0,w,h]);c0,r0,w,h=map(int,[c0,r0,w,h]);assert c0>=0 and r0>=0 and c0+w<=template['w']and r0+h<=template['h']
  grid=copy.deepcopy(template);grid.pop('patches',None);grid.pop('hydro',None);grid.pop('patchExclusions',None);grid['id']='private-one-peking-'+piece['name']+'-'+kind;grid.update(w=w,h=h,cell=cell)
  for field in ['elev','vegetation','renderedElev']:
   if field in template:grid[field]=[v for row in range(r0,r0+h)for v in template[field][row*template['w']+c0:row*template['w']+c0+w]]
  cells=[(b[0]+834500-rootgeo['bE'])/parent['cell'],(b[1]-816500+rootgeo['bN'])/parent['cell'],(b[2]+834500-rootgeo['bE'])/parent['cell'],(b[3]-816500+rootgeo['bN'])/parent['cell']];assert all(float(x).is_integer()for x in cells);grid['coarseCells']=list(map(int,cells));grid['meta']['georef']={**g,'bE':834500+b[0],'bN':816500-b[1],'W':w,'H':h};grid['meta']['parentTerrain']=URL;grid['meta']['parentSha256']=parent_sha
  if not piece['new']:grid['meta']['targetUids']=list(template['meta']['targetUids'])
  else:grid['meta']['targetUids']=receipt['uids']
  pos,ix=pack(faces);grid['nativeMesh']={'position':pos,'index':ix,'source':dict(policy='private-exact-current-native-partition-and-validated-original-inset',verticalDatum='HKPD',verticalScale=1,sourceBody=piece['afterSource']if kind=='after'else piece['beforeSource'],privateDiagnosticOnly=True)}
  return grid
 for piece in pieces:
  before,bl=cut(meshes[piece['beforeSource']],piece['bounds']);after,al=cut(meshes[piece['afterSource']],piece['bounds']);assert before and after
  bn=node_for(piece,before,'before');an=node_for(piece,after,'after');beforepath=out/(piece['name']+'-before.json');afterpath=out/(piece['name']+'-after.json');save(beforepath,bn);save(afterpath,an);refs.extend([beforepath,afterpath]);packed[piece['name']]=drawn(an);lineage[piece['name']]=dict(bounds=piece['bounds'],beforeSource=piece['beforeSource'],afterSource=piece['afterSource'],before=bl,after=al)
  members[piece['name']]=dict(bounds=piece['bounds'],beforeKind=piece['beforeKind'],oldLeaf=int(piece['beforeSource'].split('-')[1])if piece['beforeSource'].startswith('old-')else None,before=dict(path=str(beforepath.relative_to(ROOT)),sha256=digest(beforepath.read_bytes())),candidate=dict(path=str(afterpath.relative_to(ROOT)),sha256=digest(afterpath.read_bytes())),beforeFaces=len(before),afterFaces=len(after),outsideInsetSourceRetained=not piece['new'])
 seams=[]
 for ia,a in enumerate(pieces):
  for b in pieces[ia+1:]:
   edge=shapely.box(*a['bounds']).boundary.intersection(shapely.box(*b['bounds']).boundary)
   if edge.is_empty or edge.geom_type=='Point':continue
   assert edge.geom_type=='LineString'and edge.length>0;coords=list(edge.coords);xs={p[0]for p in coords};axis=0 if len(xs)==1 else 2;coordinate=coords[0][0 if axis==0 else 1];ts=[p[1 if axis==0 else 0]for p in coords];lo,hi=min(ts),max(ts)
   try:report=compatible_seam(seam_segments(packed[a['name']],axis,coordinate,lo,hi),seam_segments(packed[b['name']],axis,coordinate,lo,hi),lo,hi);passed=True;error=None
   except AssertionError as e:report=None;passed=False;error=str(e)
   seams.append(dict(members=[a['name'],b['name']],axis=axis,coordinate=coordinate,lower=lo,upper=hi,passesExistingOneCentimetreFiniteSeam=passed,report=report,error=error))
 save(out/'lineage.json.gz',lineage);save(out/'seams.json',dict(rows=seams));result=dict(uids=receipt['uids'],currentManifestSHA256=msha,parentURL=URL,parentSHA256=parent_sha,members=members,partitionRectanglesExactlyDisjoint=True,partitionCoversOldLeavesAndInsetExactly=True,internalSharedEdges=len(seams),passedFiniteSeams=sum(r['passesExistingOneCentimetreFiniteSeam']for r in seams),allFiniteSeamsPassed=all(r['passesExistingOneCentimetreFiniteSeam']for r in seams),sourceGeometryChanges=0,sourcePoseChanges=0,buildingGeometryChanges=0,terrainRepartitioned=True,sourceAccepted=False,physicalAcceptance=False,canonicalTerrainValidationPassed=False,installationApproved=False,publication=False,qualification=__doc__+' No marker/parent/current-public bytes are changed. Existing private inset limits remain binding; a separate complete partition retention/boundary contract and actual runtime/neighbour/browser checks are still required. Root grid water outside the validated inset is untouched.')
 save(out/'summary.json',result);refs.extend([out/'lineage.json.gz',out/'seams.json',HERE/'rectangular_native_fragments_v1_20261101.py',HERE/'coordinated_native_boundary_v1_20261023.py']);assert digest(manifest.read_bytes())==msha;module('one_peking_private_fragment_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-exact-rectangular-native-fragment-set-and-finite-seam-diagnostics',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()

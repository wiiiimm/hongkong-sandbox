"""Distinguish exact strict roof-interior witnesses from surface boundary contact."""
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_component_contacts_20261009 import exact_component_contacts
from exact_original_shell_intersections_20261009 import rational_face,sub,dot,cross
B=ROOT/'docs/astra-city/government-import';OLD=B/'government-xl-villa-private-canopy-collision-v1-20261015';DOC=B/'government-xl-villa-private-canopy-volume-witness-v1-20261015'
def bary(p,t):
 u=sub(t[1],t[0]);v=sub(t[2],t[0]);w=sub(p,t[0]);assert dot(cross(u,v),w)==0
 aa=dot(u,u);bb=dot(u,v);cc=dot(v,v);dd=dot(w,u);ee=dot(w,v);den=aa*cc-bb*bb;assert den>0
 s=(cc*dd-bb*ee)/den;t=(aa*ee-bb*dd)/den;return [1-s-t,s,t]
def main():
 assert not DOC.exists();rp=OLD/'rendered.json';pins={r['path']:r['sha256'] for r in read(OLD/'result.json')['evidenceRefs']};assert digest(rp.read_bytes())==pins[str(rp.relative_to(ROOT))];rendered=read(rp)
 for p,h in rendered['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 selection=B/'government-xl-villa-five-original-coupled-physical-v3-20261010/selection.json.gz';row=next(r for r in read(selection)['rows'] if r['uid']=='landsd/89917:0');asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];tri=decode_original_world_triangles(asset.read_bytes());results=[]
 for r in rendered['rows']:
  mesh=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];normal=np.cross(mesh[:,1]-mesh[:,0],mesh[:,2]-mesh[:,0]);high=mesh[:,:,1].max();roof=next(p for p in r['description']['parts'] if p['kind']=='roof');low=float(np.float32(roof['bottom']));assert low<high
  ids=np.flatnonzero((mesh[:,:,1]==high).all(1)&(normal[:,1]>0));sections=mesh[ids].copy();sections[:,:,1]=(low+high)/2
  if not len(ids):results.append({'mode':r['mode'],'part':r['part'],'roofTopFaces':0,'degenerateCandidate':True,'strictWitnesses':[]});continue
  contacts=exact_component_contacts(tri,list(range(len(tri))),sections,list(range(len(sections))));witnesses=[]
  for c in contacts['contacts']:
   if c['dimension']!=1:continue
   pts=[[F(v) for v in p] for p in c['exactPoints']];q=tuple(sum((p[k] for p in pts),F(0))/len(pts) for k in range(3));a=bary(q,rational_face(tri[c['sourceFaceA']]));b=bary(q,rational_face(sections[c['sourceFaceB']]))
   if min(a)>0 and min(b)>0:witnesses.append({'sourceFace':c['sourceFaceA'],'renderedRoofFace':int(ids[c['sourceFaceB']]),'point':[str(v) for v in q],'sourceBarycentric':[str(v) for v in a],'roofBarycentric':[str(v) for v in b]})
  results.append({'mode':r['mode'],'part':r['part'],'roofTopFaces':len(ids),'roofBottom':low,'roofTop':float(high),'strictWitnesses':witnesses,'allSectionContacts':contacts,'degenerateFaces':int((np.linalg.norm(normal,axis=1)==0).sum())})
 DOC.mkdir();save(DOC/'witnesses.json.gz',{'rows':results,'qualification':'Positive strict interior witnesses prove remaining roof-volume conflict. Absence does not prove full collision clearance or arbitrary source/Float32 equivalence.'});summary={'uids':[row['uid'],'landsd/325786:0'],'rows':[{'mode':r['mode'],'part':r['part'],'roofTopFaces':r['roofTopFaces'],'strictWitnesses':len(r['strictWitnesses']),'degenerateFaces':r.get('degenerateFaces'),'degenerateCandidate':r.get('degenerateCandidate',False)} for r in results],'fullAcceptance':False,'sourceBuildingGeometryChanged':False,'liveGeometryChanged':False}
 save(DOC/'summary.json',summary);paths=[Path(__file__),OLD/'result.json',rp,selection,asset,HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_shell_intersections_20261009.py']+[ROOT/p for p in rendered['inputHashes']]
 module('villa_private_witness_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(DOC.name,'private-canopy-exact-mid-roof-positive-volume-witness-v1',paths,{**summary,'nextStep':'If witnesses remain, resolve exact source-bound Float32 clipping before any acceptance; retain all pieces/actors and every original facet.'});print(summary,flush=True)
if __name__=='__main__':main()

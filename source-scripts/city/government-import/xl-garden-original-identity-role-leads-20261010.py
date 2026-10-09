"""Inspect complete unchanged source roles for two distinct Garden identity holds."""
from pathlib import Path
import json,numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_component_contacts_20261009 import exact_component_contacts
from source_closed_components import components
DOC=ROOT/'docs/astra-city/government-import/government-xl-garden-original-identity-role-leads-20261010'
INPUT=DOC.parent/'xl-terrain-recovery-20261010-garden-two-foreign-current-inputs-v1'
FOREIGN=DOC.parent/'government-xl-source-neighbour-recovery-leads-20261010/selection.json.gz'
def poly(rings):
 p=shapely.Polygon()
 for ring in rings:p=p.symmetric_difference(shapely.Polygon(ring))
 assert p.is_valid and p.area>0
 return p
def main():
 assert not DOC.exists();selection=read(INPUT/'check-selection.json.gz');foreign=next(r for r in read(FOREIGN)['rows'] if r['uid']=='landsd/213929:0');fpath=ROOT/foreign['candidate']['path'];fraw=fpath.read_bytes();assert digest(fraw)==foreign['sourceSHA256'];f=decode_original_world_triangles(fraw);fq=poly(foreign['source']['building']['rings']);rows=[];inputs=[Path(__file__),INPUT/'check-selection.json.gz',FOREIGN,fpath,HERE/'source_closed_components.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_packed_world_geometry_20261009.py']
 for row in selection['rows']:
  path=ROOT/row['candidate']['path'];raw=path.read_bytes();assert digest(raw)==row['sourceSHA256'];a=decode_original_world_triangles(raw);top=components(a);q=poly(row['source']['building']['rings']);projection=shapely.union_all(shapely.polygons(a[:,:,[0,2]]));distance=shapely.distance(shapely.points(a[:,:,[0,2]].reshape(-1,2)),q).reshape(len(a),3);far=np.flatnonzero(distance.max(1)>10).tolist();overlap=projection.difference(q).intersection(fq);overids=[i for i,t in enumerate(a) if shapely.Polygon(t[:,[0,2]]).intersection(overlap).area>0];wanted=sorted({ci for ci,c in enumerate(top['components']) if set(c['faceIndices'])&set(far+overids)});parts=[]
  for ci in wanted:
   c=top['components'][ci];ids=c['faceIndices'];body=a[ids];other=[i for i in range(len(a)) if i not in set(ids)];contacts=exact_component_contacts(a,ids,a,other,maximum_pairs=1000000);foreigncontacts=exact_component_contacts(a,ids,f,range(len(f)),maximum_pairs=1000000)
   parts.append({'componentId':ci,'completeOriginalFaceIds':ids,'completeOriginalTriangles':body.tolist(),'completeComponent':c,'farFaceIds':sorted(set(ids)&set(far)),'foreignExcessFaceIds':sorted(set(ids)&set(overids)),'completeComponentBounds':[body.min(axis=(0,1)).tolist(),body.max(axis=(0,1)).tolist()],'completeComponentToWholeOwnRemainderContacts':contacts,'completeComponentToWholeForeignOriginalContacts':foreigncontacts,'wholeForeignOriginalBounds':[f.min(axis=(0,1)).tolist(),f.max(axis=(0,1)).tolist()],'completeComponentEntirelyAboveActualForeign':bool(body[:,:,1].min()>f[:,:,1].max()),'wholeCurrentForeignTop':foreign['source']['building'].get('topHeightHKPD'),'physicalAccepted':False})
  rows.append({'uid':row['uid'],'completeCurrentForm':row['source']['building'],'sourceSHA256':row['sourceSHA256'],'completeWorldSHA256':digest(a.astype('<f8').tobytes()),'completeOriginalFaces':len(a),'completeOriginalParts':len(top['components']),'allFarOriginalFaceIds':far,'allFarOriginalTriangles':a[far].tolist(),'rawMaximumSourceExtentM':float(distance.max()),'foreignUid':foreign['uid'],'rawForeignExcessM2':float(overlap.area),'allForeignExcessFaceIds':overids,'roleComponents':parts,'identityAccepted':False,'physicalAccepted':False,'qualification':'Complete component geometry/contact/height roles only. No legal ownership, common permit, support, collision or terrain exemptions.'});inputs.append(path)
 save(DOC/'diagnostic.json.gz',{'rows':rows,'foreignOriginalSourceSHA256':foreign['sourceSHA256'],'foreignCompleteWorldSHA256':digest(f.astype('<f8').tobytes()),'foreignCompleteFaces':len(f),'inputHashes':{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in inputs},'sourceGeometryChanges':0,'identityAccepted':False,'physicalAccepted':False})
 print(json.dumps([{'uid':r['uid'],'farFaces':len(r['allFarOriginalFaceIds']),'foreignExcessFaces':r['allForeignExcessFaceIds'],'parts':[{'id':p['componentId'],'faces':len(p['completeOriginalFaceIds']),'aboveActualForeign':p['completeComponentEntirelyAboveActualForeign'],'ownPositiveContacts':sum(c['dimension']>0 for c in p['completeComponentToWholeOwnRemainderContacts']['contacts']),'foreignPositiveContacts':sum(c['dimension']>0 for c in p['completeComponentToWholeForeignOriginalContacts']['contacts'])} for p in r['roleComponents']]} for r in rows]),flush=True)
if __name__=='__main__':main()

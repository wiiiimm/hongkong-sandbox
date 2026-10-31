"""Complete original component-to-component contacts and roof role inputs.

No filled-volume claim for an open source shell; exact contacts, complete planar
coverage and original support samples remain independent diagnostics.
"""
import importlib.util, json, uuid,sys
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,reservations
from exact_original_component_contacts_20261009 import exact_component_contacts
from source_closed_components import components as edge_components
BATCH='government-xl-miami-original-roof-attachment-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
BASE=DOC.parent/'government-xl-miami-elevated-original-contact-graph-20261009'
INPUT=DOC.parent/'government-xl-miami-nine-original-contact-20261009/all-original-source-contact-inputs.json.gz'

def compact_inputs():
 originals=read(INPUT)['rows'];rows=[];sources=[]
 for p in sorted(DOC.glob('*-complete-original-roof-roles.json.gz')):
  record=read(p);s=next(r for r in originals if r['uid']==record['uid']);t=np.asarray(s['position']).reshape(-1,3,3);assert digest(t.astype('<f8').tobytes())==record['sourceWorldTriangleSHA256'];sources.append(s)
  for c in record['components']:
   ids=c['originalFaceIds'];rows.append({'uid':s['uid'],'component':c['component'],'sourceSHA256':s['sourceSHA256'],'sourceWorldTriangleSHA256':s['worldTriangleSHA256'],'originalFaceIds':ids,'bottomHKPD':float(t[ids,:,1].min())})
 assert len(sources)==4;save(DOC/'complete-original-component-support-inputs.json.gz',{'rows':rows,'sources':sources,'sourceInputSHA256':digest(INPUT.read_bytes()),'sourceGeometryChanges':0,'physicalAccepted':False,'qualification':'Compact complete source arrays with explicit original component IDs; every support array is exactly the original complement, never a hull or generated primitive.'})

def main():
 assert not (DOC/'result.json').exists(),'Frozen stage immutable'
 originals=read(INPUT)['rows'];graphs=sorted(BASE.glob('*-whole-component-contact-graph.json.gz'))
 claim=reservations.claim('miami-roof-role-'+str(uuid.uuid4()),['building:'+read(p)['uid'] for p in graphs],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];records=[]
 try:
  for path in graphs:
   g=read(path);source=next(r for r in originals if r['uid']==g['uid']);t=np.asarray(source['position'],float).reshape(-1,3,3);assert digest(t.astype('<f8').tobytes())==g['worldTriangleSHA256'];groups=g['components'];allids=[i for p in groups for i in p['originalFaceIds']];assert sorted(allids)==list(range(len(t))) and len(set(allids))==len(t)
   top=edge_components(t[np.asarray(groups[0]['originalFaceIds'])]);main_face_ids=groups[0]['originalFaceIds'];main_topology=[{**r,'originalFaceIds':[main_face_ids[i] for i in r['faceIndices']]} for r in top['components']]
   missing={p['component'] for p in g['remainingComponentsToMainBody'] if not p['mainBodyContact']['contacts']};out=[]
   for p in groups[1:]:
    ids=np.asarray(p['originalFaceIds']);part=t[ids];other_ids=np.setdiff1d(np.arange(len(t)),ids);other=t[other_ids];contact=[]
    if p['component'] in missing:
     lo,hi=part.min(axis=(0,1)),part.max(axis=(0,1))
     for q in groups[1:]:
      if q['component']==p['component']:continue
      qlo,qhi=np.asarray(q['worldBounds']);
      if np.any(qhi<lo) or np.any(qlo>hi):continue
      proof=exact_component_contacts(t,ids,t,q['originalFaceIds'],first_only=True)
      if proof['contacts']:contact.append({'component':q['component'],'originalFaceIds':q['originalFaceIds'],'contact':proof})
    foot=shapely.union_all(shapely.polygons(part[:,:,[0,2]]));below=other[other[:,:,1].max(axis=1)<=part[:,:,1].min()];shadow=shapely.union_all(shapely.polygons(below[:,:,[0,2]]));covered=foot.intersection(shadow).area
    row={**p,'originalMainBodyContact':next(x['mainBodyContact'] for x in g['remainingComponentsToMainBody'] if x['component']==p['component']),'exactOtherComponentContacts':contact,'completeComponentProjectionM2':foot.area,'projectionCoveredByWholeOriginalFacesEntirelyBelowBottomM2':covered,'projectionMissingOriginalBelowM2':foot.difference(shadow).area,'physicalRoleAccepted':False,'qualification':'Original component contact and below-height projected coverage only. No solid-shell claim, source ornament role, body anchoring or structural approval follows from projection.'};out.append(row)
    if len(out)%20==0:assert reservations.heartbeat(lease)['ok']
   record={'uid':g['uid'],'sourceSHA256':g['sourceSHA256'],'sourceWorldTriangleSHA256':g['worldTriangleSHA256'],'wholeOriginalFaces':len(t),'exactMainBodyEdgeTopology':main_topology,'mainBodyFilledVolumeCertified':False,'components':out,'allOriginalFacesAccountedExactlyOnce':True,'modelGeometryChanges':0,'physicalAccepted':False};save(DOC/(g['uid'].split('/')[1].replace(':','-')+'-complete-original-roof-roles.json.gz'),record);records.append({'uid':g['uid'],'componentsWithoutMainContact':len(missing),'withExactOtherContact':sum(bool(r['exactOtherComponentContacts']) for r in out if r['component'] in missing),'withCompleteBelowProjection':sum(r['projectionMissingOriginalBelowM2']<1e-9 and r['completeComponentProjectionM2']>0 for r in out if r['component'] in missing),'originalFaces':len(t)});print(json.dumps(records[-1]),flush=True)
  compact_inputs();save(DOC/'summary.json',{'rows':records,'sourceGeometryChanges':0,'physicalAccepted':False,'nextStep':'Replay every component against the full original remaining source; identify exact roof contact roles with independently accepted original body anchor.'})
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':
 if '--compact' in sys.argv:compact_inputs()
 else:main()

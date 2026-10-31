"""Bind all secondary original components to exact main-body contact diagnostics."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from source_closed_components import components
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts

def main():
 base=ROOT/'docs/astra-city/government-import'
 batch='government-xl-fu-tor-loy-secondary-original-contacts-v1-20261023'
 out=base/batch;assert not out.exists()
 capture='government-xl-fu-tor-loy-five-originals-current-v1-20261023-runtime'
 _,pins=authenticate(base/capture)
 path=base/capture/'selection.json.gz';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
 refs=[Path(__file__),path,base/capture/'result.json'];rows=[]
 for r in read(path)['rows']:
  if r['uid']=='landsd/228219:0':continue
  asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];refs.append(asset)
  t=decode_original_world_triangles(asset.read_bytes());topology=components(t)
  groups=sorted(topology['components'],key=lambda c:-c['triangles']);parts=[]
  for part in groups[1:]:
   proof=exact_finite_contacts(t,part['faceIndices'],t,groups[0]['faceIndices'])
   positive=[c for c in proof['contacts']if c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2 and c['dimension']>0]
   parts.append(dict(component=part,contacts=proof,positiveSurfaceContacts=len(positive)))
  row=dict(uid=r['uid'],sourceSHA256=r['sourceSHA256'],topology=topology,secondaryComponents=parts)
  save(out/(r['uid'].split('/')[1]+'.json.gz'),row)
  summary=dict(uid=r['uid'],faces=len(t),secondary=[dict(faces=p['component']['triangles'],degenerateFaces=p['component']['degenerateTriangles'],positiveContacts=p['positiveSurfaceContacts'])for p in parts])
  rows.append(summary);print(summary,flush=True)
 result=dict(uids=[r['uid']for r in rows],rows=rows,sourceGeometryChanges=0,installationApproved=False,qualification='Original exact contacts only; zero-dimensional/degenerate contacts never grant support. Component contacts do not certify engineering role or installation.')
 save(out/'summary.json',result)
 refs += [HERE/n for n in ['exact_packed_world_geometry_20261009.py','source_closed_components.py','exact_original_finite_triangle_contacts_20261010.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py']]
 module('secondary_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'complete-secondary-original-component-contacts',refs,result)
if __name__=='__main__':main()

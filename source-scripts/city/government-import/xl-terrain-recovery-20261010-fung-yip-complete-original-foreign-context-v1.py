"""All authenticated foreign original faces vs whole Fung originals; diagnostic."""
from pathlib import Path
import importlib.util,json,numpy as np
from shapely.geometry import Polygon,LineString
from shapely.ops import unary_union
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_component_contacts_20261009 import exact_component_contacts
from xl_source_stream_binding_20261009 import source_stream_binding
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261010-fung-yip-complete-original-foreign-context-v1';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
INPUTS=[BASE/'government-xl-terrain-recovery-fung-yip-original-pair-current-recovery-v2-20261010/selection.json.gz',BASE/'government-xl-terrain-recovery-fung-yip-foreign-original-recovery-v1-20261010/selection.json.gz']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();LOCAL.mkdir(parents=True,exist_ok=True);rows={r['uid']:r for p in INPUTS for r in read(p)['rows']};assert set(rows)=={'landsd/254815:0','landsd/79883:0','landsd/12728:0','landsd/79882:0'};t={};polys={};individual={};assets=[]
 for u,r in rows.items():
  p=ROOT/r['candidate']['path'];raw=p.read_bytes();assert digest(raw)==r['sourceSHA256'];assets.append(p);t[u]=decode_original_world_triangles(raw);assert len(t[u])==r['native']['model']['triangles'];pieces=[]
  for f in t[u]:
   q=Polygon(f[:,[0,2]]);pieces.append(q if q.area else LineString(f[:,[0,2]]))
  individual[u]=pieces;polys[u]=unary_union(pieces);assert polys[u].is_valid
 pairs=[]
 for a in ['landsd/254815:0','landsd/79883:0']:
  for b in ['landsd/12728:0','landsd/79882:0']:
   overlap=polys[a].intersection(polys[b]);contacts=exact_component_contacts(t[a],range(len(t[a])),t[b],range(len(t[b])));assert contacts['allPairsExamined'];affected=[]
   for i,p in enumerate(individual[a]):
    x=p.intersection(polys[b])
    if not x.is_empty:
     f=t[a][i];affected.append(dict(sourceFace=i,intersectionAreaM2=x.area,intersectionLengthM=x.length,closedProjectionGeometry=x.__geo_interface__,sourceBounds=[f.min(axis=0).tolist(),f.max(axis=0).tolist()],sourceNormal=np.cross(f[1]-f[0],f[2]-f[0]).tolist()))
   r=dict(sourceUID=a,foreignUID=b,sourceSHA256=rows[a]['sourceSHA256'],foreignSourceSHA256=rows[b]['sourceSHA256'],completeOwnOriginalFaces=len(t[a]),completeForeignOriginalFaces=len(t[b]),ownWorldSHA256=digest(t[a].tobytes()),foreignWorldSHA256=digest(t[b].tobytes()),wholeOriginalClosedProjectionIntersection=overlap.__geo_interface__,wholeOriginalProjectionOverlapAreaM2=overlap.area,wholeOriginalProjectionDistanceM=polys[a].distance(polys[b]),allOwnOriginalProjectionIntersectingFaces=affected,completeActualOriginalSurfaceIntersections=contacts,identityAccepted=False,physicalAccepted=False,sourceGeometryChanges=0)
   pairs.append(r);save(LOCAL/'progress.json.gz',dict(rows=pairs));print(json.dumps(dict(source=a,foreign=b,area=overlap.area,sourceAffected=len(affected),exactContacts=len(contacts['contacts']),positiveContacts=sum(c['dimension']>0 for c in contacts['contacts']))),flush=True)
 out=dict(uids=sorted(rows),manifestSHA256=read(INPUTS[0])['manifestSHA256'],sourceSHA256s={u:r['sourceSHA256']for u,r in rows.items()},completeProviderRootsAndStreams={u:source_stream_binding((ROOT/r['candidate']['path']).read_bytes())for u,r in rows.items()},rows=pairs,allOriginalVerticalCollapsedProjectionsRetained=True,sourceGeometryChanges=0,visualRoleAccepted=False,identityAccepted=False,structuralSupportAccepted=False,installationApproved=False,qualification='Complete true original foreign geometry diagnosis only. Raw form overlaps/ordinary1m² threshold remain unchanged; original projection overlap also remains measured. Exact surface contact is not common ownership, support, identity or intersection acceptance. All current physical/foreign/terrain/runtime checks remain mandatory.',evidenceRefs=[ref(p)for p in [Path(__file__),*INPUTS,*assets,HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'xl_source_stream_binding_20261009.py']]);out=json.loads(json.dumps(out,allow_nan=False));save(DOC/'diagnostic.json.gz',out);s=importlib.util.spec_from_file_location('fung_foreign_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'fung-yip-whole-original-foreign-context-v1',[ROOT/r['path']for r in out['evidenceRefs']],out)
if __name__=='__main__':main()

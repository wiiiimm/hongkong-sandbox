"""Diagnostic complete OP-owned paired original sources; no composite asset created."""
import sys,shutil,json,uuid
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,reservations
import importlib.util
from original_source_ownership import graph_reasons,document
from government_georef_cell_identity import geographic_cell
DOC=ROOT/'docs/astra-city/government-import/government-xl-identity-search-op-structures-20261009';LOCAL=HERE/'local/government-xl-identity-search-op-structures-20261009-pairs'
def mod(n,f):
 s=importlib.util.spec_from_file_location(n,HERE/f);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 source=read(HERE/'local/government-xl-identity-search-op-structures-20261009/paired-physical-source-candidates.json.gz')['rows'];claim=reservations.claim('xl-op-paired-mesh-'+str(uuid.uuid4()),['native-model:'+r['sourceKey'] for r in source],batch='government-xl-identity-search-op-structures-20261009',ttl=1800);assert claim['ok'],claim;lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
 try:
  cache={p.name[:-7]:p for p in (HERE/'local').rglob('*.glb.gz')};decode=mod('paired_op_originals','xl-second-pass.py');decode.LOCAL=LOCAL;final=mod('paired_op_forms','xl-final-script-pass.py');rel=read(DOC/'official-op-relationship-research.json.gz')['rows'];out=[]
  for uid in ['landsd/147996:0','landsd/118003:0']:
   group=next(r for r in rel if r['uid']==uid);forms=group['currentGroupForms'];cs={b['buildingCSUID'] for b in forms};members=[r for r in source if any(m['buildingCSUID'] in cs for m in r['model']['matching']['viewerMatches'])];assert len(members)==2;triangles=[];reasons=[];sourceproof=[]
   for r in members:
    m=r['model'];sha=m['asset']['sha256'];p=cache.get(sha)
    if p is None:reasons.append('original-exact-member-cache-missing:'+m['modelId']);continue
    raw=p.read_bytes();assert digest(raw)==sha;asset=LOCAL/'assets'/(sha+'.glb.gz');asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,asset);tri=decode.glb_triangles({'sourceSHA256':sha,'modelId':m['modelId'],'triangles':m['triangles'],'native':{'model':m}});triangles.append(tri);reasons+=graph_reasons(document(raw),m['modelId'],m['triangles']);b=next(b for b in forms if b['buildingCSUID'][:10]==m['modelId'][1:11]);cell=geographic_cell(m['modelId'],b['buildingCSUID'],b['structureType']);projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]))
    if not Polygon(b['rings'][0],b['rings'][1:]).covers(cell):reasons.append('target-whole-cell:'+b['uid'])
    if not projection.covers(cell):reasons.append('source-whole-cell:'+b['uid'])
    sourceproof.append({'sourceKey':r['sourceKey'],'sourceSHA256':sha,'modelId':m['modelId'],'originalPath':str(p.relative_to(ROOT)),'worldTrianglesSHA256':digest(tri.astype('<f8').tobytes())})
   measures=None
   if len(triangles)==2:
    tri=np.concatenate(triangles);lo=tri.min(axis=(0,1));hi=tri.max(axis=(0,1));context=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);guids={b['uid'] for b in forms};shape=shapely.union_all([Polygon(b['rings'][0],b['rings'][1:]) for b in forms]);others=shapely.union_all([p for b,p,_ in context if b['uid'] not in guids]);projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));measures={'targetCoverage':float(shape.intersection(projection).area/shape.area),'maximumExtentM':float(shapely.distance(shapely.points(tri[:,:,[0,2]].reshape(-1,2)),shape).max()),'unrelatedExcessOverlapM2':float(projection.difference(shape).intersection(others).area)}
    if measures['targetCoverage']<.95:reasons.append('complete-assembly-coverage-below-0.95')
    if measures['maximumExtentM']>10:reasons.append('complete-assembly-extent-over-10m')
    if measures['unrelatedExcessOverlapM2']>1:reasons.append('complete-assembly-unrelated-overlap-over-1m2')
   item={'uid':uid,'structureIds':group['structureIds'],'groupForms':forms,'sourceProofs':sourceproof,'measures':measures,'reasons':sorted(set(reasons)),'diagnosticCandidate':not reasons,'identityAccepted':False,'installationApproved':False,'modelGeometryChanges':0,'qualification':'Complete two-source original collection measured without creating/editing/composing any mesh. Both exact source roots and source cells retain separate ownership; explicit provider occupation-structure relation is supporting context. Physical/neighbour/runtime/browser and dedicated official multi-part policy remain.'};out.append(item);print(json.dumps({'uid':uid,'candidate':not reasons,'measures':measures,'reasons':reasons}),flush=True)
  save(DOC/'paired-original-op-group-measures.json.gz',{'rows':out})
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()

"""Replay all448 finite support paths and bind identical-world continuous context; no approval."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from finite_embedded_basic_support_contract_v2_20261025 import verify_mode
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-beverly-fe-after-k-finite-evidence-v1-20261025'

def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__),HERE/'finite_embedded_basic_support_contract_v2_20261025.py',HERE/'test_finite_embedded_basic_support_contract_v2_20261025.py'];pins={}
 def take(batch,name,local=False):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  p=(HERE/'local'if local else BASE)/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 runtime='government-xl-beverly-fe-after-k-runtime-v1-20261025';source=take(runtime,'selection.json.gz');by={r['uid']:r for r in source['rows']};geometry={r['uid']:r for r in take(runtime,'runtime-geometry.json.gz',local=True)['rows']}
 modesbatch='government-xl-beverly-fe-after-k-four-world-basic-v1-20261025';payload=take(modesbatch,'mode-inputs.json.gz')['rows'];raw=take(modesbatch,'mode-checks.json.gz')['rows'];coarse=take(modesbatch,'finite-clearance.json');rows=[];continuous=[]
 for item in payload:
  uid=item['uid'];assert item['sourceSHA256']==by[uid]['sourceSHA256']==geometry[uid]['sourceSHA256'];g=item['supportGeometry'];p=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];world_hashes=[]
  captured=geometry[uid];actual=np.asarray(captured['position']).reshape(-1,3)[np.asarray(captured['index']).reshape(-1,3)];actual_sha=digest(actual.astype('<f8').tobytes())
  for mode in item['modes']:
   name=mode['mode'];x=mode['geometry'];tri=np.asarray(x['position']).reshape(-1,3)[np.asarray(x['index']).reshape(-1,3)]
   paths='government-xl-beverly-'+uid.split('/')[1].split(':')[0]+'-after-k-basic-roof-paths-v1-20261025';detail=take(paths,name+'.json.gz');canonical=next(c['proof']for c in raw if c['uid']==uid and c['mode']==name)
   proof=verify_mode(tri,p,canonical,detail);rows.append(dict(uid=uid,mode=name,sourceSHA256=item['sourceSHA256'],**proof));world_hashes.append(detail['sourceWorldSHA256'])
  assert len(world_hashes)==4 and set(world_hashes)=={actual_sha}
  context=take('government-xl-beverly-fe-after-k-continuous-v1-20261025',uid.split('/')[1]+'.json.gz');assert context['sourceSHA256']==item['sourceSHA256']and context['wholeSourceFaces']==len(actual)==len(context['faces'])and context['wholeSourceUncoveredFaces']==0 and not context['continuousAffectedFaces']
  ground=np.asarray(captured['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
  continuous.append(dict(uid=uid,sourceSHA256=item['sourceSHA256'],sourceFaces=len(actual),allFourWorldIndexedTrianglesExactlyEqual=True,worldTrianglesSHA256=actual_sha,drawnGroundSHA256=digest(ground.tobytes()),completeContinuousContextReusedForIdenticalTriangles=True,upwardContinuousMinimumGapM=context['upwardContinuousMinimumGapM'],wholeSourceUncoveredFaces=0,rawGlobalHeightBoundPassed=all(r['ordinaryClearanceBoundProved']for r in coarse if r['uid']==uid)))
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==source['manifestSHA256'];refs.append(manifest)
 assert len(rows)==8 and sum(r['verifiedPaths']for r in rows)==448
 result=dict(uids=sorted(by),rows=rows,identicalWorldContinuousContext=continuous,verifiedFinitePaths=448,strictCanonicalSupportPassed=False,diagnosticOnly=True,physicalAcceptance=False,installationApproved=False,publication=False,sourceGeometryChanges=0,qualification='Separate replayed finite source-facet paths preserve all raw no-vertical-support and support-above-rim failures. All448 witnesses reach an actual exposed vertical source-wall/currentBASICroof intersection within unchanged.5m embedding/1mm path limits. Complete indexed original/literal/twoFloat32 source triangles are byte-identical to actual runtime geometry for each source; the authenticated complete continuous terrain context therefore applies identically acrossall4representations. Coarse global source-min-minus-all-ground-max failures remain raw, not renamed passes. This evidence does not resolve original F/E contact roles (including15transverse contacts), current noncandidate neighbour checks, source-specific acceptance, private/live images or publication.')
 save(out/'summary.json',result);module('beverly_adf_finite_evidence_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'paired-original-finite-support-path-and-identical-world-continuous-context-diagnostics',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()

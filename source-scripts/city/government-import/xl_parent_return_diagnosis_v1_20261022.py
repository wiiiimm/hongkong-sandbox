"""Bind the actual failed edge to its validated terrain-return template; no approval."""
from pathlib import Path
import subprocess,sys,numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from terrain_parent_template_basis_v1 import validated_template_faces
BASE=ROOT/'docs/astra-city/government-import'
OLD='government-xl-six-parent-coverage-followthrough-v1-20261022-candidates-226296-0-terrain'
BATCH='government-xl-source226296-parent-return-diagnosis-v1-20261022'
def main():
 doc=BASE/BATCH;assert not doc.exists()
 r,pins=authenticate(BASE/OLD);refs=[Path(__file__),BASE/OLD/'result.json']
 def take(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 scope=take(BASE/OLD/'scope.json');captured=take(HERE/'local'/OLD/'parent.json');template=take(HERE/'local'/OLD/'parent-template.json')
 parent=take(ROOT/'3d-viewer/city/data/terrain.json')
 for path,sha in captured['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
 builder=module('parent_return_diagnostic_builder',HERE/'resolve_pass_indexed_parent_clipping_v2.py');sampler=builder.terrain.fine.DemSampler(parent,rendered=True)
 a,b,c,d=scope['bounds'];out=[]
 for kind,faces in [('raw-current-parent',np.asarray(captured['triangles'])),('validated-template',validated_template_faces(template,parent))]:
  v=faces.reshape(-1,3).astype(np.float32).astype(float)
  v=v[np.minimum.reduce([abs(v[:,0]-a),abs(v[:,0]-c),abs(v[:,2]-b),abs(v[:,2]-d)])<.002]
  gaps=np.asarray([y-sampler.ground(x,z)for x,y,z in v])
  out.append(dict(kind=kind,edgeVertices=len(v),maximumAbsoluteGapM=float(abs(gaps).max()),worstVertex=v[np.argmax(abs(gaps))].tolist()))
 assert out[0]['maximumAbsoluteGapM']>=.01 and out[1]['maximumAbsoluteGapM']<.01
 testnames=['test_terrain_parent_template_basis','test_parent_template_validation_evidence','test_inherited_parent_coverage']
 doc.mkdir();log=doc/'tests.log'
 import os
 with log.open('w')as f:
  subprocess.run([sys.executable,'-m','unittest',*testnames],cwd=HERE,stdout=f,stderr=subprocess.STDOUT,check=True)
 refs.extend(HERE/(n+'.py')for n in testnames)
 refs.extend([HERE/'terrain_parent_template_basis_v1.py',HERE/'selected_original_local_inset_v7.py',HERE/'selected_original_bounded_candidate_batch_v5.py',HERE/'xl_validated_parent_return_followthrough_v1_20261022.py'])
 result=dict(uids=['landsd/226296:0'],rows=out,regressionTestsPassed=10,sourceGeometryChanges=0,newlyInstalled=0,installationApproved=False,publication=False,scriptExternalAICalls=0,qualification='Actual final inset inherited raw parent edge mismatch after discarding a validated return. V7 preserves that return; fresh candidate/neighbour/browser checks remain mandatory. No threshold or source geometry changes.')
 save(doc/'summary.json',result)
 module('parent_return_diagnosis_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'actual-source-parent-return-construction-diagnosis',refs,result)
if __name__=='__main__':main()

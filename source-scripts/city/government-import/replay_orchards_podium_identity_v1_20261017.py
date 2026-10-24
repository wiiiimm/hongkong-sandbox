from pathlib import Path
from copy import deepcopy
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from orchards_podium_component_identity_v1_20261017 import interpret,P,C
BATCH='government-xl-orchards-podium-component-identity-v1-20261017';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH
def main():
 assert not DOC.exists();scope=BASE/'government-xl-orchards-community-primary-scope-v1-20261017';receipt=read(scope/'result.json');refs=[Path(__file__),HERE/'orchards_podium_component_identity_v1_20261017.py',scope/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for e in receipt['evidenceRefs']:assert digest((ROOT/e['path']).read_bytes())==e['sha256'];refs.append(ROOT/e['path'])
 rows={};proofs={};meshes={};providers={}
 for n in ['podium','community']:
  d=BASE/('government-xl-orchards-'+n+'-current-checks-v1-20261017');row=read(d/'selection.json.gz')['rows'][0];uid=row['uid'];rows[uid]=row;proofs[uid]=read(d/'identity-proofs.json')['rows'][0];raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];meshes[uid]=decode_original_world_triangles(raw);providers[uid]=read(scope/(uid.split('/')[1]+'-provider.json'))
 final=module('orchards_identity_fresh_forms',HERE/'xl-final-script-pass.py');forms={b['uid']:b for b,_,_ in final.load_forms([5550,360,5660,520])}
 for _,_,tile in final.load_forms([5550,360,5660,520]):refs.append(ROOT/'3d-viewer'/tile)
 result=interpret(rows,proofs,meshes,forms,providers);tests=[]
 for name in ['source-hash','extra-failure','missing-community','changed-parent','changed-primary-id','changed-mesh']:
  rr,pp,mm,ff,aa=deepcopy((rows,proofs,meshes,forms,providers))
  if name=='source-hash':rr[P]['sourceSHA256']='0'*64
  elif name=='extra-failure':pp[P]['reasons'].append('source-pose-changed')
  elif name=='missing-community':del rr[C]
  elif name=='changed-parent':ff[C]['parent']='unrelated'
  elif name=='changed-primary-id':aa[C]['features'][0]['attributes']['BuildingID']=-1
  else:mm[P][0,0,0]+=.1
  try:interpret(rr,pp,mm,ff,aa)
  except(AssertionError,KeyError):tests.append(dict(case=name,rejected=True))
  else:raise AssertionError(name)
 save(DOC/'identity.json',result);save(DOC/'adversarial-tests.json',tests);refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl-final-script-pass.py']);out=module('orchards_podium_identity_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-podium-northern-community-component-identity-only-v1',list(set(refs)),dict(uids=[P,C],identityAccepted=True,requiredCompanionUid=C,fullAcceptance=False,tests=tests));print(dict(jobId=out['jobId'],measures=result['measures'],negativeTests=len(tests)),flush=True)
if __name__=='__main__':main()

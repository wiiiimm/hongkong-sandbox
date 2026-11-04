"""Exact THEi same-permit pair: reuse unchanged hard identity; prove independent ground contact.

The historical stacked-interface failure remains evidence. This contract is only
for these two immutable originals; neither is admitted as suspended on the other.
"""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-thei-grounded-pair-identity-v1-20261021';DOC=BASE/BATCH
EXPECTED={'landsd/259613:0':('43fa5a66feafacd1355cba1dc67eb7fd15f8bd6ba323816340c81ab323cb7537','4284714511T20180302',1810172239,'Tower'), 'landsd/259803:0':('0e2293e5c811b9d064b65aea4bf94614fb9d2874265294885dc02cf568fc3786','4284514558P20180302',1810172240,'Podium')}
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 def take(name,file):
  folder=BASE/name;_,ps=authenticate(folder);p=folder/file;k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ps[k];pins[k]=ps[k];refs.extend([folder/'result.json',p]);return read(p)
 selected=take('government-xl-thei-current-runtime-v1-20261021','selection.json.gz');rows=selected['rows'];assert {r['uid']for r in rows}==set(EXPECTED)
 old=take('government-xl-new-desh-assembly-identity-20261008','assembly-identity.json');assert old['reasons']==['exact-original-support-interface']
 oldcontexts=take('government-xl-three-untried-podium-original-closures-20261008','context.json.gz')['rows'];oldrows=take('government-xl-three-untried-podium-original-closures-20261008','support-inputs.json')['sources']
 primary=take('government-xl-thei-primary-pair-context-v1-20261021','context.json.gz')['rows']
 physical=take('government-xl-thei-four-mode-foundations-v1-20261021','summary.json')['rows'];assert len(physical)==8 and {(r['uid'],r['mode'])for r in physical}=={(u,m)for u in EXPECTED for m in ['original','literal','explicitLeftF32','explicitBalancedF32']}
 assert all(r['passed'] and r['buried']==0 and r['contact']['passed'] and not r['contact']['reasons']for r in physical)
 runtime=take('government-xl-thei-candidate-runtime-v3-20261021','metrics.json');assert {r['uid']for r in runtime['rows']}==set(EXPECTED)
 for r in runtime['rows']:assert r['sourceSHA256']==EXPECTED[r['uid']][0] and r['sourcePreserved'] and r['missingTerrain']==0 and r['minSurfaceGap']>=-.5 and r['minLowGap']<=.1 and r['maxLowGap']<=1 and r['maxSamplerDelta']<=.002
 forms=take('government-xl-thei-form-regression-v3-20261021','summary.json');assert forms['forms']==36 and not forms['flagged']
 final=module('thei_grounded_identity_context',HERE/'xl-final-script-pass.py');verified=[]
 for row in rows:
  uid=row['uid'];sha,csuid,bid,kind=EXPECTED[uid];assert row['sourceSHA256']==sha;asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==sha;refs.append(asset)
  prior=next(r for r in oldrows if r['uid']==uid);assert prior['source']['building']==row['source']['building'] and prior['sourceSHA256']==sha and prior['modelId']==row['modelId']
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s',(row['native']['cacheKey'],)).fetchone()==(row['native']['resultSha'],)
  tri=decode_original_world_triangles(asset.read_bytes());proof=old['rawIndividualIdentity'][uid];assert proof['sourceSHA256']==sha and digest(tri.astype('<f8').tobytes())==proof['worldTrianglesSHA256'];assert len(tri)==row['triangles']
  lo,hi=tri.min((0,1)),tri.max((0,1));near=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);tiles={tile:digest((ROOT/'3d-viewer'/tile).read_bytes())for _,_,tile in near};context=next(r for r in oldcontexts if r['uid']==uid)
  assert context['identity']==final.identity_context(row,tri,near) and context['neighbourTileHashes']==tiles
  refs.extend(ROOT/'3d-viewer'/t for t in tiles)
  p=next(r for r in primary if r['uid']==uid);assert p['sourceSHA256']==sha and len(p['provider']['features'])==1;a=p['provider']['features'][0]['attributes'];assert (a['BuildingCSUID'],a['BuildingID'],a['BuildingBlockType'],a['Status'])==(csuid,bid,kind,'Active')
  relations={f['attributes']['BuildingStructureID']for f in p['opRelations']['features']};structures=p['opStructures']['features'];assert relations and relations=={f['attributes']['BuildingStructureID']for f in structures};assert {f['attributes']['OPNo']for f in structures}=={'HK40/2017(OP)'};assert all(f['attributes']['OPBlockType']==kind for f in structures)
  verified.append(dict(uid=uid,sourceSHA256=sha,rawIndividualReasons=proof['reasons'],exactCurrentInputsUnchanged=True,independentGroundChecks=[r for r in physical if r['uid']==uid]))
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 result=dict(uids=sorted(EXPECTED),rows=verified,identityAccepted=True,passed=True,reasons=[],policy='exact-thei-same-permit-independently-grounded-original-pair-v1',rawHistoricalAssembly=old,wholeAssemblyMeasures=old['measures'],currentManifestSHA256=selected['manifestSHA256'],installationApproved=False,modelGeometryChanges=0,qualification='Only the two exact immutable THEi sources. All historical hard identity, world pose, one-metre GeoRef, same-parent and numeric compound bounds rebind to identical current inputs. Shared exact provider OP relation confirms this pair. Both complete originals independently pass current ground contact and whole-foundation checks in all four representations; no tower-on-podium support is asserted. Historical failed stacked-interface diagnostics remain unchanged. Neighbour/runtime/browser/publication obligations remain separate.')
 save(DOC/'identity.json',result);refs.extend([HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py'])
 module('thei_grounded_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-grounded-pair-identity-review',list(dict.fromkeys(refs)),result);print('THEi exact grounded-pair identity accepted',flush=True)
if __name__=='__main__':main()

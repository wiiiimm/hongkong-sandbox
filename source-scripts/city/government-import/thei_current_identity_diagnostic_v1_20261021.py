"""Fresh exact source identities and raw compound result; no acceptance override."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files
from original_source_assembly_diagnostic import evaluate
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-thei-current-identity-diagnostic-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
assert not DOC.exists();refs=[Path(__file__)];pins={}
def take(name,file):
 folder=BASE/name;_,ps=authenticate(folder);p=folder/file;k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ps[k];pins[k]=ps[k];refs.extend([folder/'result.json',p]);return read(p)
selection=take('government-xl-thei-current-runtime-v1-20261021','selection.json.gz');rows=selection['rows'];manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
old=take('government-xl-new-desh-assembly-identity-20261008','assembly-identity.json');primary=take('government-xl-thei-primary-pair-context-v1-20261021','context.json.gz');physical=take('government-xl-thei-four-mode-foundations-v1-20261021','summary.json');assert len(physical['rows'])==8 and all(r['passed']for r in physical['rows'])
final=module('thei_current_identity_forms',HERE/'xl-final-script-pass.py');individual={};world={};forms={}
for row in rows:
 uid=row['uid'];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s',(row['native']['cacheKey'],)).fetchone()==(row['native']['resultSha'],)
 tri=decode_original_world_triangles(asset.read_bytes());world[uid]=tri;lo,hi=tri.min((0,1)),tri.max((0,1));near=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);tiles={tile:digest((ROOT/'3d-viewer'/tile).read_bytes())for _,_,tile in near}
 for b,_,_ in near:forms[b['uid']]=b
 context=dict(sourceSHA256=row['sourceSHA256'],identity=final.identity_context(row,tri,near),neighbourTileHashes=tiles);save(DOC/(uid.split('/')[1]+'-context.json'),context);individual[uid]=verify_files(row,context,LOCAL/uid.split('/')[1]);save(DOC/(uid.split('/')[1]+'-identity.json'),individual[uid]);refs.extend(ROOT/'3d-viewer'/t for t in tiles)
compound=evaluate(rows,individual,world,old['strictOriginalInterface'],list(forms.values()),tower='landsd/259613:0',podium='landsd/259803:0');save(DOC/'raw-assembly-identity.json',compound)
provider=[]
for row in primary['rows']:
 a=row['provider']['features'][0]['attributes'];relations={f['attributes']['BuildingStructureID']for f in row['opRelations']['features']};structures={f['attributes']['BuildingStructureID']for f in row['opStructures']['features']};assert relations==structures
 provider.append(dict(uid=row['uid'],csuid=a['BuildingCSUID'],blockType=a['BuildingBlockType'],occupationPermits=sorted({f['attributes']['OPNo']for f in row['opStructures']['features']})))
summary=dict(uids=[r['uid']for r in rows],rawCompoundReasons=compound['reasons'],rawIndividualReasons={u:p['reasons']for u,p in individual.items()},measures=compound['measures'],primary=provider,independentFourModeGroundChecksPassed=True,identityAccepted=False,installationApproved=False,nextStep='Review exact same-permit original assembly with independently grounded source parts; preserve old failed stacked-interface result and all original hard identity checks.')
save(DOC/'summary.json',summary)
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.extend(p for p in LOCAL.rglob('*')if p.is_file());refs.extend([HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'original_source_assembly_diagnostic.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl-final-script-pass.py'])
module('thei_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'fresh-original-pair-identity-diagnostic',list(dict.fromkeys(refs)),summary);print(summary,flush=True)

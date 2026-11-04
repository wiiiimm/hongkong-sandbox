"""Recover the two exact approved Cullinan source assets from the pinned government sheet; never AI."""
import importlib.util,json,sys,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(HERE.parent/'citywide-native'));from download import acquire;from convert import _convert_one
sys.path.insert(0,str(HERE.parent/'enhancement-screening'));from shape_prepare import canonical_bytes,sha
BASE=HERE/'local/government-xxl-second-20260911/elements-supports/sheets/11-NW-24C';OUT=HERE/'local/government-xxl-second-20260911/elements-cullinan';DOC=ROOT/'docs/astra-city/government-import/government-xxl-20260911/second-pass/elements'
APPROVED={'B346021841701063C0':'d252584cef03a3e69033ed550452ccbc67062994f67c4d3c995f467897034143','B346291850501063C0':'94033956f886cccc7d494057e7c1eebdf95f81f68a8738986f1c70c9f0983232'}
d=json.load(open(BASE/'directory/result.json'));d['models']=[m for m in d['models'] if m['modelId'] in APPROVED];assert {m['modelId'] for m in d['models']}==set(APPROVED);result=acquire(d,BASE/'directory/zip-directory.bin',OUT/'original');(OUT/'packed').mkdir(parents=True,exist_ok=True);rows=[]
with zipfile.ZipFile(OUT/'original/11-NW-24C.zip') as z:
 for m in d['models']:
  entry=next(x['name'] for x in m['members'] if x['name'].endswith('.gltf'));packed=_convert_one(z,z.getinfo(entry),OUT/'decoded',OUT/'packed',{}, {'modelId':m['modelId']});p=OUT/'packed'/packed['asset']['asset'];expected=APPROVED[m['modelId']];raw=canonical_bytes(p.read_bytes(),expected);target=OUT/'packed/assets'/(expected+'.glb.gz');target.write_bytes(raw);assert sha(raw)==expected;rows.append({'modelId':m['modelId'],'sourceEntry':entry,'sourceSHA256':expected,'bytes':len(raw)})
proof={'sheet':d['sheet'],'revision':d['revision'],'sourceETag':d['etag'],'directorySHA256':d['directorySHA256'],'compactArchiveSHA256':result['sha256'],'sourceArchiveBytes':result['sourceArchiveBytes'],'receivedBytes':result['receivedBytes'],'rows':rows,'aiCalls':0,'geometryChanges':0,'publication':False};DOC.mkdir(parents=True,exist_ok=True);(DOC/'cullinan-recovery.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))

"""Resolve six exact captured routing references to complete embedded geometry.
No reference outside this immutable document/pointer list receives typed handling.
"""
import gzip,hashlib,json
from copy import deepcopy
CAPTURE_PATH='docs/astra-city/government-import/government-xl-lippo-exact-preapply-pending-attempt-context-v1-20261011/capture.json.gz'
CAPTURE_SHA='7e7a20f10290182433e7a89ce1ee9763ae4d07e2af800b380b819c2a74b04fbd'
TILE_PATH='3d-viewer/city/data/tiles/-9_1.json'
TILE_SHA='34096b6065f9e549e2ded9fc2afe745f88b35d76422e1548e5be3c83a9c62525'
HASH_KIND='canonical embedded modelGeometry JSON SHA256; not a gzip asset hash'
FIELDS=frozenset(['modelId','position','normal','zeroSourceNormalVertices','worldBounds','vertices','triangles','source','sourceHashes','sourceMaterials','sourceMaterialIndex','officialMatches','colour','colourItemSize','buildingCSUID','sourceTile','sourceTileRevision','sourceArchiveSha256'])
ACTORS={
 'landsd/197795:0':('1784414418T20050430','B178441441801063C0','c6e20cb0513fea0358b2a2251c48c5a83f157b234935021555a00e917418f949',339109),
 'landsd/201560:0':('1784214365T20050430','B178421436501063C0','0f607d94d3efa9807e528a06cc355ced108f5c8e4cf8c1731c073c1844d788a6',168506),
 'landsd/291920:0':('1827714041T20050430','B182771404101062G1','8ef546071b7c2ac009add7c4233ba83647b1f01787bb022cfa53fb2dedf0f23a',159755)}
POINTERS={
 '/fixtureFiles/previousInventory/parts/1530/sourceEvidence':'landsd/197795:0',
 '/fixtureFiles/pendingInventory/parts/1530/sourceEvidence':'landsd/197795:0',
 '/fixtureFiles/previousInventory/parts/1661/sourceEvidence':'landsd/201560:0',
 '/fixtureFiles/pendingInventory/parts/1661/sourceEvidence':'landsd/201560:0',
 '/fixtureFiles/previousInventory/parts/2905/sourceEvidence':'landsd/291920:0',
 '/fixtureFiles/pendingInventory/parts/2906/sourceEvidence':'landsd/291920:0'}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
def at(value,pointer):
 for part in pointer.split('/')[1:]:
  part=part.replace('~1','/').replace('~0','~');value=value[int(part)] if isinstance(value,list) else value[part]
 return value

def verify_record(pointer,record,reference,actors):
 assert pointer in POINTERS
 uid=POINTERS[pointer];csuid,model_id,pin,nbytes=ACTORS[uid]
 assert record['uid']==uid and record['csuid']==csuid and record['objectId']==int(uid.split('/')[1].split(':')[0])
 assert reference==record['sourceEvidence']
 assert reference['kind']=='embedded-native-geometry' and reference['hashKind']==HASH_KIND
 assert reference['path']==TILE_PATH and reference['sha256']==pin and reference['bytes']==nbytes and reference['hashValid'] is True
 candidate=record['candidate']
 assert candidate['assetKind']=='embedded-native-geometry' and candidate['hashKind']==HASH_KIND and candidate['asset']==TILE_PATH and candidate['sha256']==pin
 assert reference['modelId']==model_id
 matches=[b for b in actors if b.get('uid')==uid];assert len(matches)==1
 actor=matches[0];assert actor['buildingCSUID']==csuid and actor['objectId']==record['objectId']
 geometry=actor['modelGeometry'];assert set(geometry)==FIELDS
 assert geometry['modelId']==model_id and geometry['buildingCSUID']==csuid
 assert geometry['sourceHashes']==record['sourceHashes']==reference['sourceHashes']
 raw=canonical(geometry);assert len(raw)==nbytes and sha(raw)==pin
 return dict(documentPath=CAPTURE_PATH,documentSHA256=CAPTURE_SHA,pointer=pointer,uid=uid,csuid=csuid,modelId=model_id,
  sourcePath=TILE_PATH,wholeTileSHA256=TILE_SHA,hashKind=HASH_KIND,completeCanonicalGeometrySHA256=pin,completeCanonicalGeometryBytes=nbytes,
  all18GeometryFieldsVerified=True,numericGeometryExcluded=False,metadataBoundarySkipped=False,ordinaryFileSHAOutsideExactPointersUnchanged=True,
  identityAccepted=False,physicalAccepted=False,installationApproved=False)

class BoundResolver:
 def __init__(self,capture_raw,tile_raw):
  assert sha(capture_raw)==CAPTURE_SHA and sha(tile_raw)==TILE_SHA
  self.context=json.loads(gzip.decompress(capture_raw));self.tile=json.loads(tile_raw)
 def handles(self,document_path,pointer):return document_path==CAPTURE_PATH and pointer in POINTERS
 def resolve(self,document_path,pointer,reference):
  assert self.handles(document_path,pointer)
  record=at(self.context,pointer.rsplit('/',1)[0])
  return verify_record(pointer,record,reference,self.tile['buildings'])

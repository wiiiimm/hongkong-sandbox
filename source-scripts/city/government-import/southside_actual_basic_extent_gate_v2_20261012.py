"""Complete actual BASIC bounds gate; no source, role or clearance approval."""
import hashlib,math,base64,struct
from fractions import Fraction as F
MODES=('productionPositionAttribute','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix')
IDENTITY=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]
def form_key(uid):return 'building:'+uid if uid.startswith('landsd/')else 'source-form:'+uid
def validate(proof,forms,native_obligations,domain,input_sha256):
 assert proof['schema']=='southside-complete-actual-basic-extents-v1'and proof['inputSHA256']==input_sha256
 assert proof['startAndEndInputsVerified']is True and proof['providerOriginalGovernmentMeshClaim']is False
 assert proof['modelGeometryChanges']==proof['terrainGeometryChanges']==0
 assert proof['domainBounds']==domain and len(forms)==proof['completeScannedForms']==1238
 rows=proof['rows'];assert len(rows)==len({r['uid']for r in rows})==len(forms)
 assert {r['uid']for r in rows}==set(forms)
 native_excluded={r['uid']for r in native_obligations['excluded']};native_nominated={r['uid']for r in native_obligations['nominated']}
 affected=[];excluded=[]
 for row in rows:
  uid=row['uid'];assert row['currentForm']==forms[uid]
  if row['classification']=='installed-native-already-exactly-bound':
   assert uid in native_excluded|native_nominated
   if uid in native_nominated:affected.append(uid)
   else:excluded.append(dict(uid=uid,classification='complete6649ActualFourStreamBoundsExclusion'))
   continue
  assert row['classification']=='actual-production-BASIC'and uid not in native_excluded|native_nominated
  assert row['wholeUnusedPositionVerticesIncluded']is True and row['identityWorldMatrix']==IDENTITY
  assert type(row['completePositionVertices'])is int and row['completePositionVertices']>=0
  assert type(row['completeIndexedFaces'])is int and row['completeIndexedFaces']>=0
  if row['completePositionVertices']==0:
   assert row['completeIndexedFaces']==0 and row['boundsByArithmetic']is None
   affected.append(uid);continue
  assert row['completeIndexedFaces']>0
  for field in ('positionAttributeSHA256','completeIndexSHA256','actualLiteralSHA256','explicitLeftAssociatedF32SHA256','explicitBalancedF32SHA256'):
   value=row[field];assert len(value)==64 and all(c in '0123456789abcdef'for c in value)
  assert set(row['boundsByArithmetic'])==set(MODES)
  assert row['modelMatrixUniformFloat32']==IDENTITY
  assert set(row['completeStreamBytesBase64'])==set(MODES)
  arrays={}
  sha_fields=dict(productionPositionAttribute='positionAttributeSHA256',actualLiteral='actualLiteralSHA256',explicitLeftAssociatedF32ModelMatrix='explicitLeftAssociatedF32SHA256',explicitBalancedF32ModelMatrix='explicitBalancedF32SHA256')
  for mode in MODES:
   raw=base64.b64decode(row['completeStreamBytesBase64'][mode],validate=True);size=4 if mode=='productionPositionAttribute'else 8
   assert len(raw)==row['completePositionVertices']*3*size and hashlib.sha256(raw).hexdigest()==row[sha_fields[mode]]
   arrays[mode]=struct.unpack('<'+('f'if size==4 else'd')*(len(raw)//size),raw);assert all(math.isfinite(v)for v in arrays[mode])
   values=arrays[mode];actual_bounds=[[min(values[k::3])for k in range(3)],[max(values[k::3])for k in range(3)]]
   assert row['boundsByArithmetic'][mode]==actual_bounds
  assert all(arrays[m]==arrays[MODES[0]]for m in MODES)
  raw=base64.b64decode(row['completeIndexBytesBase64'],validate=True);assert len(raw)==row['completeIndexedFaces']*3*4 and hashlib.sha256(raw).hexdigest()==row['completeIndexSHA256']
  indices=struct.unpack('<'+'I'*(len(raw)//4),raw);assert all(i<row['completePositionVertices']for i in indices)
  gaps=[]
  for mode in MODES:
   bounds=row['boundsByArithmetic'][mode]
   assert len(bounds)==2 and all(len(p)==3 and all(type(v)in(int,float)and math.isfinite(v)for v in p)for p in bounds)
   assert all(bounds[0][k]<=bounds[1][k]for k in range(3))
   gap=None
   for axis in (0,2):
    if F(domain[1][axis])<F(bounds[0][axis]):gap=dict(axis=axis,exactGapM=str(F(bounds[0][axis])-F(domain[1][axis])));break
    if F(bounds[1][axis])<F(domain[0][axis]):gap=dict(axis=axis,exactGapM=str(F(domain[0][axis])-F(bounds[1][axis])));break
   if gap is not None:gaps.append(dict(arithmetic=mode,**gap))
  if len(gaps)==4:excluded.append(dict(uid=uid,classification='actualGeneratedBASICAllUnusedFourModeStrictXZGap',proofs=gaps))
  else:affected.append(uid)
 assert set(affected)|{r['uid']for r in excluded}==set(forms)
 return dict(completeScannedForms=1238,affectedUIDs=sorted(affected),completeExclusionRecords=excluded,emptyGeometryNeverExcluded=True,physicalAccepted=False)
def resources(original,forms,capture_resources,account):
 removable={form_key(uid)for uid in forms}
 result=sorted((set(original)-removable)|set(capture_resources)|{form_key(uid)for uid in account['affectedUIDs']})
 assert set(capture_resources)<=set(result)and all(form_key(uid)in result for uid in account['affectedUIDs'])
 assert 0<len(result)<=1000,'actual-affected-resource-scope-still-exceeds-existing-guard'
 return result

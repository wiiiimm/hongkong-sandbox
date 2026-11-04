from pathlib import Path
import json,gzip,hashlib,base64,struct,math
R=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city');D=R/'docs/astra-city/government-import/government-xl-polyu-sports305582-authentic-local-private-terrain-draft-v1-20261013';O=D/'actual-stage1-preparation-v2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
v=read(O/'validation.json');a=read(O/'complete-evidence-audit.json');proof=read(D/'actual-basic-protection-proof.json.gz');inp=read(D/'actual-basic-protection-input.json.gz');assert v['allPassed'] and v['error'] is None and len(v['commands'])==5 and all(c['exitCode']==0 for c in v['commands']);assert len(a['evidenceRefs'])==8813
for q in a['evidenceRefs']:assert sha(R/q['path'])==q['sha256'],q['path']
for q in v['beforeEndLiteralPins']:assert q['unchanged'] and q['sha256']==q['actualSHA256']==sha(R/q['path'])
for q in v['commands']:assert sha(R/q['log']['path'])==q['log']['sha256']
assert len(proof['rows'])==25 and len(inp['forms'])==25 and {q['uid']for q in proof['rows']}=={q['uid']for q in inp['forms']};forms={q['uid']:q for q in inp['forms']};assert all(q['currentForm']==forms[q['uid']]for q in proof['rows']);assert proof['inputSHA256']==sha(D/'actual-basic-protection-input.json.gz')
closure=read(O/'literal-runtime-closure-schema.json');assert closure['schemaValidationPassed'] and len(closure['closures'])==7
for c in closure['closures']:
 assert c['computedImportsRejected'] and c['unsupportedDynamicImports']==0
 for p,h in c['inputHashes'].items():assert sha(R/p)==h
assert sha(R/'3d-viewer/city/data/manifest.json')==v['currentManifestSHA256']=='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
buffers=[]
for row in proof['rows']:
 if row['uid']=='landsd/305793:0':
  assert row['classification']=='installed-native-scalar-bounds-whole-terrain-regression-pending'and row['completeCurrentNativeBoundsVerbatim']['completeFaces']==59527 and row['installedEntryVerbatim']['publicationApproved']is False and row['wholeNativeBeforeAfterTerrainRegressionProved']is False;continue
 assert row['classification']=='actual-production-BASIC'and row['wholeUnusedPositionVerticesIncluded']is True
 if row['completePositionVertices']==0:assert row['completeIndexedFaces']==0 and row['boundsByArithmetic']is None;buffers.append(dict(uid=row['uid'],completePositionVertices=0,emptyGeometryExplicit=True));continue
 modes={'productionPositionAttribute':('positionAttributeSHA256','f'),'actualLiteral':('actualLiteralSHA256','d'),'explicitLeftAssociatedF32ModelMatrix':('explicitLeftAssociatedF32SHA256','d'),'explicitBalancedF32ModelMatrix':('explicitBalancedF32SHA256','d')};sums={}
 for mode,(key,kind)in modes.items():
  raw=base64.b64decode(row['completeStreamBytesBase64'][mode],validate=True);assert hashlib.sha256(raw).hexdigest()==row[key];n=row['completePositionVertices']*3;assert len(raw)==n*(4 if kind=='f'else 8);values=struct.unpack('<'+str(n)+kind,raw);assert all(math.isfinite(v)for v in values);bounds=[[min(values[k::3])for k in range(3)],[max(values[k::3])for k in range(3)]];assert bounds==row['boundsByArithmetic'][mode];sums[mode]=dict(bufferSHA256=row[key],completePositionVertices=n//3,bounds=bounds)
 ixraw=base64.b64decode(row['completeIndexBytesBase64'],validate=True);assert hashlib.sha256(ixraw).hexdigest()==row['completeIndexSHA256']and len(ixraw)==row['completeIndexedFaces']*3*4;indices=struct.unpack('<'+str(len(ixraw)//4)+'I',ixraw);assert all(i<row['completePositionVertices']for i in indices)
 buffers.append(dict(uid=row['uid'],allCompleteBuffersAndUnusedBoundsVerified=True,indexSHA256=row['completeIndexSHA256'],completeIndexedFaces=row['completeIndexedFaces'],streams=sums))
assert len(buffers)==24 and sum(q.get('completeIndexedFaces',0)for q in buffers)==11892
assert sum(q.get('streams',{}).get('productionPositionAttribute',{}).get('completePositionVertices',0)for q in buffers)==35676
out=dict(executor='ROOT',passed=True,all8813EvidenceHashesVerified=True,all8807BeforeEndPinsVerified=True,allFiveActualExit0LogsVerified=True,strict7LiteralClosuresVerified=True,complete25CurrentFormsVerified=True,complete24BufferIndicesUnusedBoundsVerified=True,positionVertices=35676,indexedFaces=11892,native59527PublicationHoldPreserved=True,sourceProofSHA256=sha(D/'actual-basic-protection-proof.json.gz'),sourceValidationSHA256=sha(O/'validation.json'),noGeometryPredicateTestsExporterConstructorLeaseOrDBReplayed=True)
p=O/'root-independent-stage1-current25-audit.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))

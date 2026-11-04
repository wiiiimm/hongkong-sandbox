"""Saved metadata and GLB JSON-envelope inspection only, no geometry buffers."""
import ast,datetime,gzip,hashlib,json,shutil,struct
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
H=ROOT/'source-scripts/city/government-import'
B=ROOT/'docs/astra-city/government-import'
OLD=B/'government-xl-lcsd-three-source-primary-identity-research-v1-20261013'
UID='landsd/281463:0'
SOURCE='1480540e0a32849425d5238eeea7ecb3a7124633226c1eae9cab2d041b968d86'
WORLD='d8ab9b872ef0696d3d95d8e47df0f64db2e540229961f0142d1e83af7cf08b22'
PINS={}
def pin(p):
 p=p.resolve();assert p.is_relative_to(ROOT);raw=p.read_bytes();rel=str(p.relative_to(ROOT));v=hashlib.sha256(raw).hexdigest()
 if rel in PINS:assert PINS[rel]==v
 PINS[rel]=v;return raw
def load(p):
 raw=pin(p);return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def write(n,value):
 with (HERE/n).open('x',encoding='utf-8') as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
def literal_local_python_closure(paths):
 pending=list(paths);seen=set()
 while pending:
  p=pending.pop().resolve()
  if p in seen:continue
  seen.add(p);tree=ast.parse(pin(p),filename=str(p))
  for node in ast.walk(tree):
   names=[]
   if isinstance(node,ast.Import):names=[n.name for n in node.names]
   if isinstance(node,ast.ImportFrom) and node.module:names=[node.module]
   for name in names:
    for base in (H,H.parent/'shared-modelling'):
     q=base/(name.replace('.','/')+'.py')
     if q.exists():pending.append(q)
 return sorted(str(p.relative_to(ROOT)) for p in seen)
def main():
 assert not (HERE/'provider-site-scope-findings.json').exists()
 priorpins=load(OLD/'review-file-pins.json')['allInputHashes']
 for rel,value in priorpins.items():assert hashlib.sha256(pin(ROOT/rel)).hexdigest()==value
 load(OLD/'actual-closure-validation.json');pin(OLD/'HANDOFF.md')
 identity=load(B/'government-xl-identity-search-20261009/result.json');row=next(r for r in identity['rows'] if r['uid']==UID)
 exact=[r for r in row['officialCandidates'] if r['attributes']['BuildingCSUID']=='3215622119P20070611'];assert len(exact)==1
 attrs=exact[0]['attributes'];assert attrs['BuildingID']==1100015179 and attrs['BuildingNameEN']=='LAI CHI KOK PARK SPORTS CENTRE' and attrs['BuildingBlockType']=='Podium'
 roles=load(B/'government-xl-spatial-surface-roles-20261009/281463-0.json.gz');assert roles['sourceSHA256']==SOURCE and roles['worldTrianglesSHA256']==WORLD
 selection=load(B/'government-xl-held-component-recovery-20261008/selection.json.gz');source=next(r for r in selection['rows'] if r['uid']==UID);assert source['sourceSHA256']==SOURCE
 raw=pin(ROOT/roles['originalPath']);assert hashlib.sha256(raw).hexdigest()==SOURCE
 container=gzip.decompress(raw);magic,version,length=struct.unpack_from('<III',container);assert magic==0x46546c67 and version==2 and length==len(container)
 count,tag=struct.unpack_from('<II',container,12);assert tag==0x4e4f534a
 meta=json.loads(container[20:20+count]);assert len(meta['meshes'])==1 and len(meta['meshes'][0]['primitives'])==1
 assert meta['accessors'][2]['count']==96281 and meta['accessors'][3]['count']==112731
 # JSON descriptors only. No binary buffer/accessor values read or transformed.
 tile=load(ROOT/'3d-viewer/city/data/tiles/-2_-3.json')
 own=next(r for r in tile['buildings'] if r['uid']==UID);assert own==source['source']['building']
 named=[r for r in tile['buildings'] if 'LAI CHI KOK' in (r.get('name') or '').upper() and 'SPORT' in (r.get('name') or '').upper()]
 assert len(named)==11 and sum(r['uid']==UID for r in named)==1
 ledger=load(B/'government-xl-identity-190-actionable-ledger-20261010/result.json');lr=next(r for r in ledger['rows'] if r['uid']==UID)
 group=load(B/'government-xl-322-complete-footprint-group-scan-v2-20261008/outcomes.json.gz');gr=next(r for r in group['rows'] if r['uid']==UID);assert gr['groupUids']==[UID]
 foreign=lr['rankedForeignActorsHistorical'];assert len(foreign)==7
 resources=sorted({'building:'+r['uid'] for r in named+foreign});assert 'building:'+UID in resources and len(resources)<=1000
 retrieval=load(HERE/'retrieval.json');mapreceipt=load(HERE/'park-map-retrieval.json');pages=load(HERE/'primary-document-page-lineage.json')
 allowed={'date','etag','last-modified','content-type','content-length','content-disposition'}
 for r in retrieval['sources']+[mapreceipt]:assert {k.lower() for k in r.get('provenanceHeaders',{})}<=allowed
 for r in retrieval['sources']:
  if r['saved']:assert hashlib.sha256(pin(HERE/'primary-documents'/r['filename'])).hexdigest()==r['sha256']
 assert mapreceipt['saved'];assert hashlib.sha256(pin(HERE/'primary-document-inspection/lcsd-original-park-map.png')).hexdigest()==mapreceipt['sha256']
 for p in pages['pages']:
  assert hashlib.sha256(pin(HERE/p['png'])).hexdigest()==p['pngSHA256'];assert hashlib.sha256(pin(HERE/p['text'])).hexdigest()==p['textSHA256']
 intro=(HERE/'primary-documents/park-introduction.html').read_text();outdoor=(HERE/'primary-documents/park-outdoor-facilities.html').read_text()
 assert 'nearby complementary facilities' in intro and 'Podium Garden' in outdoor
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert hashlib.sha256(pin(manifest)).hexdigest()=='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
 write('provider-site-scope-findings.json',{'uid':UID,'modelId':'B321562211902063C0','sourceSHA256':SOURCE,'sourceKey':roles['sourceKey'],'sourceAssetPath':roles['originalPath'],'worldTrianglesSHA256':WORLD,'sourceJSONMetadata':meta,'sourceJSONChunkSHA256':hashlib.sha256(container[20:20+count]).hexdigest(),'binaryPositionOrIndexBuffersDecoded':False,'exactProviderAttributes':attrs,'historicalExactOfficialCandidateVerbatim':exact[0],'originalRecoveryEnvelopeVerbatim':source,'currentFormVerbatim':own,'separatelyNamedCurrentFormsVerbatim':named,'sameNameDoesNotExpandOwnership':True,'priorSingleSourceGroupVerbatim':gr,'sevenIndependentForeignActorsVerbatim':foreign,'priorSourceRoleQualification':roles['qualification'],'currentManifestSHA256':'c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7','newPrimaryScopeFinding':'Provider GIS itself names a large podium as Sports Centre; owner distinguishes the separate arena from the park, and documents an actual StageI podium garden. A park/site-podium correspondence candidate exists, but exact original part mapping is missing.','viewerOnlyRenameWouldNotResolveHold':True,'primaryPlanPreciselyRegistered':False,'sourceChildSemanticLabelsAvailable':False,'sourceRoleAccepted':False,'identityAccepted':False,'physicalAccepted':False,'currentAcceptance':False,'permanentRejection':False,'nextAction':'ROOT-review the unexecuted complete original component-context caller. Recover only the missing106 source IDs/fullbody primitive mapping under the existing source/world pins, then inspect exact source placement alongside the actual primary maps. Do not redo fullclearance/projectionunion or grant same-name ownership.'})
 write('bounded-followup-search-and-fetch.json',{'additionalQueries':['site:lcsd.gov.hk "Lai Chi Kok Park" "roof"','site:gov.hk "Lai Chi Kok Park" "podium"','site:lcsd.gov.hk "Lai Chi Kok Park" "Stage II" station'],'actualPrimaryImagesViewed':['primary-document-inspection/lcsd-original-park-map.png','primary-document-inspection/government-podium-garden-physical-page-004-2400px.png'],'pool245RSAvailableBrowserFetch':{'exactURL':'https://www.legco.gov.hk/yr08-09/english/fc/pwsc/papers/p09-36e.pdf','tool':'cua.createBrowserTab','result':'Browser is not available: iab','noTabOrDocumentCreated':True,'noSecurityWarningBypassed':True,'actualDrawingStillMissing':True},'noDBOrLeaseOrNumericalSourceWorker':True})
 logs=HERE/'closed-execution-logs';logs.mkdir(exist_ok=False)
 for a,n in [('/tmp/lai-chi-kok281463-primary-followup-retrieval-20261013.log','retrieval.log'),('/tmp/lai-chi-kok281463-primary-followup-inspection-20261013.log','document-inspection.log')]:shutil.copyfile(a,logs/n)
 seeds=[HERE/'source-component-comparison-draft-v1.py',H/'exact_packed_world_geometry_20261009.py',H/'exact_original_shared_edge_component_census_v2_20261011.py',H/'xl_source_stream_binding_20261009.py',H/'xl-popcorn-source-investigations-checkpoints-20261009.py',H/'xl-spatial-surface-roles-20261009.py',H/'xl-heya-aqua-184286-installed-podium-complete-source-census-v1-20261011.py']
 closure=literal_local_python_closure(seeds)
 for p in H.glob('test_exact_original_shared_edge_component_census_v2_*.py'):pin(p)
 for p in (H/'run.py',H.parent/'shared-modelling/reservations.py',H.parent/'shared-modelling/db.py',H.parent/'shared-modelling/jobs.py'):pin(p)
 for p in sorted(HERE.rglob('*')):
  if p.is_file():pin(p)
 for rel,v in PINS.items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==v
 contract={'sourceSHA256':SOURCE,'worldTrianglesSHA256':WORLD,'currentAcceptance':False,'sourceGeometryChanges':0,'priorRolePath':'docs/astra-city/government-import/government-xl-spatial-surface-roles-20261009/281463-0.json.gz','canonicalResources':resources,'allInputHashes':PINS,'staticLiteralLocalPythonClosure':closure,'dynamicImportsExplicitlyPinned':['xl-popcorn-source-investigations-checkpoints-20261009.py'],'unexecutedNormalCaller':True,'noClaimOfActualHelperTestsOrProjectImports':True}
 write('comparison-input-contract.json',contract)
 write('actual-metadata-packet-validation.json',{'allPassed':True,'inputPinCount':len(PINS),'canonicalResources':len(resources),'unchangedOldPacketInputPins':len(priorpins),'sourceMetadataOnlyNoBinaryGeometryDecode':True,'exactSourceAssetSHA256':SOURCE,'sourceIndexedFacesFromIndexDescriptor':37577,'POSITIONDescriptorCount':96281,'sourceSemanticNamedChildren':False,'literalClosureFiles':len(closure),'actualModelOrHelperImports':0,'actualModelTestsRun':0,'actualNumericalWorkers':0,'rootCallerRemainsUnexecuted':True,'currentAcceptance':False,'findingsSHA256':hashlib.sha256((HERE/'provider-site-scope-findings.json').read_bytes()).hexdigest(),'contractSHA256':hashlib.sha256((HERE/'comparison-input-contract.json').read_bytes()).hexdigest()})
 print(json.dumps({'metadataPassed':True,'pins':len(PINS),'resources':len(resources),'staticCodeClosure':len(closure),'findingsSHA256':hashlib.sha256((HERE/'provider-site-scope-findings.json').read_bytes()).hexdigest(),'contractSHA256':hashlib.sha256((HERE/'comparison-input-contract.json').read_bytes()).hexdigest()}))
if __name__=='__main__':main()

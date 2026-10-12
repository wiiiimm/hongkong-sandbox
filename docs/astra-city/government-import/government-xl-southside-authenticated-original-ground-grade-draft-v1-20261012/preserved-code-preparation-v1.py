from pathlib import Path
import json,gzip,hashlib,ast,difflib
R=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city');H=R/'source-scripts/city/government-import';B=R/'docs/astra-city/government-import';D=B/'government-xl-southside-authenticated-original-ground-grade-draft-v1-20261012';D.mkdir(exist_ok=False)
read=lambda p:json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes());canonical=lambda x:hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
CURRENT=B/'government-xl-southside-315025-300867-current-grade-source-context-v1-20261012';AUTH=B/'government-xl-southside-315025-300867-unfiltered-original-sheets-comparison-v2-20261012'
old=read(CURRENT/'diagnostic.json.gz');auth=read(AUTH/'diagnostic.json.gz');bound={}
for q in old['rows']:bound[q['uid']+'|'+q['arithmetic']]={'currentRowCanonicalSHA256':canonical(q)}
for q in auth['rows']:bound[q['uid']+'|'+q['arithmetic']]['authenticatedRowCanonicalSHA256']=canonical(q)
meta={'currentGradeJobId':'7269234ae78ade5d10223502841ee35aba9e9d844d72c59d186ae56ee45cda71','authenticatedComparisonJobId':'a3b5b315b784f978ab22d511b638106abb15ec334dc1aeabf428e80ccf83675c','currentGradeDiagnosticSHA256':sha(CURRENT/'diagnostic.json.gz'),'authenticatedComparisonDiagnosticSHA256':sha(AUTH/'diagnostic.json.gz'),'boundModes':bound,'wholeOriginalTerrainFacets':774477,'sourceSlots':51560,'residualFacesPerWorld':463,'currentAcceptance':False}
(D/'actual-saved-mode-bindings.json').write_text(json.dumps(meta,sort_keys=True,indent=2)+'\n')
helper=H/'southside_authenticated_original_grade_scope_v1_20261012.py';helper.write_text('''"""Source-specific saved-proof scope and diagnostic path accounting, not acceptance."""
import hashlib,json
SOURCES={'landsd/315025:0':'85be44e7ab9410c850d3b7d59d05df2cd45fc1072ec2f984ddbb7b43c4d9ff7c','landsd/300867:0':'2293ba8925406abcdbd848486a772dfa8baa01caf0cfe96e749d5a3cd51210f1'}
COUNTS={'landsd/315025:0':11699,'landsd/300867:0':1191}
GROUND_COUNTS={'landsd/315025:0':25388,'landsd/300867:0':7186}
def canonical_sha(row):
 return hashlib.sha256(json.dumps(row,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def prepare(world,ground,current,authenticated,binding):
 uid=authenticated['uid'];assert uid in COUNTS and current['uid']==uid and current['arithmetic']==authenticated['arithmetic']
 assert canonical_sha(current)==binding['currentRowCanonicalSHA256']and canonical_sha(authenticated)==binding['authenticatedRowCanonicalSHA256']
 assert current['sourceSHA256']==authenticated['sourceSHA256']==SOURCES[uid]
 assert world.shape==(COUNTS[uid],3,3)and ground.shape==(GROUND_COUNTS[uid],3,3)
 wsha=hashlib.sha256(world.tobytes()).hexdigest();gsha=hashlib.sha256(ground.tobytes()).hexdigest()
 assert current['completeWorldSHA256']==authenticated['completeWorldSHA256']==wsha and authenticated['completeUnfilteredSelectedGroundSHA256']==gsha
 a=current['allCompleteOriginalFiniteRecords'];b=authenticated['completeOriginalFaceComparisons'];assert len(a)==len(b)==COUNTS[uid]
 assert [q['sourceFace']for q in a]==[q['sourceFace']for q in b]==list(range(COUNTS[uid]))
 records=[]
 for i,(old,new)in enumerate(zip(a,b)):
  fsha=hashlib.sha256(world[i].tobytes()).hexdigest();assert old['completeOriginalFacetSHA256']==new['completeOriginalFacetSHA256']==fsha
  assert new['currentDrawnGroundComparisonRetainedVerbatim']==old['currentDrawnGroundComparison']and new['orientationDescriptiveOnly']==old['exactOrientationDiagnostic']
  proof=new['unfilteredAuthenticatedOriginalGroundComparison'];assert type(proof['completeFiniteOrdinaryBoundProved'])is bool
  for p in [proof['coarse']]+([]if proof['paired']is None else[proof['paired']]):assert p['sourceFaceSHA256']==fsha and p['completeCurrentGroundSHA256']==gsha and p['fullAcceptance']is False and p['installationApproved']is False
  records.append(dict(sourceFace=i,completeOriginalFacetSHA256=fsha,exactOrientationDiagnostic=old['exactOrientationDiagnostic'],currentDrawnGroundComparison=old['currentDrawnGroundComparison'],authenticatedOriginalGroundComparison=proof))
 topology=current['completeOriginalTopology'];zeros=set(topology['exactNonrenderingOriginalFaces']);groups=topology['sharedEdgeConnectedComponents'];mapping={}
 for j,ids in enumerate(groups):
  assert ids and len(ids)==len(set(ids))
  for i in ids:assert i not in zeros and i not in mapping;mapping[i]=j
 assert set(mapping)==set(range(COUNTS[uid]))-zeros
 failed={q['sourceFace']for q in records if not q['authenticatedOriginalGroundComparison']['completeFiniteOrdinaryBoundProved']};assert sorted(failed)==authenticated['allAuthenticatedGroundFailuresRetained']
 steep={q['sourceFace']for q in records if q['exactOrientationDiagnostic']=='steep-wall'};assert not steep&zeros
 nonsteep=failed-steep-zeros;eligible=sorted(set(range(COUNTS[uid]))-zeros-nonsteep)
 return dict(records=records,topology=topology,zeros=zeros,steep=steep,failed=failed,nonsteep=nonsteep,eligible=eligible,componentMap=mapping)
def account_path(ids,*,eligible,component_map,positive_grade_ids,terminal_cap_strict,interfaces,raw_helper_path):
 assert ids and len(ids)==len(set(ids))and set(ids)<=set(eligible)
 assert len({component_map[i]for i in ids})==1
 assert len(interfaces)==len(ids)-1
 nonempty=len(ids)>1 and bool(interfaces)
 genuine=ids[0]in positive_grade_ids
 edges=all(q['hasWholeStrictlyExposedOriginalEdge']for q in interfaces)
 cap=bool(raw_helper_path['hasExactOriginalStrictClearCapRoofPath']and terminal_cap_strict)
 return dict(nonemptyOriginalWallPath=nonempty,sourceFaceHasGenuinePositiveDimensionalGradeContact=genuine,diagnosticGradeToWholeClearCapAndExposedEdges=bool(nonempty and genuine and cap and edges),terminalCapWholeFiniteStrictlyClear=cap,allPathInterfacesHaveWholeExposedSharedEdge=edges,rootCredit=False,fullBodyRootProved=False)
''')
source=H/'xl-southside-315025-300867-current-grade-source-context-v1-20261012.py';s=source.read_text()
s=s.replace('DRAFT complete Southside/station saved-finite/grade/shared-edge/cap diagnostic.','UNEXECUTED authentic-original-ground residual grade/shared-edge/cap diagnostic.')
s=s.replace("from exact_original_shared_edge_component_census_v2_20261011 import census", "from southside_authenticated_original_grade_scope_v1_20261012 import prepare,account_path")
s=s.replace("FINITE=BASE/'government-xl-southside-315025-300867-complete-four-stream-current-finite-v1-20261012'", "FINITE=BASE/'government-xl-southside-315025-300867-unfiltered-original-sheets-comparison-v2-20261012'\nCURRENT_GRADE=BASE/'government-xl-southside-315025-300867-current-grade-source-context-v1-20261012'")
s=s.replace('southside-current-grade-source-context-draft-v1','southside-authenticated-original-ground-grade-draft-v1').replace('southside-315025-300867-current-grade-source-context-v1','southside-315025-300867-authenticated-original-ground-grade-v1')
# Restore the prior current-grade folder after batch substitution.
s=s.replace("CURRENT_GRADE=BASE/'government-xl-southside-315025-300867-authenticated-original-ground-grade-v1-20261012'", "CURRENT_GRADE=BASE/'government-xl-southside-315025-300867-current-grade-source-context-v1-20261012'")
s=s.replace("DRAFT/'ocean-template-to-southside-caller.diff'", "DRAFT/'current-grade-to-authenticated-grade-caller.diff'")
s=s.replace("receipts=[read(folder/'result.json')for folder in [INPUT,FINITE]]", "receipts=[read(folder/'result.json')for folder in [INPUT,FINITE,CURRENT_GRADE]]")
s=s.replace("'7e57f56133527ebed464d45f723be5dd85660d3e31265d29b4a70d3db0e117dd'", "'a3b5b315b784f978ab22d511b638106abb15ec334dc1aeabf428e80ccf83675c','7269234ae78ade5d10223502841ee35aba9e9d844d72c59d186ae56ee45cda71'")
s=s.replace("zip([INPUT,FINITE],receipts)","zip([INPUT,FINITE,CURRENT_GRADE],receipts)").replace("assert not receipt['currentAcceptance'] and not receipt['physicalAccepted']", "assert receipt['currentAcceptance']is False")
start=s.index(" saved=read(FINITE/'diagnostic.json.gz');rows=");end=s.index(" history=read(INVENTORY);",start)
s=s[:start]+''' saved=read(FINITE/'diagnostic.json.gz');rows={(q['uid'],q['arithmetic']):q for q in saved['rows']};assert len(rows)==8 and set(rows)=={(u,m)for u in UIDS for m in MODES}
 prior=read(CURRENT_GRADE/'diagnostic.json.gz');prior_rows={(q['uid'],q['arithmetic']):q for q in prior['rows']};assert set(prior_rows)==set(rows)
 selected=read(FINITE/'complete-unfiltered-authenticated-source-ground.json.gz');assert selected['completeAllOriginalSheetFacets']==774477 and selected['sourceCoordinateTransformsUnchanged']is True and selected['currentRendererGround']is False and selected['terrainGeometryChanges']==0
 grounds={q['uid']:q for q in selected['actorConservativeGrounds']};assert set(grounds)==set(UIDS)
 binding_file=DRAFT/'actual-saved-mode-bindings.json';bindings=read(binding_file);refs.append(binding_file)
 assert bindings['currentGradeDiagnosticSHA256']==digest((CURRENT_GRADE/'diagnostic.json.gz').read_bytes())and bindings['authenticatedComparisonDiagnosticSHA256']==digest((FINITE/'diagnostic.json.gz').read_bytes())
 assert sum(len(q['completeOriginalFaceComparisons'])for q in rows.values())==51560
 for uid in UIDS:
  item=data[uid];assert item['sourceSHA256']==SOURCES[uid] and set(item['completeWorldStreams'])==set(MODES)
  g=grounds[uid];ground=np.asarray(g['completeSelectedFacets'],dtype='<f8');assert digest(ground.tobytes())==g['completeSelectedFacetSHA256']and g['closedAABBWholeFacetSelection']is True and g['allSlopesVerticalAndCollapsedProjectionFacetsRetained']is True and g['noHeightAreaOrSlopeFilter']is True
  current_ground=np.asarray(item['completeDrawnGround'],dtype='<f8');assert digest(current_ground.tobytes())==item['completeDrawnGroundSHA256']
  for mode in MODES:
   world=np.asarray(item['completeWorldStreams'][mode]['completeWorldTriangles'],dtype='<f8');assert digest(world.tobytes())==item['completeWorldStreams'][mode]['completeWorldTriangleSHA256']
   p=prior_rows[uid,mode];assert p['completeGroundSHA256']==item['completeDrawnGroundSHA256']
   prepared=prepare(world,ground,p,rows[uid,mode],bindings['boundModes'][uid+'|'+mode])
   assert len(prepared['failed'])==(300 if uid==UIDS[0]else163)and len(prepared['nonsteep'])==(12 if uid==UIDS[0]else0)
''' +s[end:]
s=s.replace("return receipts,refs,pins,inputs,data,rows,history", "return receipts,refs,pins,inputs,data,rows,history,prior_rows,grounds,bindings")
s=s.replace("receipts,refs,pins,inputs,data,saved_rows,history=state", "receipts,refs,pins,inputs,data,saved_rows,history,prior_rows,grounds,bindings=state")
s=s.replace("ground=np.asarray(item['completeDrawnGround'],dtype='<f8')", "ground=np.asarray(grounds[uid]['completeSelectedFacets'],dtype='<f8')")
start=s.index("   topology=census(");end=s.index("   # Excluding failed non-walls",start)
s=s[:start]+'''   prior=saved_rows[uid,mode];prepared=prepare(world,ground,prior_rows[uid,mode],prior,bindings['boundModes'][uid+'|'+mode]);topology=prepared['topology'];zeros=prepared['zeros'];steep=prepared['steep'];records=prepared['records'];failed=prepared['failed'];eligible=prepared['eligible']
''' +s[end:]
s=s.replace("records[i]['currentDrawnGroundComparison']", "records[i]['authenticatedOriginalGroundComparison']").replace("records[cap]['currentDrawnGroundComparison']", "records[cap]['authenticatedOriginalGroundComparison']")
# Add exact original component constraint and diagnostic accounting, retaining all raw rows.
s=s.replace("cap=ids[-1];nonempty_wall_path=bool(len(ids)>1 and interfaces);edge_rows.append", "cap=ids[-1];account=account_path(ids,eligible=eligible,component_map=prepared['componentMap'],positive_grade_ids=positive_grade_ids,terminal_cap_strict=strict(records[cap]['authenticatedOriginalGroundComparison']),interfaces=interfaces,raw_helper_path=path);nonempty_wall_path=account['nonemptyOriginalWallPath'];edge_rows.append")
s=s.replace("rootCredit=False))", "rootCredit=False,fullBodyRootProved=False,sourceOriginalComponent=prepared['componentMap'][ids[0]],diagnosticAccountVerbatim=account))")
s=s.replace("allCurrentGroundFacetsRetained=len(ground)", "allAuthenticatedOriginalGroundFacetsRetained=len(ground),currentDrawnGroundSHA256Retained=item['completeDrawnGroundSHA256'],currentRawFailureIdsRetained=prior['allCurrentFailuresRetainedVerbatim'],all463ResidualsAccountedAsUnqualified=True")
s=s.replace("completeFiniteReceiptReusedExactly=receipts[1]['jobId']", "completeAuthenticFiniteReceiptReusedExactly=receipts[1]['jobId'],priorCurrentGradeReceiptRetained=receipts[2]['jobId'],completeSourceSlots=51560,authenticSourceGroundNotRenderer=True")
s=s.replace("'southside-complete-current-grade-exposed-original-edge-clear-cap-diagnostic-no-role-credit'", "'southside-authenticated-original-ground-residual-grade-edge-cap-diagnostic-no-root-role-credit'")
s=s.replace("'southside-complete-current-grade-'", "'southside-authenticated-original-grade-'")
s=s.replace("HELPERS=['run.py'", "HELPERS=['southside_authenticated_original_grade_scope_v1_20261012.py','test_southside_authenticated_original_grade_scope_v1_20261012.py','run.py'")
# Pin this exact saved-data input contract; no tests or numerical worker have run.
p=H/'xl-southside-315025-300867-authenticated-original-ground-grade-v1-20261012.py';ast.parse(s);p.write_text(s)
(D/'current-grade-to-authenticated-grade-caller.diff').write_text(''.join(difflib.unified_diff(source.read_text().splitlines(True),s.splitlines(True),fromfile=str(source.relative_to(R)),tofile=str(p.relative_to(R)))))
print(json.dumps({'callerPath':str(p),'callerSHA256':sha(p),'helperPath':str(helper),'helperSHA256':sha(helper),'modeBindingsSHA256':sha(D/'actual-saved-mode-bindings.json'),'ASTOnly':True,'workerStarted':False}))

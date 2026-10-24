"""UNEXECUTED source-only selective13 preparation, not a terrain constructor.
Uses exact captured historical parent bytes; no current runtime approval transfer.
"""
import sys,json,hashlib
from pathlib import Path
from fractions import Fraction
import numpy as np
from run import ROOT,HERE,read,digest
from southside_selective13_guard_union_parent_correspondence_draft_v1_20261013 import complete_union_atoms,parent_plane_correspondence,complete_closed_parent_coverage
BASE=ROOT/'docs/astra-city/government-import';D=BASE/'government-xl-southside-private-authentic-terrain-draft-v2-20261012';PLAN=D/'selective13-parent-restoration-draft-v1';OUT=PLAN/'closed-core-preparation-v1'
COMPAT=D/'neighbour-regression-cause-draft-v1/saved-piece-whole-form-compatibility-v2/diagnostic.json';AUDIT=D/'neighbour-regression-cause-draft-v1/saved-piece-v2-independent-result-audit.json';PACKET=PLAN/'readonly-source-plane-correspondence-and-independent3-context.json';INPUT=BASE/'government-xl-southside-315025-300867-current-actual-ground-capture-v1-20261012';GROUND=BASE/'government-xl-southside-source-local-v4-private-ground-capture-v1-20261012/production-two-scene-ground.json.gz';HISTORICAL='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'

def preflight():
 assert digest(COMPAT.read_bytes())=='2ea74a53ea190b2f163a252b20ccc984cf4a8f8b23aaa604d4fa4e975f896188'and digest(AUDIT.read_bytes())=='d827075d50d81ede8597f89dccfa9b1b372bad3430c677cb76a70f1e295242c2'
 assert digest(PACKET.read_bytes())=='513ca1348c890a5eb35cc80de06bfc0126f40de755106e67b1c70a2e119a8bd5'
 q=read(COMPAT);audit=read(AUDIT);packet=read(PACKET);ground=read(GROUND);source=read(INPUT/'complete-two-actor-four-stream-ground-inputs.json.gz')
 assert len(q['rows'])==8 and len(q['baselineFalseAuthenticTrueRestrictionFailures'])==1560 and q['unresolvedRestrictions']==[]
 assert len(packet['selective13UIDs'])==13 and set(packet['selective13UIDs'])==set(audit['formsWithNoSavedAuthenticImprovementLoss'])
 assert len(audit['formsWithSavedAuthenticImprovementLoss'])==3 and all(r['originalBodyIDs']==[0]for r in audit['perModeConflictRecords'])
 archive=INPUT/'captured-manifest.json';assert digest(archive.read_bytes())==HISTORICAL
 # Apply the same exact historical contract to both immutable pin inventories.
 # Only the recorded manifest path AND historical SHA resolve to real archive
 # bytes. All other files retain ordinary byte checking; no current credit.
 def captured_pin(path,sha):
  if path=='3d-viewer/city/data/manifest.json':
   assert sha==HISTORICAL;assert digest(archive.read_bytes())==sha;return archive
  p=ROOT/path;assert digest(p.read_bytes())==sha;return p
 assert q['inputHashes']['3d-viewer/city/data/manifest.json']==HISTORICAL
 refs=[COMPAT,AUDIT,PACKET,GROUND,archive,INPUT/'complete-two-actor-four-stream-ground-inputs.json.gz',Path(__file__),PLAN/'METHOD.md']
 for inventory in [packet['allInputHashes'],q['inputHashes']]:
  for path,sha in inventory.items():refs.append(captured_pin(path,sha))
 tests=PLAN/'immutable-preparation-tests-v1';v=read(tests/'validation.json');assert v['testCount']==10 and v['actualExitCode']==0 and v['allPassed']
 assert digest((tests/'tests.log').read_bytes())==v['testLogSHA256']
 for path,sha in v['codePins'].items():p=ROOT/path;assert digest(p.read_bytes())==sha;refs.append(p)
 refs.extend([tests/'validation.json',tests/'tests.log']);pins={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in sorted(set(refs))}
 baseline=np.asarray(ground['baseline']['completeRegionalPosition'],dtype='<f8').reshape(-1,3,3);assert baseline.shape==(144,3,3)and digest(baseline.tobytes())==packet['capturedBaselineTriangleSHA256']
 for uid,row in source['rows'].items():
  a=np.asarray(row['completeDrawnGround'],dtype='<f8');assert digest(a.tobytes())==packet['completeOriginalCurrentGroundCorrespondence'][uid]['savedGroundSHA256']
 return dict(q=q,packet=packet,source=source,baseline=baseline,pins=pins)

def main():
 s=preflight()
 if '--preflight-only'in sys.argv:print(json.dumps(dict(savedSlots=51560,selectiveForms=13,conflictingForms=3,sourceViews=8,capturedParentFaces=144,tenTestsBound=True,historicalManifestArchiveSHA256=HISTORICAL,noDB=True,noLease=True,noTerrainConstruction=True,noCurrentInputRebind=True,currentAcceptance=False)));return
 assert '--prepare-core-only'in sys.argv,'Only an explicitly reviewed source-only core preparation is supported; no terrain constructor.'
 assert not OUT.exists();union=complete_union_atoms(s['packet']['completeSelective13DomainsVerbatim']);matches={u:parent_plane_correspondence(r['completeDrawnGround'],s['baseline'])for u,r in s['source']['rows'].items()}
 for u,proof in matches.items():assert proof['uniqueActualBaselineFacetBySavedGroundFacet']==s['packet']['completeOriginalCurrentGroundCorrespondence'][u]['uniqueCurrentBaselineFaceBySavedGroundFace']
 coverage=complete_closed_parent_coverage(union,s['baseline'])
 out=dict(schema='southside-selective13-closed-core-parent-preparation-v1',completeRawClosedDomainUnion=union,completeSavedParentCorrespondence=matches,completeClosedParentCoverage=coverage,constructionPrerequisiteSatisfied=coverage['allClosedPrimitivesCovered'],separateCollarNotConstructedOrQualified=True,all1560NegativeRestrictionsRetainedAt=dict(path=str(COMPAT.relative_to(ROOT)),sha256=digest(COMPAT.read_bytes())),independent3ConflictContextsVerbatim=s['packet']['independent3ConflictContexts'],all19HistoricalObligationsVerbatim=s['q']['all19HistoricalObligationsVerbatim'],all46ProtectedFormsVerbatim=s['q']['all46ProtectedFormsVerbatim'],historicalCapturedBaselineOnly=True,historicalManifestArchive=dict(path=str((INPUT/'captured-manifest.json').relative_to(ROOT)),sha256=HISTORICAL),inputHashes=s['pins'],noSourceGroundClearanceReplay=True,noNewTerrain=True,noDB=True,noLease=True,currentAcceptance=False,physicalAccepted=False,installationApproved=False)
 for p,h in s['pins'].items():assert digest((ROOT/p).read_bytes())==h
 OUT.mkdir();p=OUT/'closed-core-preparation.json';p.open('x').write(json.dumps(out,indent=2,sort_keys=True,default=lambda v:str(v)if isinstance(v,Fraction)else (_ for _ in ()).throw(TypeError(type(v).__name__)))+'\n');print(json.dumps(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()),closedPrimitiveCount=len(union['completeRawDomainRecords']),uniquePositiveAreaUnionAtoms=len(union['atoms']),completeParentCoverage=coverage['allClosedPrimitivesCovered'],currentAcceptance=False)))
if __name__=='__main__':main()

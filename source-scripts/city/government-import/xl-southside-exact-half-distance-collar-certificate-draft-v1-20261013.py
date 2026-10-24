"""UNEXECUTED exact source-derived closed mask/packing certificate only."""
import sys,json,gzip,hashlib
from pathlib import Path
from fractions import Fraction as F
from southside_exact_half_distance_closed_collar_draft_v1_20261013 import make_certificate
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
P=ROOT/'docs/astra-city/government-import/government-xl-southside-private-authentic-terrain-draft-v2-20261012/selective13-parent-restoration-draft-v1'
DISTANCE=P/'all-saved-negative-region-exact-core-distance-v1/diagnostic.json.gz';AUDIT=P/'readonly-exact-distance-result-audit-v1.json';PREP=P/'immutable-exact-distance-import-preflight-v1/validation.json'
METHOD=P/'EXACT-HALF-DISTANCE-COLLAR-CERTIFICATE-DRAFT-METHOD.md';OUT=P/'exact-half-distance-closed-mask-certificate-v1'
CODE=[Path(__file__),HERE/'southside_exact_half_distance_closed_collar_draft_v1_20261013.py',HERE/'test_southside_exact_half_distance_closed_collar_draft_v1_20261013.py']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def preflight():
 assert sha(DISTANCE)=='ceac65ffb0e573c6d70bd024740a7d223d508c0894455c345da84f709cf3cc77'and sha(AUDIT)=='26949d1f768e44b6c639f8f1f2ee79e7f20a3f1ea29a669b2c7663f5fa3c2bc5'and sha(PREP)=='17ec5c2190e17a3f77b677a6a1b81086f1c59b1d8a1b5c19d820a96c9a5087f4'
 a,v=read(AUDIT),read(PREP);assert a['negativeRegions']==4784 and a['unresolved']==0 and a['producerProcessesAbsent']and v['allPassed']
 pins=dict(v['completePinnedInputs'])
 for path,h in a['allInputHashes'].items():assert path not in pins or pins[path]==h;pins[path]=h
 for path,h in pins.items():assert sha(ROOT/path)==h,path
 validation_path=P/'immutable-exact-half-distance-collar-fixtures-v1/validation.json';validation=read(validation_path);log=validation_path.parent/'tests.log'
 assert validation['testCount']==14 and validation['actualExitCode']==0 and validation['allPassed']and sha(log)==validation['testLogSHA256']
 assert validation['codePins']=={str(p.relative_to(ROOT)):sha(p)for p in CODE}
 q=read(DISTANCE);assert q['inputHashes']==a['allInputHashes']and q['exactGlobalDistanceInfimumM']==a['exactGlobalDistanceInfimumM']and q['completeGlobalMinimumWitnesses']==a['completeGlobalMinimumWitnesses']
 for p in [*CODE,DISTANCE,AUDIT,PREP,METHOD,validation_path,log]:pins[str(p.relative_to(ROOT))]=sha(p)
 return q,pins
def main():
 q,pins=preflight()
 if '--preflight-only'in sys.argv:
  print(json.dumps(dict(savedRegionCount=4784,originalCoreLineage=3653,uniqueCoreHulls=831,priorFailedFiveMetreRecords=3484,fixtureCount=14,noDB=True,noLease=True,noDistanceReplay=True,noTerrainConstruction=True,currentAcceptance=False)));return
 assert '--prepare-source-bound-collar-only'in sys.argv and not OUT.exists()
 certificate=make_certificate(q)
 for path,h in pins.items():assert sha(ROOT/path)==h,path
 out=dict(schema='southside-exact-half-distance-closed-mask-certificate-v1',sourceBoundMaskCertificate=certificate,originalCompleteDistanceArtifact=dict(path=str(DISTANCE.relative_to(ROOT)),sha256=sha(DISTANCE)),completeGlobalMinimumWitnessesRetained=q['completeGlobalMinimumWitnesses'],all3484PriorFiveMetreNegativesVerbatim=q['all3484PriorCollarNegativesVerbatim'],all19HistoricalObligationsVerbatim=q['all19HistoricalObligationsVerbatim'],all46ProtectedFormsVerbatim=q['all46ProtectedFormsVerbatim'],inputHashes=pins,historicalCapturedSourceOnly=True,all117ActorAnd6650NativeTerrainGuardsRemainUnprovedHere=True,noDB=True,noLease=True,noDistanceReplay=True,noSourceDecode=True,noWholeFiniteReplay=True,noTerrainConstruction=True,physicalAccepted=False,currentAcceptance=False)
 OUT.mkdir();p=OUT/'certificate.json.gz';payload=json.dumps(out,sort_keys=True,separators=(',',':'),default=lambda v:str(v)if isinstance(v,F)else (_ for _ in ()).throw(TypeError(type(v).__name__))).encode();p.open('xb').write(gzip.compress(payload,mtime=0))
 print(json.dumps(dict(path=str(p.relative_to(ROOT)),sha256=sha(p),exactDerivedUniformWidthM=str(certificate['exactDerivedUniformWidthM']),exactMaxMaskVertexPackingErrorM=str(certificate['exactMaxMaskVertexPackingErrorM']),all4784ClosedRegionsSeparatedFromPackedMask=certificate['all4784ClosedRegionsSeparatedFromPackedMask'],noTerrainConstruction=True,currentAcceptance=False)),flush=True)
if __name__=='__main__':main()

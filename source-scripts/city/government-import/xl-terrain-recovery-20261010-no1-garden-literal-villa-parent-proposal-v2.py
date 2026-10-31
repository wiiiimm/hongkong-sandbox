"""Exact current retained-child metadata restoration; no geometry alteration."""
import copy,importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BATCH="xl-terrain-recovery-20261010-no1-garden-literal-villa-parent-proposal-v2";BASE=ROOT/"docs/astra-city/government-import";DOC=BASE/BATCH;LOCAL=HERE/"local"/BATCH
PRIOR=BASE/"xl-terrain-recovery-20261010-no1-garden-literal-villa-parent-proposal-v1"
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();old=read(PRIOR/"terrain-candidates.json")[0];assert ref(ROOT/old["path"])["sha256"]==old["sha256"]
 wrapper=read(ROOT/old["path"]);parent_path=ROOT/"3d-viewer"/old["replaces"]["url"];assert digest(parent_path.read_bytes())==old["replaces"]["sha256"];parent=read(parent_path)
 originals={c["id"]:c for c in parent["patches"]};records=[]
 for c in wrapper["patches"]:
  if c["id"] not in originals:continue
  current=originals[c["id"]]
  if c==current:continue
  x=copy.deepcopy(c);y=copy.deepcopy(current);a=x["nativeMesh"]["sourceOverlap"];b=y["nativeMesh"]["sourceOverlap"];first=Path(a["evidencePath"]);second=Path(b["evidencePath"])
  first=first if first.is_absolute() else ROOT/first;second=second if second.is_absolute() else ROOT/second
  assert first.read_bytes()==second.read_bytes() and digest(first.read_bytes())==a["evidenceSHA256"]==b["evidenceSHA256"]
  a["evidencePath"]=b["evidencePath"];assert x==y,"Only byte-identical audit path relocation may be restored"
  records.append(dict(childId=c["id"],relocatedHistoricalAudit=ref(first),actualCurrentAudit=ref(second),allGeometryAndOtherMetadataIdentical=True))
 wrapper["patches"]=[copy.deepcopy(originals[c["id"]]) if c["id"] in originals else c for c in wrapper["patches"]]
 assert [c for c in wrapper["patches"] if c["id"] in originals]==parent["patches"] and len(originals)==8
 asset=LOCAL/"terrain-central-no1-with-literal-villa-parent-facets-v2.json";save(asset,wrapper);candidate={**old,"path":ref(asset)["path"],"sha256":ref(asset)["sha256"]};save(DOC/"terrain-candidates.json",[candidate])
 prior=read(PRIOR/"diagnostic.json.gz");refs=[ref(p) for p in [Path(__file__),PRIOR/"result.json",PRIOR/"diagnostic.json.gz",PRIOR/"terrain-candidates.json",ROOT/old["path"],parent_path,asset]]+[r[k] for r in records for k in ["relocatedHistoricalAudit","actualCurrentAudit"]]
 result={**prior,"priorProposal":old,"newTerrainCandidate":candidate,"retainedAuditPathRestorations":records,"otherNestedChildrenLiterallyUnchanged":True,"allEightChildRecordsEqualActualCurrentParent":True,"sourceGeometryChanges":0,"terrainProposalGeometryChanged":True,"evidenceRefs":refs,"fullAcceptance":False,"installationApproved":False};save(DOC/"diagnostic.json.gz",result)
 spec=importlib.util.spec_from_file_location("f",HERE/"xl-popcorn-source-investigations-checkpoints-20261009.py");m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,"exact-current-eight-retained-child-record-restoration-v1",[ROOT/r["path"] for r in refs],dict(uids=["landsd/304714:0"],restoredAuditPaths=len(records),allEightChildRecordsEqualActualCurrentParent=True,allGeometryIdenticalToPriorProposal=True,sourceGeometryChanges=0,terrainProposalGeometryChanged=True,fullAcceptance=False))
 print(json.dumps(dict(restoredAuditPaths=len(records),currentEightChildrenExactlyEqual=True,fullAcceptance=False)),flush=True)
if __name__=="__main__":main()

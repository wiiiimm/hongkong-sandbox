"""Summarise exact saved source junction failures; no geometry or acceptance change."""
from pathlib import Path
import gzip,hashlib,json
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'docs/astra-city/government-import'
def read(p):
 raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
 src=BASE/'government-xl-citywalk-saved294-source-layer-attribution-v1-20261014'
 context=BASE/'government-xl-citywalk-saved294-combined-junction-review-v1-20261015'
 out=BASE/'government-xl-citywalk-saved294-junction-decision-v1-20261015';assert not out.exists()
 result=read(src/'result.json');assert result['jobId']=='6f681ae0af407d16e1583450094f267862963ed716b28523601ca4658e0b7806'
 for q in result['evidenceRefs']:assert ref(ROOT/q['path'])==q
 data=read(src/'complete-saved294-source-layer-attribution.json.gz');assert len(data['sourceWorldRows'])==4
 summaries=[]
 for world in data['sourceWorldRows']:
  rows=world['rows'];assert len(rows)==294
  for uid in sorted({r['uid'] for r in rows}):
   rr=[r for r in rows if r['uid']==uid];g=[r['nativeStyleFloat32StrictDiagnostic']['computedGap'] for r in rr]
   summaries.append(dict(world=world['sourceWorld'],uid=uid,savedPoints=len(rr),strictNativeGapRange=[min(g),max(g)],beyondHalfMetre=sum(x<-.5 for x in g),pointsWithLowerContactLayer=sum(bool(r['EPSModelGeometry']['lowerHitsWithinExistingContactInterval'])for r in rr),highestSourceFaces=sorted({h['faceIndex']for r in rr for h in r['EPSModelGeometry']['highestSourceHits']})))
 out.mkdir();report=dict(sourceOnly=True,newlyInstalled=0,installationApproved=False,permanentRejection=False,sourceGeometryChanges=0,inputs=[ref(src/'result.json'),ref(src/'complete-saved294-source-layer-attribution.json.gz'),ref(context/'review-inputs.json'),ref(context/'combined-junction-context-2160x1800.png'),ref(Path(__file__))],rows=summaries,decision='Do not run another terrain-only repair for these 294 source-to-source interface points. Their queried support is unchanged original podium geometry; terrain adjustment cannot lower that geometry.',nextAction='Investigate exact tower/podium authored junction applicability or an authoritative alternate original source. The combined cropped source view alone does not establish a passing strict interface. Retain all current failure evidence; no corruption or permanent-uninstallable conclusion.')
 (out/'decision.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(rows=len(summaries),sourceOnly=True,newlyInstalled=0)))
if __name__=='__main__':main()

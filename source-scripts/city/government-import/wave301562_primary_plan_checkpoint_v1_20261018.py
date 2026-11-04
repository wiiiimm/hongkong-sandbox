"""Checkpoint primary-plan context without granting placement or source-support approval."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-wave301562-primary-plan-context-v1-20261018';DOC=BASE/BATCH
PRIOR=BASE/'government-xl-wave301562-support-inventory-v1-20261018'
def main():
 r=read(PRIOR/'result.json');pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 provenance=read(DOC/'provenance.json');assert digest((DOC/'the-wave-sales-brochure.pdf').read_bytes())==provenance['sha256']
 review=dict(uid='landsd/301562:0',sourceSHA256='8326b663b61047b8728c2fa49550b0ab26b48868a05b8b2588db33004acf1959',primaryDocument=provenance,inspectedPdfPages=[20,47,48,92,93],inspectedPrintedPages=[18,45,46,90,91],sourceFaceCount=144,rawUnresolvedSamples=17,rawIncidentFaces=[80,87,88,138,142],observations=[
 'The layout labels a refuse-storage/material-recovery chamber and open filtration plant at ground level along the end of Tower2, immediately beside the ramp to carpark.',
 'The first-basement plan depicts descending vehicle access in this end-of-development area. Sections distinguish ground floor and basement levels, with adjacent vehicular access at12.71 to15.20m HKPD.',
 'Diagnostic38.6degree rotation of unchanged worldXZ shows the triangular service source beyond Tower2 in the corresponding service-strip position. This is qualitative correspondence, not surveyed image registration.',
 'All17 original warning points are above the queried support by2.510244 to3.717134m. The incident original faces include two bottom faces and three adjoining side faces at the broad end; the original minimum is15.275m. This is not a centimetre seam.',
 'Whole-source diagrams show the connected service structure; compound context is partly occluded. The separately labelled partial context omits long and high support faces and cannot prove hidden status or whole-ground clearance.'
 ],interpretation='A ground-level service block adjoining a descending basement ramp is a plausible explanation for the elevated underside. Current evidence does not establish that each flagged surface is intentionally overhead or fully concealed; do not waive the17warnings.',fullAcceptance=False,currentMapAcceptance=False,installationApproved=False,permanentRejection=False,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,nextSteps=['Exact local original podium/ramp face attribution and unoccluded actual renderer views','Complete current-map neighbour/identity/runtime/fallback acceptance before publication'])
 save(DOC/'ROOT-PLAN-CONTEXT.json',review)
 out=module('wave_plan_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'wave-original-service-block-primary-plan-context-v1',[Path(__file__),PRIOR/'result.json',*[ROOT/p for p in pins]],dict(uids=['landsd/301562:0'],fullAcceptance=False,newlyInstalled=0,sourceEvidenceInterpretationUsedAI=True,nextStep=review['nextSteps']))
 print(out['jobId'],flush=True)
if __name__=='__main__':main()

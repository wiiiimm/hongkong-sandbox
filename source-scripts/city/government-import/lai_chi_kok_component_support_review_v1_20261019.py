"""Scoped original embedded-component support interpretation; not publication."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-component-support-review-v1-20261019';DOC=BASE/BATCH
NAMES=['original-component-checks-v1','component-visual-observations-v1','component-identity-review-v1','component-top-conflicts-v2','eight-foundations-v1','eight-render-attributes-v1','eight-runtime-v1','component-wall-paths-v1','wall-support-intersections-v2','rim-contact-paths-v1','rim-contact-replay-v1','contact-rounding-bound-v1']
def main():
 assert not DOC.exists();folders={n:BASE/('government-xl-lai-chi-kok-'+n+'-20261019')for n in NAMES};refs=[Path(__file__)];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in folders.values():
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 sources=read(folders['eight-render-attributes-v1']/'selection.json.gz')['rows'];uids={r['uid']for r in sources[1:]};assert len(uids)==7
 paths=read(folders['rim-contact-paths-v1']/'summary.json')['rows'];assert {r['uid']for r in paths}==uids and sum(r['samples']for r in paths)==132 and all(r['samples']==r['withOriginalPathToSupport']for r in paths)
 replay=read(folders['rim-contact-replay-v1']/'summary.json')['rows'];assert len(replay)==21 and all(r['sharedEdgePathsPreserved']==r['samples']for r in replay)
 bounds=read(folders['contact-rounding-bound-v1']/'summary.json')['rows'];assert len(bounds)==21 and all(r['samples']==r['withinExistingPointOneMetreBand']for r in bounds)
 maximum=max(r['maximumSeparationMetres']for r in bounds);assert maximum<1e-8
 wallpaths=read(folders['component-wall-paths-v1']/'summary.json')['rows'];assert len(wallpaths)==28 and all(r['allSteepSideFaces']and r['allConnectedToOriginalUpwardFaces']for r in wallpaths)
 contacts=read(folders['wall-support-intersections-v2']/'summary.json')['rows'];assert len(contacts)==28 and all(r['affected']==r['withFiniteSupportContact']for r in contacts)
 tops=read(folders['component-top-conflicts-v2']/'summary.json')['rows'];assert {r['uid']for r in tops}==uids and all(r['occludedProjectionAreas']['candidate']==r['occludedProjectionAreas']['platform']==0 for r in tops)
 foundations=read(folders['eight-foundations-v1']/'summary.json')['rows'];componentfound=[r for r in foundations if r['uid']in uids];assert len(componentfound)==28 and all(r['upwardBuried']==0 for r in componentfound)
 observations=read(folders['component-visual-observations-v1']/'observations.json')['rows'];assert len(observations)==7 and all(r['actuallyViewedByCoordinator']for r in observations)
 metrics=read(folders['eight-runtime-v1']/'metrics.json')['rows'];assert len(metrics)==8 and all(r['sourcePreserved']and r['maxSamplerDelta']==0 for r in metrics)
 raw=read(folders['original-component-checks-v1']/'support.json.gz')['rows']
 decision=dict(reviewer='Codex ROOT',uids=sorted(uids),sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in sources},requiredAssemblyUids=[r['uid']for r in sources],sourceSpecificComponentSupportInterpretationAccepted=True,rawStrictInterfacePassed=False,rawSupport=raw,rawComponentFoundationRows=componentfound,originalSampleContactPaths=paths,renderedFiniteContactBounds=bounds,maximumRenderedContactSeparationMetres=maximum,priorInspectedImages=[r['image']for r in observations],observations=[
 'The seven complete originals are raised rectangular, rounded and long edge structures within the original platform assembly, as shown in the previously inspected source views. This review does not assign unverified architectural uses.',
 'All132 canonical failed original low-rim samples are support-above-rim. Their exact source vertex or edge generators have short original shared-edge paths to positive-dimensional finite terrain/platform contacts. The largest path has four faces. This does not claim that each low-rim point itself touches the highest surface.',
 'All35 wholly buried component facets are steep side faces connected by exact source edges to original upward faces, and their recorded paths intersect finite support facets in all four coordinate modes. No component has a wholly buried upward facet. Original upper-surface analysis finds no exposed upward projection buried by candidate terrain or platform above the existing0.5m diagnostic.',
 'The same rim source paths persist in the three renderer coordinate representations. Some exact intersection pairs disappear through arithmetic rounding, but rational barycentric correspondence proves finite paired contact regions remain within the recorded bound; the existing0.1m contact band is unchanged.',
 'Interpret the retained low-rim and side-face burial flags as source-authored embedded lower-wall interfaces in this complete original assembly. This is functional source interpretation, not zero-gap certification or a structural engineering assessment. The original global rim/foundation flags remain in evidence.'
 ],qualification='Valid only for these exact seven sources, platform source, candidate terrain, captured renderer closure and current forms. No geometry edits, source offsets, global threshold changes, new names or standalone publication. Source/context changes invalidate this review.',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,modelGeometryChanges=0,fullAcceptance=False,publicationApproved=False,installationApproved=False,remaining=['main platform source identity and grade interpretation','complete current affected-neighbour and assembly browser acceptance','guarded publication and live verification','commit and push installed models'])
 save(DOC/'ROOT-SUPPORT-REVIEW.json',decision)
 module('component_support_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'seven-original-component-embedded-support-interpretation',list(dict.fromkeys(refs)),dict(uids=sorted(uids),sourceSpecificComponentSupportInterpretationAccepted=True,rawStrictInterfacePassed=False,maximumRenderedContactSeparationMetres=maximum,installationApproved=False,remaining=decision['remaining']))
 print('maximum rendered contact separation',maximum,flush=True)
if __name__=='__main__':main()

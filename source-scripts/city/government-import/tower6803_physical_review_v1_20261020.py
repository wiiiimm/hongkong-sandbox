"""Source-specific original tower/podium interpretation; all raw warnings retained."""
from pathlib import Path
from fractions import Fraction
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tower6803-physical-review-v1-20261020';DOC=BASE/BATCH;UID='landsd/6803:0';POD='landsd/15047:0'
def folder(n):return BASE/('government-xl-tower6803-'+n+'-20261020')
def main():
 assert not DOC.exists();names=['private-terrain-capture-v1','private-terrain-foundations-v1','underside-paths-v1','runtime-paths-v1','finite-path-verification-v1','runtime-finite-verification-v1','feature-clearance-v1','source-feature-context-v2'];pins={};refs=[Path(__file__)]
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for n in names:
   r=read(folder(n)/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);pins[n]={e['path']:e['sha256'] for e in r['evidenceRefs']};refs.append(folder(n)/'result.json')
 def consume(n,file):
  p=folder(n)/file;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 rows=consume('private-terrain-capture-v1','selection.json.gz')['rows'];sources={r['uid']:r['sourceSHA256'] for r in rows};metrics=consume('private-terrain-capture-v1','metrics.json');pod=next(r for r in metrics['rows'] if r['uid']==POD)
 assert pod['minLowGap']>=-.1 and pod['maxLowGap']<=1 and pod['missingTerrain']==0 and pod['maxSamplerDelta']==0
 accounts=[]
 for mode in ['original','literal','explicitLeftF32','explicitBalancedF32']:
  n='underside-paths-v1' if mode=='original' else 'runtime-paths-v1';low=consume(n,mode+'-verified.json.gz')['rows'][0];graph=consume(n,mode+'-graph.json.gz')['rows'][0]
  finite=consume('finite-path-verification-v1' if mode=='original' else 'runtime-finite-verification-v1',mode+'.json')
  feature=consume('feature-clearance-v1',mode+'.json.gz');f=consume('private-terrain-foundations-v1','6803:0-'+mode+'.json');pf=consume('private-terrain-foundations-v1','15047:0-'+mode+'.json')
  assert pf['strictFoundationAccepted'] and not f['strictFoundationAccepted'] and f['foundation']['fullyBuriedTriangles']==6 and f['foundation']['fullyBuriedUpwardTriangles']==1
  assert f['worldSHA256']==feature['sourceWorldSHA256']==low['worldSHA256']==finite['sourceWorldSHA256'] and pf['worldSHA256']==feature['supportWorldSHA256']==finite['supportWorldSHA256']
  assert graph['strictSamples']==572 and graph['failedSamples']==196 and low['boundedPaths']==179 and low['unresolved']==17
  failed={tuple(x['position']) for x in low['details'] if not x['verified']};fixed={tuple(x['target']) for x in finite['rows']};assert failed==fixed and len(fixed)==17
  assert all(x['finitePathVerified'] and x['withinEndpointHeight'] and x['maximumResidualM']<=.001 for x in finite['rows'])
  assert feature['completeEdgeConnectedFeatureFaceIds']==list(range(12516,12532)) and feature['positivePodiumContactCount']==15
  clear=feature['wholeFaceGroundClearances'];assert len(clear)==16 and all(x['proof']['existingOrdinaryClearanceBoundProved'] and Fraction(x['proof']['exactCertifiedLowerClearanceM'])>17 for x in clear)
  accounts.append(dict(mode=mode,sourceWorldSHA256=f['worldSHA256'],supportWorldSHA256=pf['worldSHA256'],drawnGroundSHA256=feature['drawnGroundSHA256'],samples=768,strictContacts=572,finiteEndpointBoundedOriginalPaths=179,additionalFinitePodiumContactPaths=17,unresolved=0,rawBuriedFaces=6,rawBuriedUpwardFaces=1,whole16FaceFeatureGroundClear=True,positiveOriginalPodiumContacts=15,terminalBoundaryContacts=sum(x['terminalContactOnSourceBoundary'] for x in finite['rows']),terminalInteriorContacts=sum(not x['terminalContactOnSourceBoundary'] for x in finite['rows'])))
 images=[]
 for file in ['context-2m.png','context-6m.png']:
  p=folder('source-feature-context-v2')/file;assert digest(p.read_bytes())==pins['source-feature-context-v2'][str(p.relative_to(ROOT))];refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
 review=dict(uids=[UID,POD],sourceSHA256ByUid=sources,sourceSpecificPhysicalInterpretationAccepted=True,rawCanonicalInterfacePassed=False,rawStrictTowerCompoundFoundationPassed=False,rawFailuresPreserved=True,sampleAccounts=accounts,imagesActuallyViewed=images,reviewer='Codex ROOT',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,basis='The six highest-surface flagged facets, including the upward cap, are part of one 16-facet original projecting facade feature. Its whole finite surface is more than17m above all candidate drawn ground facets; exact source-podium intersections exist on seven of its other faces. The higher podium surface therefore does not establish terrain burial. The unchanged authored feature and its intersections are retained, not removed or lowered. Source context shows this small boxed/slab-shaped feature at the lower facade among similar projections; no specific engineering function is asserted. Every original low-rim sample has a strict contact or a verified finite original-face path bounded by its own endpoints. Underside paths remain explicitly original shell connections, not wall-only or structural certification; sixteen additional terminal contacts are on source boundaries and one is an interior crossing. This exact-source interpretation resolves applicability of the highest-surface warning without changing the raw failed foundation result or tolerances. Podium itself has complete strict foundation pass on original-derived private terrain in allfour modes and strict low-rim contact in actual runtime.',scope='Original source physical interpretation only. Identity, full loader, staged/live browser, all terrain runtime guards and guarded publication remain required; no optimisation approval.')
 save(DOC/'ROOT-PHYSICAL-REVIEW.json',review)
 module('tower6803_physical_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-facade-feature-and-podium-source-interpretation',refs,dict(uids=[UID,POD],sourceSpecificPhysicalInterpretationAccepted=True,installationApproved=False))
if __name__=='__main__':main()

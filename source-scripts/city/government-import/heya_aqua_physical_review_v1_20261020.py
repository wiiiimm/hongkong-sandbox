"""Source-specific Heya wall-joint interpretation; publication remains separate."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-heya-aqua-physical-review-v1-20261020';DOC=BASE/BATCH
NAMES=['current-support-v3','render-foundations-v1','render-contacts-v1','wall-adjacency-v1','seam-distance-v1','private-browser-v5','joint-browser-v4']
def folder(n):return BASE/('government-xl-heya-aqua-'+n+'-20261020')
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for n in NAMES:
   p=folder(n)/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 def take(n,name):
  p=folder(n)/name;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 strict=take('current-support-v3','summary.json');assert strict['samples']==142 and strict['strictContacts']==135 and strict['unresolved']==7 and strict['finiteContactWitnesses']==6
 f=take('current-support-v3','foundation.json');assert f['triangles']==f['completeTerrainTriangles']==19777 and f['fullyBuriedTriangles']==0
 render=take('render-foundations-v1','summary.json')['rows'];assert len(render)==3
 for f in render:assert f['triangles']==f['completeTerrainTriangles']==19777 and f['fullyBuriedTriangles']==0
 contacts=take('render-contacts-v1','summary.json')['rows'];assert len(contacts)==3
 for x in contacts:assert x['witnesses']==7 and x['withPositiveIncidentContact']==6 and all(r['lastFaceContacts']for r in x['adjacentRoutes'])
 seam=take('seam-distance-v1','distances.json');remaining=[r for r in seam['rows']if not r['positiveOriginalContactCount']];assert len(remaining)==4 and all(abs(r['distanceM']-.020711322742891107)<1e-12 for r in remaining)
 images=[];reports=[]
 for width in [390,1280]:
  report=take('private-browser-v5',str(width)+'/staged-browser.json');assert report['passed']and not report['errors'];reports.append(report)
  for v in report['views']:
   if 'time'in v:assert v['active']and v['fullyFramed']and v['pick']==v['collision']==v['uid']
  for p in sorted((folder('private-browser-v5')/str(width)).glob('*.png')):
   assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
 assert len(images)==8
 joint=take('joint-browser-v4','1280/staged-browser.json');assert joint['passed']and not joint['errors'];view=joint['localJointViews'][0];hit=view['inspectionAngles'][0];assert hit['firstHitUid']=='landsd/184285:0'and 16<=hit['firstHitDistance']<16.05
 p=folder('joint-browser-v4')/'1280'/view['file'];assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
 sources=take('current-support-v3','support-inputs.json')['sources']
 review=dict(reviewer='Codex ROOT',uids=[r['uid']for r in sources],sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in sources},localWallInterpretationAccepted=True,rawStrictInterfacePassed=False,rawStrictFailuresRetained=True,strictSummary=strict,rendererContactAccounts=contacts,imagesActuallyViewed=images,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,installationApproved=False,publication=False,remainingGates=['Current complete neighbour/source applicability review','Qualified guarded publication plan','Live installation verification and Neon installed receipt'],basis=[
 'The 142-sample vertical support test retains its seven raw failures. Six have exact positive-dimensional contacts on incident original faces in source and all captured renderer representations. This does not relabel them as strict vertical contacts.',
 'The seventh sample is on original near-vertical wall face17083. Exact nonzero shared edges connect17083 to17084 to17085, whose finite original podium contact remains positive in literal and both Float32 modes. The small seam is part of the continuous authored wall shell, not a separately floating building or an identity mismatch. No per-facet engineering-support requirement is introduced.',
 'Nearest podium surface at the seventh original witness is0.020711322742891107m in allfour representations. The scene-selected ray reaches that original podium wall0.044004713267547m beyond the witness along an oblique ray. This is evidence of a backing wall beside this local facade seam, not a global permitted-gap tolerance.',
 'ROOT inspected all8fulltower/podium exports and the scene-selected local export. Desktop podium views show the tower body meeting the podium wall bands; no broad floating tower or buried body is apparent. The local image shows solid wall with authored openings/edge lines, with exact ray evidence locating the witness. Night original geometry stays dark with procedural windows disabled. Mobile tower is visible; mobile podium own views are obstructed by an adjacent BASIC building, so they do not independently prove the joint appearance. Desktop and local views supply that context.',
 'Every one of19777towerfaces has complete compoundfoundation coverage and zero whollyburiedfaces in source/literal/leftF32/balancedF32. Acceptance here is limited to interpretation of this exact authored wall joint; original strict diagnostics remainfalse and no runtime geometry, pose, tolerance or terrain is changed.' ])
 save(DOC/'review.json',review)
 for p in refs:
  key=str(p.relative_to(ROOT))
  if key in pins:assert digest(p.read_bytes())==pins[key]
 module('heya_physical_review_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'root-source-specific-local-wall-joint-interpretation',refs,review)
if __name__=='__main__':main()

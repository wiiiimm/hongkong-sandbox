"""Bounded ROOT interpretation of four original tower/podium interfaces."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympian-two-original-interface-review-v1-20261018';DOC=BASE/BATCH
NAMES=['government-xl-olympian-two-four-world-path-bounds-v1-20261018','government-xl-olympian-two-assembly-views-v1-20261018','government-xl-olympian-two-primary-architect-v1-20261018']
TOWERS=['landsd/270317:0','landsd/269908:0','landsd/269839:0','landsd/269837:0']
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in NAMES:
   p=BASE/name/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 bounds=read(BASE/NAMES[0]/'bounds.json.gz')['rows'];contacts=read(BASE/NAMES[0]/'contacts.json.gz')['rows'];assert len(contacts)==7812 and all(x['contactPassed']for x in contacts);assert len(bounds)==16 and all(x['maximumFaceDistanceBoundM']<=.001 for x in bounds)
 foundation=read(BASE/'government-xl-olympian-two-four-world-foundations-v1-20261018/summary.json');assert foundation['allModesPassed']and len(foundation['rows'])==16 and all(x['covered']==x['faces']and x['buried']==x['upwardBuried']==0 for x in foundation['rows'])
 interfaces=read(BASE/'government-xl-olympian-two-four-world-interfaces-v1-20261018/interfaces.json.gz')['rows'];assert len(interfaces)==16 and all(x['proof']['strictContacts']>0 for x in interfaces)
 selection=read(BASE/'government-xl-olympian-two-current-identity-runtime-v1-20261018/selection.json.gz')['rows'];worlds=read(BASE/'government-xl-olympian-two-six-original-four-world-v1-20261018/summary.json');sources=[dict(uid=r['uid'],sourceSHA256=r['sourceSHA256'],sourceForm=r['source'],modelId=r['modelId'],worldHashes=worlds[r['uid']]['hashes'])for r in selection]
 images=[BASE/NAMES[1]/(u.replace('/','-').replace(':','-')+'.png')for u in TOWERS]+[BASE/NAMES[2]/'810_180501-web-project-page2.jpg'];assert all(str(p.relative_to(ROOT))in pins for p in images)
 review=dict(uids=TOWERS,sourceSpecificInterfaceInterpretationAccepted=True,reviewer='Codex ROOT',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,fullAcceptance=False,installationApproved=False,publicationApproved=False,rawStrictWarningsPreserved=True,sourceBindings=sources,inspectedImages=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in images],basis=[
 'ROOT inspected all four original lower-tower/podium plan and oblique views. Towers2/3/5 have projecting lower facade wings around recessed areas; vertical rays from those edges do not represent the whole tower support. Tower1 lower slivers lie in the same authored lower interface. No replacement support or coordinate fitting is introduced.',
 'The architect photograph supplies qualitative context of elevated residential facades, recessed bases and a landscaped podium. It is not surveyed registration or an exact tower-number identity proof.',
 'All1953 retained canonical failures have complete lower-original-surface paths to contact points on the original podium assembly.7812 endpoint checks retain the original maximum-surface contact interval in four captured worlds. Complete finite-face path membership is bounded below the existing .001m tolerance;21 small original seams remain unchanged, maximum bound below.000008m. Paths do not route through upper-storey or roof geometry.',
 'Each tower retains positive strict contacts in every mode. All21402 tower faces are covered in complete compound-foundation checks in each mode, with zero fully buried or upward buried faces. These checks and visible original lower-source geometry support interpreting the ray failures as authored overhang/recessed interface geometry, not a freely translated or unsupported whole tower.',
 'This is a bounded source-specific architectural interpretation, not automatic acceptance of every connected mesh or a new generic support rule. It does not assert engineering adequacy, exact source welding, global watertightness, or universal GPU precision. Raw warnings and source paths remain available.'],remaining=['Three source identity exception reviews','Current-parent podium terrain repair and complete affected-neighbour regression','Current staged/live desktop/mobile rendering, picking, collision and fallback','Guarded installation and verified Neon installed record'])
 save(DOC/'ROOT-INTERFACE-REVIEW.json',review);refs.extend(ROOT/p for p in pins)
 out=module('olympian_interface_review_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'four-olympian-original-tower-interface-source-review-v1',list(set(refs)),dict(uids=TOWERS,sourceSpecificInterfaceInterpretationAccepted=True,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()

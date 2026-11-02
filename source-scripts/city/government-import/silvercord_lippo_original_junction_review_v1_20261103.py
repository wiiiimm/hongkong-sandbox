"""Record bounded original junction interpretation; no whole physical/publication approval."""
import sys,uuid
from fractions import Fraction as F
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v2_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-silvercord-lippo-original-junction-review-v1-20261103';LOCAL=HERE/'local'/BATCH
UIDS=['landsd/233997:0','landsd/231645:0'];SOURCES={'landsd/233997:0':'11b03482304ea9f139e6863d259891f06aecc5def1df2e18abd921e0a0aebc5d','landsd/231645:0':'cfe390f024ac815a8c8ae3f422724fd72e4cd5c164e7325f9404cd81fc1b46da'}
CONTACT='government-xl-silvercord-lippo-original-contacts-v1-20261101';CONTEXT='government-xl-silvercord-lippo-exact-contact-representation-v1-20261103';PLANES='government-xl-silvercord-lippo-original-area-plane-context-v1-20261103';VIEWS='government-xl-silvercord-lippo-complete-source-views-v1-20261101';JUNCTION='government-xl-silvercord-lippo-original-contact-views-v1-20261101'
def owned():
    lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);refs=[Path(__file__)];pins={}
    def take(batch,name,structured=True):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        p=BASE/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)if structured else dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
    contacts=take(CONTACT,'summary.json');context=take(CONTEXT,'summary.json');planes=take(PLANES,'summary.json');junction=take(JUNCTION,'summary.json')
    for s in [contacts,context,planes]:assert s['uids']==UIDS and s['sourceSHA256ByUid']==SOURCES
    bounds=junction['exports'][0]['displayBounds'];bounded=[]
    for i,mode in enumerate(['original','literal','leftF32','balancedF32']):
        raw=take(CONTACT,mode+'.json.gz');assert raw['allPairsExamined']and raw['sourceFacesOmitted']==0
        assert len(raw['contacts'])==[248,213,1326,1326][i]
        lo=[min(F(p[a])for c in raw['contacts']for p in c['exactPoints'])for a in range(3)]
        hi=[max(F(p[a])for c in raw['contacts']for p in c['exactPoints'])for a in range(3)]
        assert all(F(float(bounds[0][a]))<=lo[a]<=hi[a]<=F(float(bounds[1][a]))for a in range(3))
        proof=take(CONTEXT,mode+'.json.gz')['summary'];assert proof['allSavedContactsExamined']and proof['allVerticesExactlyOnBothRepresentedFaces']and proof['allAffineDisplacementsWithinExactVertexBounds']
        assert proof['maximumMappedDisplacementM'][0]==proof['maximumMappedDisplacementM'][2]==0
        assert F(proof['maximumMappedDisplacementExact'][1])==[F(0),F(13,1125899906842624),F(1,2097152),F(1,2097152)][i]
        p=planes['rows'][i];assert p['areaContactPairs']==[0,0,269,269][i]
        if i>=2:assert p['originalPlaneRelations']=={'parallel-separated':268,'non-parallel':1}and p['originalContactDimensions']=={'None':268,'0':1}and p['bothOriginalTrianglesStraddleOtherPlane']==0
        bounded.append(dict(mode=mode,contactBoundsExact=[[str(v)for v in lo],[str(v)for v in hi]],allContactsInsideActuallyInspectedOriginalJunctionContext=True,rawContacts=take(CONTACT,mode+'.json.gz',False)))
    images=[take(VIEWS,'233997-0-oblique-35.png',False),take(VIEWS,'231645-0-oblique-35.png',False),take(JUNCTION,'231645-0-junction.png',False)]
    review=dict(reviewer='ROOT',uids=UIDS,sourceSHA256ByUid=SOURCES,allListedExportsActuallyInspected=True,images=images,exactSourcePairJunctionInterpretationReviewed=True,scope='unchanged-original-podium-pair-authored-wall-and-roof-boundary-context-only',boundedContactEvidence=bounded,originalSourcePointLineContacts=248,originalAreaContacts=0,float32AreaContacts=269,sourceGeometryChanges=0,sourcePoseChanges=0,sourceFacesOmitted=0,identityApprovalTransferred=False,physicalAcceptance=False,supportAcceptance=False,collisionExemption=False,currentSceneRevalidated=False,terrainAccepted=False,runtimeAccepted=False,visualAcceptance=False,installationApproved=False,publication=False,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,interpretation='ROOT inspected both complete original podium obliques and the original pair junction from both displayed directions. The saved original contacts occupy their adjoining exterior wall and roof-edge junction. All four represented contact sets lie inside that exact displayed original-source junction context. Of269 Float32 area pairs,268 are distinct parallel horizontal planes in the unchanged originals and one pair has only an original point contact; none has both original triangles straddling the other plane. Exact affine checks bound every contact vertex to its corresponding unchanged original face with zero horizontal change and at most1/2097152metre vertical representation change. Treat the increase in area-contact count as representation context for this exact authored junction, not evidence that source geometry requires remodelling. Preserve every original point/line contact and all269 represented area pairs. This source-only interpretation grants no collision exemption or whole physical clearance and cannot skip current terrain, support, foreign actor, runtime, identity-revalidation or guarded publication checks.')
    save(BASE/BATCH/'ROOT-JUNCTION-REVIEW.json',review);summary={k:v for k,v in review.items()if k not in ['images','boundedContactEvidence','interpretation']};summary['review']=dict(path=str((BASE/BATCH/'ROOT-JUNCTION-REVIEW.json').relative_to(ROOT)),sha256=digest((BASE/BATCH/'ROOT-JUNCTION-REVIEW.json').read_bytes()));save(BASE/BATCH/'summary.json',summary);assert reservations.owns(lease)
    module('silvercord_junction_context_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-exact-original-pair-junction-interpretation',list(dict.fromkeys(refs)),summary)
if __name__=='__main__':
    if '--owned'in sys.argv:owned()
    else:
        assert not LOCAL.exists()and not(BASE/BATCH).exists();c=reservations.claim('silvercord-lippo-junction-review-'+str(uuid.uuid4()),['building:'+u for u in UIDS]+['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert c['ok'],'Source reservation unavailable';execute_reserved(c['reservation'],LOCAL/'reservation.json',[sys.executable,__file__,'--owned'])

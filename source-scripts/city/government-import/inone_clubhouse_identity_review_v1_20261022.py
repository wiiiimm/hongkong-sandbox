"""Scoped clubhouse identity interpretation; no placement or publication approval."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-inone-clubhouse-identity-review-v1-20261022'
def main():
 doc=BASE/BATCH;assert not doc.exists();refs=[Path(__file__)]
 def take(batch,name):
  folder=BASE/batch;_,pins=authenticate(folder);p=folder/name;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.extend([folder/'result.json',p]);return p
 b='government-xl-inone-adjoining-identity-v2-20261022';identity=read(take(b,'277974:0/identity.json'));context=read(take(b,'277974:0/context.json'))['identity']
 assert identity['exactCurrentComponentRoute']['qualified']and identity['exactWholeCellCoverage']['covered']
 assert set(identity['reasons'])=={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}
 assert context['exactObjectAndCSUID']and context['targetCoveredBySourceProjection']>.998
 other=[f for f in context['intersectingForms']if f['uid']!='landsd/277974:0'];assert len(other)==1 and other[0]['uid']=='landsd/277973:0'and other[0]['structureType']=='Podium'
 assert abs(other[0]['intersectionAreaM2']-context['sourceProjectionAreaM2'])<1e-8
 rows=read(take(b,'selection.json.gz'))['rows'];row=next(r for r in rows if r['uid']=='landsd/277974:0');asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']=='c228a786763b304643263f101169c559c89d9707cfd7bc06c028c3073244e693';refs.append(asset)
 tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256'];refs.append(tile)
 image=take('government-xl-inone-clubhouse-extent-context-v1-20261022','277974-0.png')
 layout=HERE/'local/government-xl-inone-primary-plan-20261022/page-32.png';pdf=layout.parent/'official-brochure.pdf';assert digest(pdf.read_bytes())=='49b3e39cb85eb9399d5ff9246e765b1fa4e053a718f4d7b8e7cbb87697712ecd';refs.extend([layout,pdf])
 review=dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],sourceFormTileSHA256=row['source']['tileSHA256'],reviewer='Codex ROOT',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,imagesActuallyViewed=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in [image,layout]],identityAccepted=True,sourceSpecificIdentityReviewAccepted=True,automaticIdentityCheckPassed=False,rawIdentityReasons=identity['reasons'],rawSpatialContext=context,observations=[
 'Exact government object, CSUID and tower-type routing identifies the original clubhouse. The complete source geographic cell is covered.',
 'The inspected source projection follows the same distinctive bent clubhouse footprint. Maximum outward extension is 0.770751881693801 metres; 99.83185320803665 percent of the recorded target footprint is covered. These are measured facts for this revision, not new global thresholds.',
 'The only other intersecting form is the enclosing podium277973, whose footprint contains the entire original clubhouse projection. The 68.066049111274 square metre excess is a narrow perimeter difference, not another tower or displaced independent building.',
 'Official layout page31 places the clubhouse at the corresponding development boundary within the podium complex. This supplies qualitative architectural context, not precise registration, engineering support or a collision guarantee.'
 ],decision='Accept identity of this exact original clubhouse revision. Retain both raw footprint-overlap flags; do not alter automatic guards. This decision does not approve either podium or establish support.',remainingRequirements=['Complete original clubhouse support and foundation checks','Independent identity and physical acceptance of any required podium','Staged/live runtime and guarded publication checks'],installationApproved=False,publicationApproved=False,sourceGeometryChanges=0)
 save(doc/'ROOT-IDENTITY-REVIEW.json',review)
 module('clubhouse_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'qualified-original-clubhouse-source-identity',refs,review)
if __name__=='__main__':main()

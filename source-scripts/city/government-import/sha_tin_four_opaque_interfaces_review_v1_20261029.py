"""ROOT's bounded source-junction review; no source edits or publication."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-sha-tin-'
BATCH=PREFIX+'four-opaque-interface-role-reviews-v1-20261029'


def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:
            pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        p=BASE/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    contacts=take(PREFIX+'civic-seven-foreign-contacts-v1-20261029','summary.json')
    basics=take(PREFIX+'civic-seven-foreign-contacts-v1-20261029','basic.json')
    for path,sha in basics['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    selection=take(PREFIX+'seven-upward-floor-runtime-v1-20261029','selection.json.gz')
    shapes={r['uid']:r for r in basics['rows']};rows=[]
    pairs=[(271344,235892,'Authored roof/wall/rounded-end junction at the retained shopping-podium edge; the former BASIC proxy also met this podium. Preserve the complete original source and the retained opaque BASIC body.'),(271344,236080,'Authored narrow wall/edge junction alongside the retained podium wall. The detailed source replaces the broad proxy side with finer wall returns; keep that original arrangement and the retained body.'),(238142,24712,'Source-authored lower roof/wall return meets the retained taller opaque building wall. This source detail was absent from the simpler proxy in the focused window; it is not evidence that the immutable source must be clipped.'),(92881,257099,'Authored stepped wall/ledge return joins the retained station-podium side. Preserve the original ledges and wall outline together with the current opaque neighbouring body.')]
    for sid,fid,basis in pairs:
        uid='landsd/'+str(sid)+':0';foreign='landsd/'+str(fid)+':0';batch=PREFIX+'seven-interface-'+str(sid)+'-'+str(fid)+'-focused-v1-20261029'
        diagram=take(batch,'summary.json');image=BASE/batch/'before-after-contact-context.png';assert digest(image.read_bytes())==pins[batch][str(image.relative_to(ROOT))];refs.append(image)
        source=next(r for r in selection['rows']if r['uid']==uid);assert source['sourceSHA256']==diagram['sourceSHA256']
        asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256'];refs.append(asset)
        form=shapes[foreign]['currentBuilding'];tile=ROOT/'3d-viewer/city/data/tiles'/(form['tile']+'.json');assert next(b for b in read(tile)['buildings']if b['uid']==foreign)==form;refs.append(tile)
        raw=next(r for r in contacts['rows']if r['uid']==uid and r['foreignUid']==foreign);modes={r['mode']:r for r in raw['modes']};assert {'original','literal','leftF32','balancedF32'}<=set(modes)and all(modes[m]['positiveContactPairs']>0 for m in ['original','literal','leftF32','balancedF32'])
        rows.append(dict(uid=uid,foreignUid=foreign,sourceSHA256=source['sourceSHA256'],currentRetainedForm=form,rawFiniteContactSummary=raw,focusedDiagram=str(image.relative_to(ROOT)),focusedDiagramActuallyInspected=True,boundedOpaqueJunctionRoleApproved=True,decision='retain-original-and-current-neighbour',basis=basis,sourceGeometryChanges=0,retainedGeometryChanges=0,suppressionApproved=False,physicalRootOrSupportCredit=False,reverseSolidContainmentCertification=False,rawContactFlagsPreserved=True))
    result=dict(uids=contacts['uids'],reviewer='ROOT',rows=rows,sourceSpecificOpaqueInterfaceRolesApproved=True,evidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,wholeGroupAcceptance=False,installationApproved=False,publication=False,qualification='Exact four source/retained-BASIC junctions reviewed from all four focused before/after diagrams actually opened by ROOT, complete finite-contact summaries and current immutable source/form bindings. This approves retaining these authored opaque junctions for the viewer. It asserts neither cadastral ownership nor engineering support, universal closed-solid clearance, whole-group source placement or publication. Diagram clipping is display-only; raw contact/overlap records remain verbatim and all original government geometry remains unchanged.')
    save(out/'ROOT-OPAQUE-INTERFACE-REVIEWS.json',result)
    module('sha_tin_four_interfaces_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-source-original-and-retained-basic-opaque-junction-role-review',list(dict.fromkeys(refs)),result)


if __name__=='__main__':main()

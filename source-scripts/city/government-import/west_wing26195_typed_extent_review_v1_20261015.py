"""Exact 211-face architectural extent interpretation; other identity failures retained."""
from copy import deepcopy
from pathlib import Path
import hashlib,json
import numpy as np
from shapely.geometry import Polygon
import shapely
from run import ROOT,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';CAP=BASE/'government-xl-west-wing26195-complete-current-runtime-capture-v2-20261012'
DOC=BASE/'government-xl-west-wing26195-typed-extent-review-v1-20261015'
SOURCE='50da67a3a009c3c832d2bfdbd08640c89d958ef8cf077d1c172e7059900f8af9';WORLD='32969c0eb6a4ea9d4fbfab447ad4e374809399b88ecf82fd52534a1d2d1c712b';UID='landsd/26195:0'
EXTENT={'full-source-maximum-extent','fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM'}
def compose(raw,tri,form,context,interpretation):
 tri=np.asarray(tri,dtype='<f8');assert tri.shape==(46918,3,3)and np.isfinite(tri).all();assert digest(tri.tobytes())==WORLD==raw['worldTrianglesSHA256']
 assert raw['uid']==UID and raw['sourceSHA256']==SOURCE and form['uid']==UID
 assert form['objectId']==26195 and form['buildingCSUID']=='3511615681P20110704' and form['structureType']=='Podium'
 assert raw['originalOwnership']['sourceGraphVerified'] and raw['exactWholeCellCoverage']['covered'] and raw['exactWholeCellCoverage']['wholeOriginalFacesAccounted']==46918 and raw['geographicCell']['targetCoversWholeCell'] and raw['freshCurrentIdentity']['exactObjectAndCSUID']
 p=Polygon(form['rings'][0],form['rings'][1:]);d=np.asarray(shapely.distance(shapely.points(tri[:,:,[0,2]].reshape(-1,2)),p)).reshape(-1,3);far=np.flatnonzero(d.max(axis=1)>10).tolist()
 assert far==context['completeOver10mFaceIds']and len(far)==211
 low=[i for i in far if tri[i,:,2].max()<700];high=[i for i in far if tri[i,:,2].min()>780]
 assert len(low)==160 and len(high)==51 and sorted(low+high)==far
 assert interpretation['uid']==UID and interpretation['sourceSHA256']==SOURCE and interpretation['worldSHA256']==WORLD
 assert interpretation['extentScopeReviewed']is True and interpretation['geometryChanges']==0
 assert interpretation['groups'][0]['sourceFaceIds']==low and interpretation['groups'][1]['sourceFaceIds']==high
 assert interpretation['scope']=='identity-extent-only' and interpretation['physicalExemption']is False
 out=deepcopy(raw);out.update(rawIdentityRetained=deepcopy(raw),policy='west-wing-exact211-original-approach-connector-extent-v1',sourceInterpretation=deepcopy(interpretation),rawExtentMaximumM=float(d.max()),ordinaryExtentFaceCount=46918-211,completeFaceAccounting=True,sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False,currentAcceptance=False,qualification='Exact original 160 curved approach facets and 51 elevated connector facets are source-authored site structures consistent with the retained architect plan. Only the two extent reason keys are accounted for. Raw target coverage, unrelated overlap, every physical check and all original faces remain unchanged.')
 out['reasons']=[x for x in raw['reasons']if x not in EXTENT];out['narrowlyAccountedReasonKeys']=sorted(set(raw['reasons'])&EXTENT);out['passed']=not out['reasons'];out['proof']={k:False for k in raw['proof']}
 return out

def main():
 assert not DOC.exists();rawpath=BASE/'government-xl-west-wing26195-current-unchanged-raw-owned-identity-v1-20261012/identities.json';contextpath=BASE/'government-xl-west-wing26195-extent-face-context-v1-20261015/context.json'
 raw=read(rawpath)['rawFullCellIdentity'];tri=np.asarray(read(CAP/'original-full-source-root-context.json.gz')['completeOriginalBinary64WorldTriangles']);forms=read(CAP/'literal-source-inputs.json.gz')['completeCurrentForms'];form=next(f for f in forms if f['uid']==UID);context=read(contextpath)
 far=context['completeOver10mFaceIds'];low=[i for i in far if tri[i,:,2].max()<700];high=[i for i in far if tri[i,:,2].min()>780]
 interpretation=dict(uid=UID,sourceSHA256=SOURCE,worldSHA256=WORLD,reviewer='Codex ROOT',scope='identity-extent-only',extentScopeReviewed=True,geometryChanges=0,physicalExemption=False,usesAISourceInterpretation=True,aiGeometryModelling=False,groups=[dict(role='curved low approach at the landscaped podium edge',sourceFaceIds=low),dict(role='elevated eastern connecting structure',sourceFaceIds=high)],basis='Actual original extent-context image, complete original paired-neighbour image and architect-supplied site plan inspected. Two spatially separated features correspond to curved approach and cross-link features in the complex design. This is source architectural scope, not surveyed raster registration, legal ownership, structural certification or a collision exception.')
 out=compose(raw,tri,form,context,interpretation);assert not out['passed']and len(out['reasons'])==4
 # Adverse bindings must reject; independent failures must survive intact.
 checks=[]
 for name,mutation in [('source-hash',lambda r,i:r.update(sourceSHA256='bad')),('world-binding',lambda r,i:r.update(worldTrianglesSHA256='bad')),('face-omission',lambda r,i:i['groups'][0]['sourceFaceIds'].pop()),('physical-exemption',lambda r,i:i.update(physicalExemption=True)),('scope-change',lambda r,i:i.update(scope='all-identity'))]:
  rr=deepcopy(raw);ii=deepcopy(interpretation);mutation(rr,ii)
  try:compose(rr,tri,form,context,ii)
  except AssertionError:checks.append(dict(case=name,rejected=True))
  else:raise AssertionError(name)
 rr=deepcopy(raw);rr['reasons'].append('independent-failure');assert 'independent-failure'in compose(rr,tri,form,context,interpretation)['reasons'];checks.append(dict(case='independent-failure',retained=True))
 paths=[Path(__file__),rawpath,contextpath,CAP/'original-full-source-root-context.json.gz',CAP/'literal-source-inputs.json.gz',BASE/'government-xl-west-wing26195-extent-face-context-v1-20261015/extent-context.png',BASE/'government-xl-west-wing26195-neighbour319534-original-context-v1-20261015/two-original-context.png',BASE/'government-xl-west-wing26195-architect-site-plan-v1-20261015/site-plan.jpg',BASE/'government-xl-west-wing26195-architect-site-plan-v1-20261015/provenance.json']
 refs=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in paths]
 save(DOC/'interpretation.json',interpretation);save(DOC/'identity-extent-only.json',out);save(DOC/'checks.json',dict(checks=checks,positiveExtentReasonKeys=out['narrowlyAccountedReasonKeys'],retainedReasons=out['reasons'],inputRefs=refs,sourceOnly=True,newlyInstalled=0,currentIdentityReplayStillRequired=True));print(json.dumps(dict(extentFaces=211,retainedReasons=out['reasons'],checks=len(checks))))
if __name__=='__main__':main()

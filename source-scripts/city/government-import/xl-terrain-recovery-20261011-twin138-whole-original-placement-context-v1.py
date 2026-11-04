"""Images-only complete source placement of every remaining Twin body.

No distance search, mounting predicate, inferred function or acceptance. Every
highlighted part is complete; grey surrounding source faces are display only.
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
import twin155_complete_boundary_actual_fixture_v1_20261011 as fixture
import twin155_named_complete_boundary_visual_assembly_proposal_v1_20261011 as k

BATCH='xl-terrain-recovery-20261011-twin138-whole-original-placement-context-v1'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def draw(ax,part,near,lo,hi,body,azimuth):
 origin=(lo+hi)/2
 ax.add_collection3d(Poly3DCollection((near-origin)[:,:,[0,2,1]],facecolors=(.40,.53,.65,.22),edgecolors=(.3,.4,.5,.17),linewidths=.15))
 ax.add_collection3d(Poly3DCollection((part-origin)[:,:,[0,2,1]],facecolors='#ed4b26',edgecolors='#592818',linewidths=.65))
 a=(lo-origin)[[0,2,1]];b=(hi-origin)[[0,2,1]]
 ax.set_xlim(a[0],b[0]);ax.set_ylim(a[1],b[1]);ax.set_zlim(a[2],b[2]);ax.set_box_aspect(b-a);ax.view_init(elev=22,azim=azimuth);ax.set_axis_off()
 ax.set_title(str(body)+' / '+str(len(part))+' complete facets',fontsize=12)
def main():
 assert not DOC.exists()
 docs,packages,refs,receipts=fixture.actual_fixture()
 worlds=next(iter(packages.values()))['worlds'];w=worlds['providerOriginal']
 ids=sorted(set(a['originalBody']for a in docs['bands']['rows'][0]['all293OriginalBodyAssociations'])-set(k.NAMED_SOURCE_PART_FACES));assert len(ids)==138
 common=set.intersection(*[set(r['qualifiedDiagnosticBodyIDs'])for r in docs['paths']['rows']]);assert len(common)==827 and not common.intersection(ids)
 refs += [ref(Path(__file__)),ref(HERE/'twin155_complete_boundary_actual_fixture_v1_20261011.py'),ref(HERE/'twin155_named_complete_boundary_visual_assembly_proposal_v1_20261011.py')]
 for r in receipts.values():
  for q in r['evidenceRefs']:assert ref(ROOT/q['path'])==q;refs.append(q)
 DOC.mkdir(parents=True);records=[]
 for body in ids:
  item=docs['graph']['bodies'][body];uid=item['actorUID'];faces=item['globalOriginalFaces'];part=w[faces];offset,total=(0,13063)if uid=='landsd/222465:0'else(13063,456);own=w[offset:offset+total]
  lo=part.min((0,1));hi=part.max((0,1));margin=np.maximum((hi-lo)*.6,[8.,5.,8.]);surround=[offset+int(i)for i in np.flatnonzero(np.all(own.max(1)>=lo-margin,axis=1)&np.all(own.min(1)<=hi+margin,axis=1))]
  finite=[];negative=[];hostfaces={}
  for mode in k.MODES:
   f=next(r for r in docs['finite']['rows']if r['mode']==mode and r['uid']==uid);p=next(r for r in docs['paths']['rows']if r['mode']==mode);band=next(r for r in docs['bands']['rows']if r['mode']==mode);a=next(a for a in band['all293OriginalBodyAssociations']if a['originalBody']==body)
   assert k.world_sha(worlds[mode][offset:offset+total])==f['completeWorldSHA256']
   findings=[]
   for face in faces:
    ctx=f['completeAllOriginalFacetContexts'][face-offset];proof=f['allFaces'][face-offset]
    assert ctx['sourceFace']==proof['sourceFace']==face-offset and ctx['sourceFaceSHA256']==k.world_sha(worlds[mode][face])
    findings.append(dict(globalOriginalFace=face,completeFiniteProofVerbatim=proof,completeFacetContextVerbatim=ctx))
   hs=sorted(z for i in common if docs['graph']['bodies'][i]['actorUID']==uid for g in p['completeActualCensusForEveryOriginalBody'][i]['completeActualEdgeCensus']['sharedEdgeConnectedComponents']for z in g)
   hostfaces[mode]=hs
   finite.append(dict(mode=mode,completeActorWorldSHA256=f['completeWorldSHA256'],completeActualDrawnGroundSHA256=f['completeActualDrawnGroundSHA256'],completePartFiniteFindings=findings,completePartActualEdgeCensus=a['completeActualEdgeCensus']))
   negative.append(dict(mode=mode,allAssociationAndMountingFindingsVerbatim=a))
  records.append(dict(originalBody=body,actorUID=uid,sourceSHA256=k.SOURCE_SHA[uid],completeOriginalFaces=faces,completeOriginalPartWorldSHA256=k.world_sha(part),completeOriginalBounds=dict(min=lo.tolist(),max=hi.tolist()),completeActorContextOriginalFaces=list(range(offset,offset+total)),completeWideContextOriginalFaces=surround,wideContextBounds=dict(min=(lo-margin).tolist(),max=(hi+margin).tolist()),allFourStreamCompleteFiniteFindings=finite,allPriorMountingAndFreeEdgeNegativesVerbatim=negative,completeQualifiedNonvisualFacesByMode=hostfaces,greyContextDoesNotQualifyVisualHosts=True,sourceFunctionInferred=False,visualRoleAccepted=False,structuralRootOrBridgeCredit=False))
 assert sum(len(r['completeOriginalFaces'])for r in records)==1521
 for page,start in enumerate(range(0,len(records),12),1):
  group=records[start:start+12]
  for azimuth,label in [(-58,'south-east'),(118,'north-west')]:
   fig=plt.figure(figsize=(28,21),dpi=100)
   for j,r in enumerate(group):
    lo=np.array(r['wideContextBounds']['min']);hi=np.array(r['wideContextBounds']['max'])
    draw(fig.add_subplot(3,4,j+1,projection='3d'),w[r['completeOriginalFaces']],w[r['completeWideContextOriginalFaces']],lo,hi,r['originalBody'],azimuth)
   fig.suptitle('Twin Regency remaining138 — complete orange source parts / exhaustive same-actor wide source context\nPage '+str(page)+'; no inferred function, mounting, structural/root/bridge or accepted role',fontsize=19)
   fig.subplots_adjust(left=.01,right=.99,bottom=.025,top=.93,wspace=.03,hspace=.08)
   image=DOC/('page-'+str(page).zfill(2)+'-'+label+'-2800x2100.png');fig.savefig(image);plt.close(fig)
   for r in group:r.setdefault('contextImages',[]).append(ref(image))
   print(dict(page=page,view=label,bodies=[r['originalBody']for r in group]),flush=True)
 assert all(ref(ROOT/r['path'])==r for r in refs)
 save(DOC/'diagnostic.json.gz',dict(complete138OriginalImageContexts=records,completeOriginalWorldSHA256=k.world_sha(w),completeFourWorldSHA256={m:k.world_sha(worlds[m])for m in k.MODES},uids=['landsd/222465:0','landsd/223206:0'],sourceOnly=True,noNewDistanceSearch=True,noFreshCurrentCapture=True,sourceGeometryChanges=0,visualRoleAccepted=False,currentAcceptance=False,structuralRootOrBridgeCredit=False,nativeReacceptance=False,newlyInstalled=0,evidenceRefs=list({(r['path'],r['sha256']):r for r in refs}.values())))
 print(dict(completeParts=138,completeFacets=1521,output=str(DOC.relative_to(ROOT))),flush=True)
if __name__=='__main__':main()

"""Original source images only; reuse frozen finite findings, no new distances."""
from pathlib import Path
import importlib.util,sys,time,uuid
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect,reservations
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-elements11-whole-original-building-placement-context-v2';DOC=BASE/BATCH
PARTS=(69,75,76,78,705,744,839,893,897,902,921)
INPUTS=('elements-complete-owned-original-contact-graph-v1','elements132-four-stream-qualified-host-association-v1','elements-owned-four-stream-complete-finite-v1','elements-sun-star-two-current-render-attribute-capture-v1','elements-bounded-owned-four-stream-path-replay-v1','elements15-intrinsic-sheet-backing-and-roof-correspondence-v1','elements4-named-complete-perimeter-visual-sheet-proposals-v1')
HELPERS=('test_elements24_named_original_mounted_visual_surface_proposal_v1_20261011.py','elements24_named_original_mounted_visual_surface_proposal_v1_20261011.py','exact_packed_world_geometry_20261009.py','xl-popcorn-source-investigations-checkpoints-20261009.py')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def plot(ax,part,context,lo,hi,title,elev,azim):
 ax.add_collection3d(Poly3DCollection(context[:,:,[0,2,1]],facecolors='#aebac6',edgecolors='#71808c',linewidths=.16,alpha=.2))
 ax.add_collection3d(Poly3DCollection(part[:,:,[0,2,1]],facecolors='#df4435',edgecolors='#741b15',linewidths=1.,alpha=1))
 for axis,a,b in [('x',lo[0],hi[0]),('y',lo[2],hi[2]),('z',lo[1],hi[1])]:getattr(ax,'set_'+axis+'lim')(a,b)
 ax.set_box_aspect((hi-lo)[[0,2,1]]);ax.view_init(elev=elev,azim=azim);ax.set_axis_off();ax.set_title(title,fontsize=10)
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]+[ref(HERE/n)for n in HELPERS]
 for stem in INPUTS:
  folder=BASE/('xl-terrain-recovery-20261011-'+stem);r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(ref(folder/'result.json'))
  for q in r['evidenceRefs']:
   p=ROOT/q['path'];assert p.is_file()and ref(p)==q;refs.append(q)
 refs=list({(q['path'],q['sha256']):q for q in refs}.values())
 fixture=load('elements11_image_source_fixture',HERE/HELPERS[0]);docs,packages=fixture.actual_fixture();worlds=next(iter(packages.values()))['worlds'];w=worlds['providerOriginal'];graph=docs['graph']
 paths=read(BASE/('xl-terrain-recovery-20261011-'+INPUTS[4])/'diagnostic.json.gz');intrinsic=read(BASE/('xl-terrain-recovery-20261011-'+INPUTS[5])/'diagnostic.json.gz')
 qualified=set(next(r for r in paths['rows']if r['mode']=='providerOriginal')['qualifiedDiagnosticOwnedBodies']);assert len(qualified)==866 and not qualified.intersection(PARTS)
 claim=reservations.claim('elements11-images-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 try:
  DOC.mkdir(parents=True);records=[]
  for body in PARTS:
   item=graph['components'][body];uid=item['actorUID'];ids=sorted(item['globalOriginalFaces']);part=w[ids];offset,count=(0,12129)if uid=='landsd/204145:0'else(12129,11680);ownids=list(range(offset,offset+count));full=w[ownids]
   lo=part.min((0,1));hi=part.max((0,1));margin=np.maximum((hi-lo)*.6,[8.,5.,8.]);localids=[offset+int(i)for i in np.flatnonzero(np.all(full.max(1)>=lo-margin,axis=1)&np.all(full.min(1)<=hi+margin,axis=1))];local=w[localids]
   finite=[]
   for mode in fixture.k.MODES:
    row=next(r for r in docs['finite']['rows']if r['mode']==mode and r['uid']==uid);assert digest(worlds[mode][offset:offset+count].tobytes())==row['completeWorldSHA256'];faces=[row['allFaces'][i-offset]for i in ids]
    assert all(f['closedProjectionCovered']is True and f['existingOrdinaryClearanceBoundProved']is True and f['strictlyExposedWholeFacet']is True for f in faces)
    finite.append(dict(mode=mode,completeActorWorldSHA256=row['completeWorldSHA256'],completePartFiniteFindings=faces))
   fig=plt.figure(figsize=(24,10),dpi=100);pad=np.maximum((full.max((0,1))-full.min((0,1)))*.04,[1.,1.,1.])
   for j,(context,a,b,title,elev,azim)in enumerate([(full,full.min((0,1))-pad,full.max((0,1))+pad,'complete unchanged original actor',22,-55),(local,lo-margin,hi+margin,'wide original surrounding faces',25,-55),(local,lo-margin,hi+margin,'same complete source context / alternate view',50,45)]):
    plot(fig.add_subplot(1,3,j+1,projection='3d'),part,context,a,b,str(body)+' / '+title,elev,azim)
   fig.suptitle('Red: complete original part '+str(body)+'; grey: untouched same-actor source context (including unqualified parts). No function, mount, root or accepted role inferred.',fontsize=12);fig.tight_layout();image=DOC/(str(body)+'-whole-original-building-wide-source-context-2400x1000.png');fig.savefig(image);plt.close(fig)
   records.append(dict(originalBody=body,actorUID=uid,sourceSHA256=fixture.k.SOURCE_SHA[uid],completeOriginalFaces=ids,completeOriginalPartWorldSHA256=digest(part.tobytes()),completeOriginalBounds=dict(min=lo.tolist(),max=hi.tolist()),completeActorContextOriginalFaces=ownids,completeWideContextOriginalFaces=localids,wideContextBounds=dict(min=(lo-margin).tolist(),max=(hi+margin).tolist()),allFourStreamCompleteFiniteFindings=finite,allPriorIntrinsicFindingsVerbatim=[r for r in intrinsic['all15FourStreamIntrinsicCorrespondences']if r['originalBody']==body],contextImage=ref(image),greyContextDoesNotQualifyVisualHosts=True,sourceFunctionInferred=False,visualRoleAccepted=False,structuralRootOrBridgeCredit=False));pulse();print(dict(originalBody=body,faces=len(ids),wideContextFaces=len(localids),image=str(image.relative_to(ROOT))),flush=True)
  pulse(True);assert len(records)==11 and all(ref(ROOT/q['path'])==q for q in refs)
  save(DOC/'diagnostic.json.gz',dict(uids=['landsd/204145:0','landsd/204143:0'],complete11OriginalImageContexts=records,sourceOnly=True,noNewDistanceSearch=True,noFreshCurrentCapture=True,sourceGeometryChanges=0,visualRoleAccepted=False,currentAcceptance=False,structuralRootOrBridgeCredit=False,nativeReacceptance=False,newlyInstalled=0,evidenceRefs=refs))
  freezer=load('elements11_image_context_freeze',HERE/HELPERS[-1]);freezer.freeze(BATCH,'elements11-whole-original-building-wide-source-images-only-no-role-credit-v2',[ROOT/q['path']for q in refs]+list(DOC.iterdir()),dict(uids=['landsd/204145:0','landsd/204143:0'],completeOriginalParts=11,sourceOnly=True,visualRoleAccepted=False,currentAcceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()

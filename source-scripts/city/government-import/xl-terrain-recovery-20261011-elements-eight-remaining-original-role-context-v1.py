"""Bounded visual review of eight complete original held bodies.

No numerical mounting predicate is introduced or rerun. The original complete
part is highlighted with explicitly cropped already-qualified same-actor
source context; all existing four-stream negative findings remain verbatim.
Images alone provide no function, role, structural or current acceptance.
"""
from pathlib import Path
import importlib.util,sys,uuid
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect,reservations
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-elements-eight-remaining-original-role-context-v1';DOC=BASE/BATCH
PARTS=(69,75,76,78,705,744,897,921)
INPUTS=('xl-terrain-recovery-20261011-elements-complete-owned-original-contact-graph-v1','xl-terrain-recovery-20261011-elements132-four-stream-qualified-host-association-v1','xl-terrain-recovery-20261011-elements-owned-four-stream-complete-finite-v1','xl-terrain-recovery-20261011-elements-sun-star-two-current-render-attribute-capture-v1','xl-terrain-recovery-20261011-elements-bounded-owned-four-stream-path-replay-v1','xl-terrain-recovery-20261011-elements132-remaining-original-bodies-context-v1','xl-terrain-recovery-20261011-elements-seven-original-host-loop-correspondence-v1')
HELPERS=('test_elements24_named_original_mounted_visual_surface_proposal_v1_20261011.py','elements24_named_original_mounted_visual_surface_proposal_v1_20261011.py','exact_packed_world_geometry_20261009.py','exact_original_shared_edge_component_census_v2_20261011.py','xl-popcorn-source-investigations-checkpoints-20261009.py')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def load(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]+[ref(HERE/n)for n in HELPERS]
 for batch in INPUTS:
  folder=BASE/batch;r=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(ref(folder/'result.json'))
  for binding in r['evidenceRefs']:
   p=ROOT/binding['path'];assert p.is_file()and ref(p)==binding;refs.append(binding)
 refs=list({(r['path'],r['sha256']):r for r in refs}.values());assert all(ref(ROOT/r['path'])==r for r in refs)
 fixture=load('elements_eight_original_context_source_fixture',HERE/HELPERS[0]);docs,packages=fixture.actual_fixture();w=next(iter(packages.values()))['worlds']['providerOriginal'];graph=docs['graph'];contexts=read(BASE/INPUTS[5]/'diagnostic.json.gz');paths=read(BASE/INPUTS[4]/'diagnostic.json.gz');qualified=set(next(r for r in paths['rows']if r['mode']=='providerOriginal')['qualifiedDiagnosticOwnedBodies']);assert len(qualified)==866 and not qualified.intersection(PARTS)
 claim=reservations.claim('elements-eight-context-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  records=[];fig=plt.figure(figsize=(24,14),dpi=100)
  for slot,body in enumerate(PARTS):
   item=graph['components'][body];ids=sorted(item['globalOriginalFaces']);t=w[ids];lo=t.min((0,1));hi=t.max((0,1));extent=hi-lo;margin=np.maximum(extent*.15,[.25,.25,.25]);sameactor=sorted(f for i in qualified if graph['components'][i]['actorUID']==item['actorUID']for f in graph['components'][i]['globalOriginalFaces']);hosts=w[sameactor];keep=np.all(hosts.max(1)>=lo-margin,axis=1)&np.all(hosts.min(1)<=hi+margin,axis=1);cropped=[f for f,k in zip(sameactor,keep)if k]
   ax=fig.add_subplot(2,4,slot+1,projection='3d')
   if cropped:ax.add_collection3d(Poly3DCollection(w[cropped][:,:,[0,2,1]],facecolors='#bcc6cf',edgecolors='#7b8794',linewidths=.25,alpha=.25))
   ax.add_collection3d(Poly3DCollection(t[:,:,[0,2,1]],facecolors='#c84132',edgecolors='#682620',linewidths=.7,alpha=.9))
   for axis,start,end,pad in [('x',lo[0],hi[0],margin[0]),('y',lo[2],hi[2],margin[2]),('z',lo[1],hi[1],margin[1])]:getattr(ax,'set_'+axis+'lim')(start-pad,end+pad)
   ax.set_box_aspect((extent+2*margin)[[0,2,1]]);ax.view_init(elev=25,azim=-55);ax.set_axis_off();ax.set_title(str(body)+' / '+str(len(ids))+' complete original faces\nXYZ extent '+', '.join(format(float(v),'.3g')for v in extent)+' m',fontsize=10)
   original=next(r for r in contexts['all132Bodies']if r['originalBody']==body);assert original['completeGlobalOriginalFaces']==ids
   records.append(dict(originalBody=body,actorUID=item['actorUID'],completeOriginalSourceContextVerbatim=original,completeHighlightedOriginalFaces=ids,completeOriginalWorldSHA256=digest(t.tobytes()),croppedQualifiedSameActorOriginalContextFaces=cropped,contextCropIsVisualOnly=True,allFourStreamOriginalHostAssociationFindingsVerbatim=[next(a for a in r['all132OriginalBodyAssociations']if a['originalBody']==body)for r in docs['bands']['rows']],architectureFunctionInferred=False,visualRoleAccepted=False,structuralRootOrBridgeCredit=False));assert reservations.heartbeat(lease)['ok']and reservations.owns(lease)
  assert len(records)==8 and sum(len(r['completeHighlightedOriginalFaces'])for r in records)==61;fig.suptitle('Eight held original bodies / complete red source geometry / cropped qualified grey context / no accepted role or support',fontsize=13);fig.tight_layout();DOC.mkdir(parents=True);fig.savefig(DOC/'eight-complete-original-bodies-qualified-host-context-2400x1400.png');plt.close(fig)
  assert all(ref(ROOT/r['path'])==r for r in refs);save(DOC/'diagnostic.json.gz',dict(uids=['landsd/204145:0','landsd/204143:0'],allEightCompleteOriginalContexts=records,completeHeldOriginalFaces=61,originalSourceGeometryChanges=0,sourceOnly=True,noFreshCurrentCapture=True,currentAcceptance=False,visualRoleAccepted=False,structuralRootOrBridgeCredit=False,newlyInstalled=0,evidenceRefs=refs));freezer=load('elements_eight_original_context_freeze',HERE/HELPERS[-1]);freezer.freeze(BATCH,'elements-eight-complete-original-held-body-source-context-no-role-credit-v1',[ROOT/r['path']for r in refs]+list(DOC.iterdir()),dict(uids=['landsd/204145:0','landsd/204143:0'],completeHeldParts=8,completeOriginalFaces=61,sourceOnly=True,visualRoleAccepted=False,currentAcceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()

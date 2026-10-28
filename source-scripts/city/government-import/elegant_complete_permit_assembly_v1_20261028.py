"""Measure complete officially enumerated original assemblies under existing limits.

No parent/name exclusions, thresholds, source poses or approval flags change.
"""
import argparse,sys,uuid
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_source_assembly_diagnostic import COVERAGE_REASONS
BASE=ROOT/'docs/astra-city/government-import';CAP='government-xl-elegant-garden-seventeen-original-current-selection-v1-20261028'
CENSUS='government-xl-elegant-garden-complete-two-permit-records-v1-20261028';PRIMARY='government-xl-elegant-garden-current-primary-records-v1-20261028';SCOPE='government-xl-elegant-garden-sixteen-original-updated-scope-v1-20261028'
IDENTITIES={**{u:'government-xl-elegant-garden-seven-original-identities-v1-20261028'for u in ['landsd/173532:0','landsd/173768:0','landsd/236170:0']},'landsd/173764:0':'government-xl-elegant-garden-followup-two-original-identities-v1-20261028','landsd/228592:0':'government-xl-elegant-garden-rex-podium-current-identity-v1-20261028'}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args()
 assert a.batch.startswith('government-xl-')and '/'not in a.batch
 out=BASE/a.batch;local=HERE/'local'/a.batch;lp=local/'reservation.json';assert not out.exists()
 rp=BASE/'government-xl-elegant-garden-sixteen-original-updated-terrain-plan-v1-20261028.json';resources=set(read(rp)['resources'])
 if not a.owned:
  assert not local.exists();claim=reservations.claim('elegant-complete-assembly-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=3600);assert claim['ok']
  return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
 lease=read(lp);assert reservations.owns(lease)and resources<=set(lease['resources']);refs=[Path(__file__),rp];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selected=take(CAP,'selection.json.gz');sources={r['uid']:r for r in selected['rows']};census=take(CENSUS,'summary.json');primary=take(PRIMARY,'summary.json');forms=take(SCOPE,'form-obligations.json.gz')
 official={r['csuid']:r for r in primary['rows']};manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
 allrows=[];out.mkdir()
 for group in census['rows']:
  assert reservations.owns(lease);assert group['allMembersHaveSelectedOriginals']and not group['membersWithoutSelectedOriginals']
  uids=group['selectedSourceUIDs'];assert len(uids)in [2,3]and set(uids)<=set(IDENTITIES)
  assert {sources[u]['source']['building']['buildingCSUID']for u in uids}==set(group['completeCSUIDs'])
  triangles={};raw={};targets=[];projections=[];vertices=[];hard_reasons=[]
  for uid in uids:
   r=sources[uid];b=r['source']['building'];asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];refs.append(asset);t=decode_original_world_triangles(asset.read_bytes());assert len(t)==r['triangles'];triangles[uid]=t
   proof=take(IDENTITIES[uid],uid.split('/')[1]+'/identity.json');assert proof['sourceSHA256']==r['sourceSHA256']and proof['worldTrianglesSHA256']==digest(t.astype('<f8').tobytes());raw[uid]=proof
   hard_reasons.extend(uid+':'+s for s in set(proof['reasons'])-COVERAGE_REASONS)
   cell=proof['geographicCell'];assert cell['targetCoversWholeCell']and(cell['originalProjectionCoversWholeCell']or proof['exactWholeCellCoverage']['covered'])
   assert proof['freshCurrentIdentity']['exactObjectAndCSUID']
   row=official[b['buildingCSUID']];assert row['uniqueOfficialRecord'];f=row['officialRecords'][0]
   assert f['Status']=='Active'and f['BuildingBlockType']==b['structureType']and f['BaseHeight']==b['base']and abs(f['TopHeight']-b['base']-b['height'])<1e-8
   projections.append(shapely.union_all([shapely.MultiPoint(face[:,[0,2]]).convex_hull for face in t]));targets.append(Polygon(b['rings'][0],b['rings'][1:]));vertices.append(t[:,:,[0,2]].reshape(-1,2))
  source=shapely.union_all(projections);target=shapely.union_all(targets);others=shapely.union_all([Polygon(f['rings'][0],f['rings'][1:])for f in forms if f['uid']not in uids]);excess=source.difference(target)
  measures=dict(coverage=source.intersection(target).area/target.area,maximumExtentM=float(shapely.distance(shapely.points(np.concatenate(vertices)),target).max()),unrelatedExcessM2=excess.intersection(others).area,sourceFaces=sum(len(t)for t in triangles.values()),sourceProjectionAreaM2=source.area,targetAreaM2=target.area)
  reasons=list(hard_reasons)
  if measures['coverage']<.95:reasons.append('complete-permit-coverage-below-.95')
  if measures['maximumExtentM']>10:reasons.append('complete-permit-extent-above-10m')
  if measures['unrelatedExcessM2']>1:reasons.append('complete-permit-unrelated-excess-above-1m2')
  slug=group['permit'].replace('/','-');fig=plt.figure(figsize=(18,8),layout='constrained');ax=fig.add_subplot(1,3,1)
  colors=['#df8b40','#4275ab','#60a56d']
  for color,uid in zip(colors,uids):
   t=triangles[uid];ax.add_collection(PolyCollection(t[:,:,[0,2]],facecolors=color,edgecolors=color,alpha=.25,linewidth=.1))
   b=sources[uid]['source']['building']
   for ring in b['rings']:
    xy=np.asarray(ring);ax.plot(xy[:,0],xy[:,1],color=color,linewidth=1.5,label=uid)
  ax.autoscale();ax.set_aspect('equal');ax.grid(alpha=.2);ax.legend(fontsize=7);ax.set_title('Complete originals and all member footprints')
  complete=np.concatenate(list(triangles.values()));lo,hi=complete.min((0,1)),complete.max((0,1));size=np.maximum((hi-lo)[[0,2,1]],.1)
  for k,angle in enumerate([35,215],2):
   view=fig.add_subplot(1,3,k,projection='3d')
   for color,uid in zip(colors,uids):view.add_collection3d(Poly3DCollection((triangles[uid]-lo)[:,:,[0,2,1]],facecolors=color,edgecolors=color,alpha=.55,linewidth=.12))
   view.set(xlim=(0,size[0]),ylim=(0,size[1]),zlim=(0,size[2]),xlabel='X offset m',ylabel='Z offset m',zlabel='Y offset m');view.set_box_aspect(size.copy());view.view_init(22,angle);view.set_title('All immutable source facets')
  fig.suptitle(f"Permit {group['permit']} · {len(uids)} complete official members\nCoverage {measures['coverage']:.4%}; extent {measures['maximumExtentM']:.4f}m; unrelated excess {measures['unrelatedExcessM2']:.6f}m². Diagnostic only.")
  image=out/(slug+'.png');fig.savefig(image,dpi=140);plt.close(fig);refs.append(image)
  record=dict(permit=group['permit'],uids=uids,completeCSUIDs=group['completeCSUIDs'],measures=measures,reasons=reasons,assemblyLimitsPassed=not reasons,sourceSHA256ByUid={u:sources[u]['sourceSHA256']for u in uids},rawIndividualIdentity=raw,export=dict(path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes()),dimensions=[2520,1120]),identityAccepted=False)
  save(out/(slug+'.json'),record);allrows.append(record);print(dict(permit=group['permit'],measures=measures,reasons=reasons),flush=True)
 result=dict(uids=sorted({u for r in allrows for u in r['uids']}),rows=allrows,sourceGeometryChanges=0,sourcePoseChanges=0,identityAccepted=False,physicalAccepted=False,installationApproved=False,
  qualification='Complete fresh official permit membership, individually authenticated exact source/CSUID/full metre-cell routes, and complete primitive projections. Existing95%/10m/1m² limits applied to the complete assembly. EVERY other current scoped form remains unrelated, with no same-parent or name exclusion. Raw individual failures retained. Images require actual inspection. Assembly measurements grant no identity, architectural/support, collision or publication approval.')
 save(out/'summary.json',result);refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','original_source_assembly_diagnostic.py']);assert reservations.owns(lease)
 module('complete_assembly_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-official-permit-original-assembly-spatial-diagnostic',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()

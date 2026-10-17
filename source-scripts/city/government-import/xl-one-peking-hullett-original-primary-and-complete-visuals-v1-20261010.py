"""Three complete original sources, precise excess surfaces and primary context.
This historical/current source interpretation grants no identity or physical credit.
"""
import importlib.util,json,sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
sys.path.insert(0,str(HERE.parent/'landsd-territory'));from source import request
BATCH='government-xl-one-peking-hullett-original-primary-and-complete-visuals-v1-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH
CONTEXT=DOC.parent/'government-xl-one-peking-hullett-complete-original-boundary-context-v1-20261010'
OWN='landsd/233985:0';FOREIGN='landsd/73140:0';TOWER='landsd/240487:0'
def main():
 assert not DOC.exists();DOC.mkdir(parents=True);context=read(CONTEXT/'diagnostic.json.gz');sources=context['sources'];triangles={};assets=[]
 for r in sources:
  asset=ROOT/r['source']['path'];raw=asset.read_bytes();assert digest(raw)==r['source']['sha256'];tri=decode_original_world_triangles(raw);assert digest(tri.tobytes())==r['worldTrianglesSHA256'];triangles[r['uid']]=tri;assets.append(asset)
 u='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0/query'
 raw,rec=request(u,dict(f='json',where="GeoRefNo IN ('3551217446','3555317380','3552117445')",outFields='*',returnGeometry='true',outSR='2326',resultRecordCount='1000',orderByFields='OBJECTID'))
 (DOC/'fresh-primary-model-georef-context.json').write_bytes(raw);save(DOC/'fresh-primary-model-georef-context.request.json',rec)
 # Independently sourced historic site arrangement; not surveyed current/property bounds.
 plan='https://www.amo.gov.hk/filemanager/amo/common/form/plan/plan_51.pdf'
 raw,rec=request(plan,json_expected=False);assert raw.startswith(b'%PDF');(DOC/'amo-former-marine-police-hq-context-plan.pdf').write_bytes(raw);save(DOC/'amo-former-marine-police-hq-context-plan.request.json',rec)
 own=triangles[OWN];marked=own[[r['sourceFace'] for r in context['affectedSourceFaces']]];centre=np.concatenate(list(triangles.values())).mean(axis=(0,1))
 def world(t):return np.stack([t[...,0]-centre[0],-t[...,2]+centre[2],t[...,1]],axis=-1)
 colors={OWN:'#b6b9bc',FOREIGN:'#087bbf',TOWER:'#d2b36d'}
 fig=plt.figure(figsize=(16,9),dpi=180);ax=fig.add_subplot(121,projection='3d')
 for uid,tri in triangles.items():ax.add_collection3d(Poly3DCollection(world(tri),facecolors=colors[uid],edgecolors='none',alpha=.68 if uid!=TOWER else .42))
 ax.add_collection3d(Poly3DCollection(world(marked),facecolors='#e33b2e',edgecolors='#731611',linewidths=.5,zorder=30))
 full=world(np.concatenate(list(triangles.values())));lo=full.min(axis=(0,1));hi=full.max(axis=(0,1));ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[1],hi[1]);ax.set_zlim(lo[2],hi[2]);ax.set_box_aspect(hi-lo);ax.view_init(29,-58)
 ax.set_title('All complete original government surfaces\nGrey One Peking podium; gold tower; blue installed Hullett House');ax.set_xlabel('East offset (m)');ax.set_ylabel('North offset (m)');ax.set_zlabel('HKPD (m)')
 top=fig.add_subplot(122)
 for uid,tri in triangles.items():top.add_collection(PolyCollection(tri[:,:,[0,2]],facecolors=colors[uid],edgecolors='none',alpha=.3))
 top.add_collection(PolyCollection(marked[:,:,[0,2]],facecolors='#e33b2e',edgecolors='#731611',linewidths=.35,zorder=30))
 for r in context['completeCurrentForms']:
  b=r['building']
  if b['uid'] not in [OWN,FOREIGN]:continue
  for ring in b['rings']:
   p=np.asarray(ring);top.plot(p[:,0],p[:,1],color='#252525' if b['uid']==OWN else '#0064a5',lw=1.2,zorder=35)
 xy=marked[:,:,[0,2]];lo=xy.min(axis=(0,1));hi=xy.max(axis=(0,1));top.set_xlim(lo[0]-4,hi[0]+4);top.set_ylim(lo[1]-4,hi[1]+4);top.invert_yaxis();top.set_aspect('equal');top.set_title('All36 excess faces and complete installed foreign silhouette\nCurrent 2D proxy5.270854m² vs actual source projection0.021723m²');top.set_xlabel('World X (m)');top.set_ylabel('World Z (m)')
 fig.suptitle('One Peking / Hullett House — distinct source-owned original surfaces',fontsize=16);fig.text(.5,.015,'Complete4114 +11670 +32635 original faces, all12 positive exact interfaces retained. No common ownership, surveyed site boundary, identity or physical acceptance inferred.',ha='center',fontsize=9);fig.tight_layout(rect=[0,.05,1,.94]);path=DOC/'complete-three-original-and-foreign-silhouette-2880x1620.png';fig.savefig(path);plt.close(fig)
 save(DOC/'render.json',dict(width=2880,height=1620,completeSourceFaceCounts={k:len(v) for k,v in triangles.items()},markedOriginalFaceIds=[r['sourceFace'] for r in context['affectedSourceFaces']],contextManifestSHA256=context['capturedManifestSHA256'],currentManifestAcceptanceClaimed=False,sourceGeometryChanges=0,identityAccepted=False,physicalAccepted=False))
 refs=[Path(__file__),CONTEXT/'result.json',CONTEXT/'diagnostic.json.gz',HERE/'exact_packed_world_geometry_20261009.py',*assets]
 refs += [p for p in DOC.rglob('*') if p.is_file()]
 spec=importlib.util.spec_from_file_location('peking_visual_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(BATCH,'one-peking-distinct-full-original-installed-foreign-silhouette-and-authoritative-site-context-v1',sorted(set(refs)),dict(uids=[OWN,FOREIGN,TOWER],completeFaces=sum(map(len,triangles.values())),sourceGeometryChanges=0,identityAccepted=False,physicalAccepted=False,publication=False,currentManifestAcceptanceClaimed=False))
 print(dict(render=str(path.relative_to(ROOT)),completeFaces=sum(map(len,triangles.values()))),flush=True)
if __name__=='__main__':main()

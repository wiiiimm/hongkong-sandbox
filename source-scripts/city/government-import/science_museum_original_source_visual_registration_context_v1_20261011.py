"""DRAFT scientific source context plots; all171+11520 faces unchanged.
Primary drawings stay separate/unmodified: no unproved pixel georeference or function.
"""
import json,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,read,digest,save
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from pathlib import Path
B=ROOT/'docs/astra-city/government-import';C=B/'government-xl-science-museum-open-sided-original-gltf-identity-comparison-v3-20261011';T=B/'government-xl-science-museum-original-open-sided-contact-topology-attribution-v1-20261011';P=B/'government-xl-science-museum-open-structure-primary-20261009';DOC=B/'government-xl-science-museum-original-source-visual-registration-context-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();d=read(C/'diagnostic.json.gz');t=read(T/'diagnostic.json.gz')
 for e in t['evidenceRefs']:assert ref(ROOT/e['path'])==e
 arr=C/'complete-original-viewer-coordinate-diagnostic.npz'
 with np.load(arr,allow_pickle=False)as n:own=n['triangles']
 assert own.shape==(171,3,3)and digest(own.astype('<f8').tobytes())==d['completeAuthoredMatrixWorldTrianglesSHA256'];sel=B/'government-xl-science-museum-partial-parent-20261005/selection.json.gz';r=next(x for x in read(sel)['rows']if x['uid']=='landsd/80343:0');asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];museum=decode_original_world_triangles(asset.read_bytes());assert museum.shape==(11520,3,3);DOC.mkdir();colours=['#e87722','#176fc1','#9f3ba7','#218349','#b12230'];fig,axes=plt.subplots(1,2,figsize=(16,8))
 for ax,zoom in zip(axes,[False,True]):
  ax.add_collection(PolyCollection(museum[:,:,[0,2]],facecolors='#dddddd',edgecolors='#aaaaaa',linewidths=.15,alpha=.55))
  for body in t['originalOpenBodyDetails']:
   fs=body['originalFaces'];ax.add_collection(PolyCollection(own[fs][:,:,[0,2]],facecolors=colours[body['body']],edgecolors=colours[body['body']],linewidths=.5,alpha=.35))
   xyz=own[fs].mean((0,1));ax.text(xyz[0],xyz[2],str(body['body']),color=colours[body['body']],fontsize=10)
  ring=np.asarray(t['sourceRegistrationToHistoricalBASIC']['savedHistoricalBASICForm']['rings'][0]);ax.plot(ring[:,0],ring[:,1],color='black',linestyle='--',linewidth=1,label='Saved BASIC83471 footprint')
  points=own.reshape(-1,3)if zoom else museum.reshape(-1,3);pad=2 if zoom else 5;lo=points.min(0);hi=points.max(0);ax.set_xlim(lo[0]-pad,hi[0]+pad);ax.set_ylim(hi[2]+pad,lo[2]-pad);ax.set_aspect('equal');ax.set_xlabel('Viewer X: east metres');ax.set_ylabel('Viewer Z: minus-north metres');ax.set_title('Original source extent'+(' / open-sided detail'if zoom else' / complete Museum'));ax.legend(loc='lower left');ax.grid(alpha=.2)
 fig.suptitle('Unchanged original Museum11520 + open-sided171 faces, bodies0–4\nExact geometry context; primary plans not pixel-registered; no architecture/root/installation approval');fig.tight_layout();fig.savefig(DOC/'original-complete-plan-context.png',dpi=160);plt.close(fig)
 for elevation,azimuth,label in [(32,-60,'south-east'),(30,125,'north-west')]:
  fig=plt.figure(figsize=(12,9));ax=fig.add_subplot(111,projection='3d');ax.add_collection3d(Poly3DCollection(museum[:,:,[0,2,1]],facecolor='#d0d0d0',edgecolor='#aaaaaa',linewidth=.08,alpha=.12))
  for body in t['originalOpenBodyDetails']:
   ax.add_collection3d(Poly3DCollection(own[body['originalFaces']][:,:,[0,2,1]],facecolor=colours[body['body']],edgecolor=colours[body['body']],linewidth=.45,alpha=.8))
  lo=own.min((0,1));hi=own.max((0,1));ax.set_xlim(lo[0]-3,hi[0]+3);ax.set_ylim(lo[2]-3,hi[2]+3);ax.set_zlim(lo[1]-3,hi[1]+3);ax.set_box_aspect([hi[0]-lo[0]+6,hi[2]-lo[2]+6,hi[1]-lo[1]+6]);ax.view_init(elevation,azimuth);ax.set_xlabel('Viewer X east');ax.set_ylabel('Viewer Z minus-north');ax.set_zlabel('Original source Y');ax.set_title('Complete unchanged original source, '+label+' context\nSurface crossings and five bodies unresolved; no inferred feature function');fig.savefig(DOC/('original-source-'+label+'-context.png'),dpi=160);plt.close(fig)
 refs=[ref(p)for p in [Path(__file__),arr,C/'diagnostic.json.gz',C/'result.json',T/'diagnostic.json.gz',T/'result.json',asset,sel,P/'architectural-services-museum-expansion-existing-plans.pdf',*[P/('plan-page-'+str(n)+'.png')for n in [3,5,6]]]];save(DOC/'context.json',dict(sourceOnly=True,currentAcceptance=False,identityAccepted=False,architectureRoleApproved=False,sourceGeometryChanges=0,primaryDrawingPixelGeoreferencePerformed=False,sourceCoordinatesOrPoseChanged=False,all171And11520SourceFacesPlotted=True,bodyColours=dict(enumerate(colours)),primaryPlanRegistrationRequirement='Compare actual source placement/outline and five bodies with unmodified primary site/ground/first-floor drawings. No unmeasured pixel warp, same-name actor ownership, height inference or attachment credit. Record ambiguity/plan vintage and53proper surface crossings if exact feature identification is unsupported.',evidenceRefs=refs))
if __name__=='__main__':main()

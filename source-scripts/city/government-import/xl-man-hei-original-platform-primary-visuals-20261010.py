"""Complete original source visual evidence; not geometry editing or acceptance."""
import numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from run import ROOT,HERE,read,digest,save
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from lei_tung_named_original_lower_platform_identity_20261010 import polygon
DOC=ROOT/'docs/astra-city/government-import/government-xl-man-hei-original-platform-primary-visuals-20261010';BASE=DOC.parent
UPPER=BASE/'government-xl-man-fuk-nine-current-identity-75694-0-20261010';PLATFORM=BASE/'government-xl-man-fuk-complete-retained-original-physical-v5-20261010';GAPS=BASE/'government-xl-man-hei-original-platform-missing-floor-diagnostic-20261010'
def main():
 assert not DOC.exists();rows=[read(d/'selection.json.gz')['rows'][0] for d in [UPPER,PLATFORM]];tri=[];pins=[]
 for r in rows:
  p=ROOT/r['candidate']['path'];raw=p.read_bytes();assert digest(raw)==r['sourceSHA256'];tri.append(decode_original_world_triangles(raw));pins.append({'path':str(p.relative_to(ROOT)),'sha256':digest(raw)})
 fig,ax=plt.subplots(1,2,figsize=(16,9),dpi=150);a,b=tri
 for x in ax:
  x.add_collection(PolyCollection(b[:,:,[0,2]],facecolors='#d2dadd',edgecolors='#bbc5c9',linewidths=.10));x.add_collection(PolyCollection(a[:,:,[0,2]],facecolors='#e5b453',edgecolors='#826522',linewidths=.2))
  for ring in rows[0]['source']['building']['rings']:
   r=np.asarray(ring);x.plot(r[:,0],r[:,1],color='#0060ad',lw=1,label='Current named Block H footprint')
  x.set_aspect('equal');x.grid(alpha=.15)
 lim=np.concatenate(tri).reshape(-1,3);ax[0].set_xlim(lim[:,0].min()-5,lim[:,0].max()+5);ax[0].set_ylim(lim[:,2].min()-5,lim[:,2].max()+5);ax[0].set_title('Complete originals: platform10661faces + BlockH2286faces')
 lo=a.min((0,1));hi=a.max((0,1));ax[1].set_xlim(lo[0]-3,hi[0]+3);ax[1].set_ylim(lo[2]-3,hi[2]+3);ax[1].set_title('Named upper footprint and genuine missing floor witnesses')
 g=read(GAPS/'diagnostic.json.gz')
 for region in g['completeMissingRegionDispositions']:
  for f in region['allFiniteFacets']:
   q=f['completeOriginalUpwardFloorCoverage']
   if not q['exactProjectionCovered']:
    v=np.asarray(f['literalMissingRegionProofFacet']);ax[1].add_collection(PolyCollection([v[:,[0,2]]],facecolors='none',edgecolors='red',linewidths=1));w=[float(__import__('fractions').Fraction(x)) for x in q['exactUncoveredInteriorWitnessXZ']];ax[1].plot(w[0],w[1],'rx')
 fig.suptitle('Untouched originals; blue exact current tower outline, red real finite noncoverage. No identity/support credit.');fig.tight_layout();DOC.mkdir(parents=True);fig.savefig(DOC/'complete-original-pair-2400x1350.png');plt.close(fig);save(DOC/'render.json',{'dimensions':[2400,1350],'sourcePins':pins,'allOriginalFaces':[2286,10661],'sourceGeometryChanges':0,'identityAccepted':False,'imageBasedPrecisionClaims':False})
if __name__=='__main__':main()

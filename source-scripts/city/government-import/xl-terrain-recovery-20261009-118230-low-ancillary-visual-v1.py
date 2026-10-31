"""Exact original low exterior facets plotted for evidence interpretation only."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from run import ROOT,read,save,digest
BATCH='xl-terrain-recovery-20261009-118230-low-ancillary-visual-v1'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
INPUT=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-118230-low-ancillary-context-v1/diagnostic.json.gz'
def main():
 assert not DOC.exists();d=read(INPUT);rows=d['everyComponentFace'];tri=np.array([r['originalVertices'] for r in rows]);local=tri-[3300,0,-1730]
 fig,axs=plt.subplots(1,3,figsize=(15,6));failed=set(d['sevenRawExposureFailures'])
 for ax,dims,title in zip(axs,[(0,2),(0,1),(2,1)],['Original plan: hollow narrow cap/ring','Original x/elevation','Original z/elevation']):
  polygons=local[:,:,dims];colors=['#c83232' if r['sourceFace'] in failed else '#c9dce9' if r['normalYRatio']>.25 else '#d8d8d8' for r in rows]
  ax.add_collection(PolyCollection(polygons,facecolors=colors,edgecolors='#343434',linewidths=.45,alpha=.85));ax.autoscale();ax.set_aspect('equal');ax.set_title(title);ax.set_xlabel('Local x (m)' if dims[0]==0 else 'Local z (m)');ax.set_ylabel('Local z (m)' if dims[1]==2 else 'Original elevation (m HKPD)');ax.grid(alpha=.2)
  if dims==(0,2):
   for r,p in zip(rows,polygons):
    if r['sourceFace'] in failed:ax.annotate(str(r['sourceFace']),p.mean(axis=0),fontsize=7)
 fig.suptitle('Two Harbourfront: all 54 untouched original ancillary faces\nRed = seven historical below-grade side faces; blue = original upper caps. No acceptance or synthetic terrain.');fig.tight_layout();DOC.mkdir(parents=True);out=DOC/'original-low-part-1800x720.png';fig.savefig(out,dpi=120);plt.close(fig)
 save(DOC/'render.json',dict(inputPath=str(INPUT.relative_to(ROOT)),inputSHA256=digest(INPUT.read_bytes()),sourceSHA256=d['sourceSHA256'],originalWorldSHA256=d['completeSourceWorldSHA256'],completeOriginalPartFaces=d['component432OriginalFaces'],outputPath=str(out.relative_to(ROOT)),outputSHA256=digest(out.read_bytes()),width=1800,height=720,sourceGeometryChanges=0,diagnosticOnly=True,installationApproved=False,qualification='Plots every exact original part facet in orthographic projections. Historical red face classifications are retained. Figure is for source interpretation, not a browser/runtime/physical acceptance witness.'))
 print(out)
if __name__=='__main__':main()

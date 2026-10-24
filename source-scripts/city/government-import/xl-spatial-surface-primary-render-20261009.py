"""Render original primary PDF pages for source interpretation; no edits or tracing."""
from pathlib import Path
import pymupdf
from run import ROOT,save,digest
P=ROOT/'docs/astra-city/government-import/government-xl-spatial-surface-roles-20261009/primary';rows=[]
for name,page in [('kai-tak-cruise-terminal-pedestrian-map.pdf',0),('kai-tak-cruise-terminal-operator-floorplans.pdf',28)]:
 p=P/name;d=pymupdf.open(p);out=P/(name.replace('.pdf',f'-page-{page+1}.png'));d[page].get_pixmap(matrix=pymupdf.Matrix(1.5,1.5)).save(out);rows.append({'sourcePath':str(p.relative_to(ROOT)),'sourceSHA256':digest(p.read_bytes()),'pageZeroBased':page,'renderPath':str(out.relative_to(ROOT)),'renderSHA256':digest(out.read_bytes()),'pymupdfVersion':pymupdf.VersionBind,'renderScale':1.5,'sourceImageEdits':0})
save(P/'original-page-render-receipts.json',{'rows':rows})

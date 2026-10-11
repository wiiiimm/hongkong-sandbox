"""Rank new topology diagnostics for targeted primary research, never auto-accept."""
from collections import Counter
import csv
from run import ROOT,read,save
DOC=ROOT/'docs/astra-city/government-import/government-xl-spatial-surface-roles-20261009'
j=read(DOC/'topological-failure-ranking.json.gz');assert j['checked']==179
rows=[];counts=Counter();op=[]
for r in j['rows']:
 v=r['variants'].get('direct-shared-OSM');families=v['diagnosticFamilies'] if v else r['diagnosticFamilies'];counts.update(families);stats=v['stats'] if v else {};coverage=stats.get('targetCoverage');interior=stats.get('missingInteriorAreaM2',0);total=stats.get('missingTotalAreaM2',0)
 priority=0 if 'missing-interior-area' in families else 1 if families==['source-authored-extra-extent-role-unresolved'] and stats.get('maximumSourceExtentM',100)<=20 else 2 if families==['overlapping-source-surface-ownership-unresolved'] and stats.get('excessOverOtherFormsM2',100)<=5 else 3 if 'bounds-pass-other-identity-contract-unresolved' in families else 4
 rows.append({'uid':r['uid'],'name':r['name'],'modelId':r['modelId'],'sourceSHA256':r['sourceSHA256'],'researchPriority':priority,'diagnosticFamilies':families,'targetCoverage':coverage,'missingInteriorAreaM2':interior,'missingBoundaryAreaM2':stats.get('missingBoundaryConnectedAreaM2'),'originalExtentM':stats.get('maximumSourceExtentM'),'overlapM2':stats.get('excessOverOtherFormsM2'),'interpretationRequired':True,'identityAccepted':False,'installationApproved':False})
 if 'official-OP-structure' in r['variants']:op.append({'uid':r['uid'],'name':r['name'],'stats':r['variants']['official-OP-structure']['stats'],'diagnosticFamilies':r['variants']['official-OP-structure']['diagnosticFamilies']})
rows.sort(key=lambda r:(r['researchPriority'],-(r['targetCoverage'] or 0),r['uid']));save(DOC/'research-ranking.json.gz',{'rows':rows,'familyCountsOverlap':dict(counts),'opGroups':op,'all179Accounted':True,'aiGeometryModelling':False,'geometryChanges':0,'newPositiveAcceptanceProofs':0,'qualification':'Prioritisation uses new exact uncovered topology and visible-surface height diagnostics, not triangle count. Scores select research only; no source corruption/permanent rejection/acceptance inferred.'})
with (DOC/'research-ranking.csv').open('w') as f:
 fields=['uid','name','modelId','researchPriority','diagnosticFamilies','targetCoverage','missingInteriorAreaM2','missingBoundaryAreaM2','originalExtentM','overlapM2'];w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
print({'familyCountsOverlap':dict(counts),'officialOPVariants':len(op),'primaryResearchPriorityUids':[r['uid'] for r in rows if r['researchPriority']==0]},flush=True)

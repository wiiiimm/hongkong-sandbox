"""Account for every raw support failure, without assigning architectural approval."""
import numpy as np
from collections import Counter
from run import ROOT, read, save, digest
DOC=ROOT/'docs/astra-city/government-import/government-xl-popcorn-source-support-roles-20261009'
PRIOR=ROOT/'docs/astra-city/government-import/government-xl-popcorn-original-pair-interface-20261009'
raw=read(PRIOR/'exact-original-interface-diagnostic.json.gz')['rows'][0]
parts=read(PRIOR/'complete-station-source-shells-and-mall-attachments.json.gz')['components']
owner={f:i for i,p in enumerate(parts) for f in p['originalSourceFaces']}
contacts=read(DOC/'every-original-station-to-mall-contact.json.gz')
touch=set(r['sourceFaceA'] for r in contacts['contacts'])
rows=[]
for r in raw['unresolved']:
 faces=r['originalSourceFaces']
 ids=sorted(set(f['faceIndex'] for f in faces))
 # Geometric measurements only: original normal is retained in each evidence row.
 rows.append({**r,'sourceComponents':sorted(set(owner[f] for f in ids)),
              'incidentOriginalFacesWithExactMallContact':sorted(set(ids)&touch),
              'incidentHorizontalOriginalFaces':[f['faceIndex'] for f in faces if abs(f['normal'][1])>.99],
              'incidentNearVerticalOriginalFaces':[f['faceIndex'] for f in faces if abs(f['normal'][1])<.05]})
out={'uid':raw['uid'],'sourceSHA256':raw['sourceSHA256'],'supportSHA256':raw['supportSHA256'],
     'rawFailures':rows,'rawFailureReasonCounts':dict(Counter(r['reason'] for r in rows)),
     'componentFailureCounts':dict(Counter(c for r in rows for c in r['sourceComponents'])),
     'samplesWithIncidentExactMallContactFace':sum(bool(r['incidentOriginalFacesWithExactMallContact']) for r in rows),
     'samplesWithoutNearVerticalIncidentFace':sum(not r['incidentNearVerticalOriginalFaces'] for r in rows),
     'horizontalIncidentOriginalFaceIds':sorted(set(f for r in rows for f in r['incidentHorizontalOriginalFaces'])),
     'geometryChanges':0,'physicalSupportAccepted':False,'installationApproved':False,
     'qualification':'Normal/original component accounting only. Near-vertical faces are not automatically facade/envelope roles, and no raw failure is waived.'}
save(DOC/'every-original-unresolved-rim-face-role.json.gz',out)
print({k:v for k,v in out.items() if k not in ['rawFailures','qualification']})

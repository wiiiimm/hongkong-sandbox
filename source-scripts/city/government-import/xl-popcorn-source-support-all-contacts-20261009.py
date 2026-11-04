"""Full station-to-mall exact source contact dimensions; no approval or model edits."""
import numpy as np
from collections import Counter
from run import ROOT, read, save, digest
from exact_original_component_contacts_20261009 import exact_component_contacts
DOC=ROOT/'docs/astra-city/government-import/government-xl-popcorn-source-support-roles-20261009'
PRIOR=ROOT/'docs/astra-city/government-import/government-xl-popcorn-original-pair-interface-20261009'
inp=read(PRIOR/'exact-original-contact-inputs.json.gz')
station=next(r for r in inp['rows'] if r['uid']=='landsd/295539:0')
mall=next(r for r in inp['rows'] if r['uid']=='landsd/295538:0')
a=np.array(station['position']).reshape(-1,3,3);b=np.array(mall['position']).reshape(-1,3,3)
parts=read(PRIOR/'complete-station-source-shells-and-mall-attachments.json.gz')['components']
owner={f:i for i,p in enumerate(parts) for f in p['originalSourceFaces']}
out=exact_component_contacts(a,list(range(len(a))),b,list(range(len(b))),maximum_pairs=300000)
for r in out['contacts']:r['stationComponent']=owner[r['sourceFaceA']]
out.update({'stationSourceSHA256':station['sourceSHA256'],'stationWorldTriangleSHA256':station['worldTriangleSHA256'],
            'mallSourceSHA256':mall['sourceSHA256'],'mallWorldTriangleSHA256':mall['worldTriangleSHA256'],
            'inputSHA256':digest((PRIOR/'exact-original-contact-inputs.json.gz').read_bytes()),
            'contactDimensionCounts':dict(Counter(r['dimension'] for r in out['contacts'])),
            'stationComponentsWithDirectMallContact':sorted(set(r['stationComponent'] for r in out['contacts'])),
            'qualification':'Source-only exact geometric contact census. No structural, grounded anchor, envelope-role or collision approval follows from contact dimension.'})
save(DOC/'every-original-station-to-mall-contact.json.gz',out)
print({'pairs':out['trianglePairsTested'],'contacts':len(out['contacts']),'dimensions':out['contactDimensionCounts'],
       'largest':sorted(out['contacts'],key=lambda r:r['maximumSpanM'],reverse=True)[:8]},flush=True)

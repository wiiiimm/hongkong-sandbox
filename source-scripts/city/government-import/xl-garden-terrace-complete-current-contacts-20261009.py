"""Complete original Garden Terrace surface contacts; no support acceptance."""
import numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from exact_original_component_contacts_20261009 import exact_component_contacts
DOC=ROOT/'docs/astra-city/government-import/government-xl-garden-terrace-complete-current-support-20261009'
GEOMETRY=HERE/'local/government-xl-garden-terrace-complete-original-physical-v2-20261009/runtime-geometry.json.gz'
def main():
    target=DOC/'exact-original-component-contacts.json.gz';assert not target.exists()
    runtime={r['uid']:r for r in read(GEOMETRY)['rows']}
    census=read(DOC/'diagnostic.json.gz');source=runtime['landsd/21894:0'];support=runtime['landsd/162285:0']
    tri=lambda g:np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
    tower,podium=tri(source),tri(support)
    assert len(tower)==10670 and len(podium)==1418
    faces=[r['originalRuntimeFaces'] for r in census['rows']]
    assert sorted(i for f in faces for i in f)==list(range(len(tower)))
    main_faces=faces[0];assert len(main_faces)==802
    anchor=exact_component_contacts(tower,main_faces,podium,list(range(len(podium))))
    attachments=[]
    for i,part in enumerate(faces[1:],1):
        result=exact_component_contacts(tower,part,tower,main_faces)
        attachments.append({'component':i,'sourceFaces':part,'originalContact':result})
        if i%25==0:print({'componentsChecked':i,'total':len(faces)},flush=True)
    paths=[GEOMETRY,DOC/'diagnostic.json.gz',Path(__file__),HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_shell_intersections_20261009.py']
    save(target,{'sourceUid':source['uid'],'supportUid':support['uid'],'sourceSHA256':source['sourceSHA256'],'supportSHA256':support['sourceSHA256'],'sourceFaces':len(tower),'supportFaces':len(podium),'mainOriginalFaces':main_faces,'mainToPodiumContacts':anchor,'rows':attachments,'completeOriginalFaceAccounting':True,'physicalSupportAccepted':False,'publication':False,'sourceGeometryChanges':0,'evidenceRefs':[{'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())} for p in paths],'qualification':'Every source component compared to the complete exact original main body, and the main body to all original podium faces. Point/line/area contact dimensions are preserved. Contact alone does not resolve incomplete strict ground/deck support, embedding, foreign interactions or installation gates.'})
    print({'mainPodiumContacts':len(anchor['contacts']),'mainLargestContactSpanM':max((r['maximumSpanM'] for r in anchor['contacts']),default=0),'directlyContactingComponents':sum(any(c['dimension']>0 for c in r['originalContact']['contacts']) for r in attachments),'totalOtherComponents':len(attachments),'physicalSupportAccepted':False},flush=True)
if __name__=='__main__':main()

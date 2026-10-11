"""Exact positive-length original component contact witnesses; no support approval."""
import importlib.util
import json
import uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from exact_original_shell_intersections_20261009 import rational_face,intersection_points

BATCH='government-xl-hoi-yu-positive-contact-attachment-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
CENSUS=ROOT/'docs/astra-city/government-import/government-xl-hoi-yu-source-components-20261009/components.json.gz'
SELECTION=ROOT/'docs/astra-city/government-import/government-xl-hoi-yu-original-pair-v2-20261009/selection.json.gz'

def main():
    assert not DOC.exists() and not LOCAL.exists()
    claim=reservations.claim('hoi-yu-exact-attachment-'+str(uuid.uuid4()),
        ['building:landsd/177604:0','building:landsd/177605:0'],batch=BATCH,ttl=1800)
    assert claim['ok'],claim
    lease=claim['reservation']
    save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
    try:
        census=read(CENSUS)
        row=next(r for r in read(SELECTION)['rows'] if r['uid']==census['uid'])
        raw=(ROOT/row['candidate']['path']).read_bytes()
        assert digest(raw)==row['sourceSHA256']==census['sourceSHA256']
        (LOCAL/'assets').mkdir()
        (LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz')).write_bytes(raw)
        spec=importlib.util.spec_from_file_location('hoi_yu_attachment_decoder',HERE/'xl-second-pass.py')
        decoder=importlib.util.module_from_spec(spec);spec.loader.exec_module(decoder);decoder.LOCAL=LOCAL
        triangles=decoder.glb_triangles({**row,'triangles':8775})
        components=census['components']
        main_index=max(range(len(components)),key=lambda i:components[i]['triangles'])
        body_ids=np.asarray(components[main_index]['originalSourceFaces'])
        body=triangles[body_ids];lower=body.min(axis=1);upper=body.max(axis=1)
        body_rational={};rows=[]
        for index,component in enumerate(components):
            if index==main_index:continue
            proof=None;tests=0;candidates=0
            for face_id in component['originalSourceFaces']:
                face=triangles[face_id];lo=face.min(axis=0);hi=face.max(axis=0)
                hits=np.flatnonzero(np.all(upper>=lo,axis=1)&np.all(lower<=hi,axis=1))
                candidates+=len(hits);rf=rational_face(face)
                for j in hits:
                    j=int(j);tests+=1
                    if j not in body_rational:body_rational[j]=rational_face(body[j])
                    points=intersection_points(rf,body_rational[j])
                    if len(points) >= 2:
                        proof={'sourceFace':face_id,'mainBodyFace':int(body_ids[j]),
                            'exactIntersectionPoints':[[str(v) for v in p] for p in sorted(points)]}
                        break
                if proof:break
            rows.append({'component':index,'triangles':component['triangles'],'bounds':component['bounds'],
                'contactWithMainBody':bool(proof),'witness':proof,'exactTrianglePairsTested':tests,
                'broadPhaseCandidatesVisited':candidates})
            assert reservations.heartbeat(lease)['ok']
            print(json.dumps({'component':index,'triangles':component['triangles'],'contact':bool(proof),'exactPairs':tests}),flush=True)
        paths=[CENSUS,SELECTION,Path(__file__),HERE/'exact_original_shell_intersections_20261009.py',HERE/'xl-second-pass.py',ROOT/row['candidate']['path']]
        save(DOC/'diagnostic.json.gz',{'uid':census['uid'],'sourceSHA256':row['sourceSHA256'],
            'sourceTriangles':8775,'componentCount':32,'mainBodyComponent':main_index,'rows':rows,
            'evidenceRefs':[{'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())} for p in paths],
            'coordinateArithmetic':'exact rational of original decoded binary coordinates',
            'modelGeometryChanges':0,'installationApproved':False,'newlyInstalled':0,
            'qualification':'An exact positive-length surface intersection witness establishes original geometric attachment only. It does not classify a component as decorative, certify structural support, excuse foreign intersections or replace complete terrain/neighbour/runtime acceptance. Components without a direct witness may need attachment through another original component.'})
    finally:
        assert reservations.release(lease)['ok']

if __name__=='__main__':main()

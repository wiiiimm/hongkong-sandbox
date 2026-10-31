"""Complete unchanged original PopCorn envelope diagnosis; no placement credit."""
import importlib.util, json, uuid
from pathlib import Path
from fractions import Fraction
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,reservations
from original_open_vertical_envelope_20261009 import diagnose
from original_degenerate_ground_context_20261009 import degenerate_ground_context

BATCH='government-xl-popcorn-original-open-envelope-context-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
INPUT=ROOT/'docs/astra-city/government-import/government-xl-popcorn-original-pair-interface-20261009/exact-original-contact-inputs.json.gz'
TIN=ROOT/'docs/astra-city/government-import/government-xl-popcorn-source-support-roles-20261009/exact-original-mall-ground-contact-inputs.json.gz'
GRAPH=ROOT/'docs/astra-city/government-import/government-xl-popcorn-original-wall-contact-20261009/affected-original-component-census.json.gz'
CONTEXT=ROOT/'docs/astra-city/government-import/government-xl-popcorn-original-complete-face-ground-20261009/295538-0-complete-face-context.json.gz'
UID='landsd/295538:0'

def main():
    assert not (DOC/'result.json').exists(), 'Fresh immutable diagnostic required'
    source=next(r for r in read(INPUT)['rows'] if r['uid']==UID)
    tri=np.asarray(source['position'],dtype='<f8').reshape(-1,3,3)
    assert digest(tri.tobytes())==source['worldTriangleSHA256']
    data=read(TIN);ground=np.asarray(data['terrain']['position'],dtype='<f8').reshape(-1,3,3)
    assert digest(ground.tobytes())==data['terrain']['worldTriangleSHA256']
    polygons=shapely.polygons(ground[:,:,[0,2]]);keep=shapely.area(polygons)>1e-10
    ground,polygons=ground[keep],polygons[keep];tree=shapely.STRtree(polygons)
    context=read(CONTEXT);assert len(context['faces'])==len(tri)
    census=read(GRAPH)['components'];wanted=[11473,14556,14658,14660,13330]
    claim=reservations.claim('popcorn-open-envelope-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=1800)
    assert claim['ok'],claim;lease=claim['reservation'];rows=[]
    try:
        for key in wanted:
            part=next(p for p in census if p['component']==key);ids=part['originalFaces']
            try:
                result=diagnose(tri,ids);vertices=np.unique(tri[ids].reshape(-1,3),axis=0)
                heights=sorted(set(vertices[:,1]));boundaries=[]
                for y in heights:
                    for strip in result['completeOriginalStrips']:
                        a,b=[[float(Fraction(x)) for x in p] for p in strip['planEndpoints']]
                        line=np.array([[a[0],y,a[1]],[b[0],y,b[1]],[a[0],y,a[1]]])
                        g=degenerate_ground_context(line,ground,polygons,tree)
                        boundaries.append({'originalHeight':float(y),'originalPlanEndpoints':[a,b],'ground':g})
                result.update(completeOriginalBoundaryGroundContexts=boundaries,
                              everyOriginalBoundaryCovered=all(b['ground']['groundProjectionCovered'] for b in boundaries),
                              originalTopBoundaryMinimumGapM=min(b['ground']['minimum']['minimumGapM'] for b in boundaries if b['originalHeight']==heights[-1]),
                              rawComponentMinimumGapM=min(context['faces'][i]['minimum']['minimumGapM'] for i in ids),
                              rawAffectedOriginalFaces=[i for i in ids if context['faces'][i]['minimum']['minimumGapM']<-.5])
                row={'component':key,'exactOpenEnvelopeRecognized':True,'diagnostic':result}
            except AssertionError as e:
                row={'component':key,'exactOpenEnvelopeRecognized':False,'originalFaces':ids,'reason':str(e),'sourceGeometryChanges':0,'installationApproved':False}
            save(DOC/(str(key)+'-exact-original-envelope.json.gz'),row);rows.append(row)
            assert reservations.heartbeat(lease)['ok']
            print(json.dumps({k:v for k,v in row.items() if k!='diagnostic'}),flush=True)
        spec=importlib.util.spec_from_file_location('popcorn_open_envelope_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        paths=[Path(__file__),INPUT,TIN,GRAPH,CONTEXT,HERE/'original_open_vertical_envelope_20261009.py',HERE/'test_original_open_vertical_envelope_20261009.py',HERE/'original_degenerate_ground_context_20261009.py',HERE/'original_face_ground_crossing_20261009.py']
        m.freeze(BATCH,'complete-exact-original-uncapped-envelope-context-v1',paths,{'uids':[UID],'wholeSourceFaces':len(tri),'rows':[{'component':r['component'],'exactOpenEnvelopeRecognized':r['exactOpenEnvelopeRecognized'],'reason':r.get('reason'),'originalTopBoundaryMinimumGapM':r.get('diagnostic',{}).get('originalTopBoundaryMinimumGapM')} for r in rows],'humanStatus':'held-unknown','requiresMoreComputeOrSourceEvidence':True,'requiresAIModelGeometry':False,'requiresHumanDecision':False,'sourceOnlyDiagnostic':True,'currentDrawnTerrainAcceptance':False,'remainingReason':'source-specific-open-wall-panel-underbody-roles-and-complete-current-physical-gates-pending','nextStep':'Complete original source-specific surface role review with all current foreign actors; retain every raw burial and unsupported component. No architectural-purpose or installation credit from an uncapped plan envelope alone.'})
    finally:assert reservations.release(lease)['ok']

if __name__=='__main__':main()

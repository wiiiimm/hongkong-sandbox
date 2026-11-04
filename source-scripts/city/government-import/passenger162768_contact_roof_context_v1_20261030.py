"""Read-only four-world roof coverage context; no suppression or acceptance."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module

P = 'government-xl-passenger162768-after-civic-five-'
BATCH = P+'contact-roof-context-v1-20261030'
IDS = {71245,83090,129770,153422,161537,161745,232103,332872}

def main():
    base=ROOT/'docs/astra-city/government-import'; doc=base/BATCH
    assert not (doc/'result.json').exists()
    refs=[Path(__file__)]; pins={}
    def take(batch, filename):
        if batch not in pins:
            pins[batch]=authenticate(base/batch)[1]; refs.append(base/batch/'result.json')
        path=base/batch/filename
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))]
        refs.append(path); return read(path)
    selection=take(P+'current-ground-v1-20261030','selection.json.gz')
    row=next(r for r in selection['rows'] if r['uid']=='landsd/162768:0')
    attr=next(r for r in take(P+'attributes-v1-20261030','attributes.json.gz')['rows'] if r['uid']==row['uid'])
    asset=ROOT/row['candidate']['path']; refs.append(asset)
    assert digest(asset.read_bytes())==row['sourceSHA256']==attr['sourceSHA256']
    index=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
    worlds={'packed':decode_original_world_triangles(asset.read_bytes())}
    for key in ['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']:
        worlds[key]=np.asarray(attr[key]).reshape(-1,3)[index]
    forms=take(P+'source-scope-v1-20261030','162768:0-forms.json.gz')
    selected=[r['building'] for r in forms if r['building']['objectId'] in IDS]
    assert len(selected)==len(IDS)
    rows=[]
    for mode,tri in worlds.items():
        assert len(tri)==32238
        normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
        # Existing roof-context convention: upward facets, normal Y > 0.25 length.
        up=normal[:,1]>.25*np.linalg.norm(normal,axis=1)
        polys=shapely.polygons(tri[:,:,[0,2]])
        valid=shapely.area(polys)>0
        for b in selected:
            footprint=shapely.Polygon(b['rings'][0],b['rings'][1:])
            assert footprint.is_valid and footprint.area>0
            hits=valid & shapely.intersects(polys,footprint)
            overlap=shapely.union_all(polys[hits]).intersection(footprint)
            roof=[]
            for label,height in [('above-base',b['base']),('near-basic-top',b['base']+b['height']-1),('above-basic-top',b['base']+b['height'])]:
                mask=hits & up & (tri[:,:,1].min(1)>=height)
                covered=shapely.union_all(polys[mask]).intersection(footprint)
                roof.append(dict(label=label,minimumWholeFacetHeightM=height,facets=int(mask.sum()),coverageM2=covered.area,coverageFraction=covered.area/footprint.area))
            rows.append(dict(mode=mode,uid=b['uid'],name=b.get('name'),buildingCSUID=b.get('buildingCSUID'),buildingId=b.get('buildingId'),parent=b.get('parent'),structureType=b.get('structureType'),basicBaseM=b['base'],basicTopM=b['base']+b['height'],basicFootprintM2=footprint.area,originalProjectionCoverageM2=overlap.area,originalProjectionCoverageFraction=overlap.area/footprint.area,roof=roof))
    result=dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],completeOriginalFaces=32238,worldModes=list(worlds),rows=rows,sourceGeometryChanges=0,terrainEdits=False,duplicateSuppressionApproved=False,identityAccepted=False,physicalAcceptance=False,installationApproved=False,qualification='Conservative whole-facet upward roof projection coverage only. Shared parent/contact/coverage is not component ownership or support proof. All BASIC models remain retained; exact source intersections, identity, architecture, terrain and browser review remain required.')
    save(doc/'summary.json',result)
    module('passenger_roof_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'passenger-whole-original-four-world-contact-roof-context',refs,result)
    print('Completed read-only roof context:',len(rows),'rows; no approval or publication')

if __name__=='__main__': main()

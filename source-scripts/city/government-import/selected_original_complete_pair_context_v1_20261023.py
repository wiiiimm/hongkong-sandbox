"""Complete immutable original-pair contact and footprint evidence, no approval."""
import argparse
from pathlib import Path
from collections import Counter
from fractions import Fraction
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_primitive_contacts_v1 import exact_component_contacts_with_primitives
from exact_original_shell_intersections_20261009 import rational_face
from exact_contact_role_context_v1_20261023 import contact_role

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','capture','a','b']:p.add_argument('--'+key,required=True)
    args=p.parse_args();assert args.batch.startswith('government-xl-')and'/'not in args.batch and args.a!=args.b
    base=ROOT/'docs/astra-city/government-import';out=base/args.batch;assert not out.exists();_,pins=authenticate(base/args.capture);path=base/args.capture/'selection.json.gz';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];selection=read(path);rows=[next(r for r in selection['rows']if r['uid']==uid)for uid in [args.a,args.b]];refs=[Path(__file__),base/args.capture/'result.json',path];triangles=[];polygons=[]
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    for row in rows:
        tile=ROOT/'3d-viewer'/row['source']['tile'];assert [f for f in read(tile)['buildings']if f['uid']==row['uid']]==[row['source']['building']];refs.append(tile)
        asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];refs.append(asset);t=decode_original_world_triangles(raw);assert len(t)==row['triangles'];triangles.append(t);f=row['source']['building'];polygons.append(shapely.Polygon(f['rings'][0],f['rings'][1:]))
    raw=exact_component_contacts_with_primitives(triangles[0],range(len(triangles[0])),triangles[1],range(len(triangles[1])),maximum_pairs=1000000);assert raw['allPairsExamined'];save(out/'complete-exact-contacts.json.gz',raw);classified=[]
    for c in raw['contacts']:
        points=[tuple(Fraction(v)for v in p)for p in c['exactPoints']];faces=[rational_face(triangles[i][c[k]])for i,k in enumerate(['sourceFaceA','sourceFaceB'])];classified.append(dict(c,contactRole=contact_role(*faces,points,c['dimension'],c['primitiveDimensions'])))
    save(out/'complete-classified-contacts.json.gz',classified);projections=[shapely.union_all([shapely.MultiPoint(t[:,[0,2]]).convex_hull for t in source])for source in triangles];context=[]
    for i,row in enumerate(rows):
        own,projection=polygons[i],projections[i];context.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],completeSourceFaces=len(triangles[i]),worldBounds=[triangles[i].min((0,1)).tolist(),triangles[i].max((0,1)).tolist()],targetAreaM2=own.area,sourceProjectedAreaM2=projection.area,targetCoveredBySource=own.intersection(projection).area/own.area,sourceOutsideOwnFootprintM2=projection.difference(own).area,sourceOutsideBothFootprintsM2=projection.difference(shapely.union_all(polygons)).area))
    result=dict(uids=[row['uid']for row in rows],rows=context,trianglePairsTested=raw['trianglePairsTested'],completePairExamined=True,contactDimensions=dict(Counter(str(c['dimension'])for c in classified)),contactRoles=dict(Counter(c['contactRole']for c in classified)),sourceGeometryChanges=0,installationApproved=False,qualification='Every exact inclusive-AABB original facet pair examined, with all point/line/area/degenerate contacts and full original footprint coverage retained. Contact roles are geometric descriptions only; no architectural support, related ownership, model acceptance or geometry edits.')
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_primitive_contacts_v1.py','exact_original_shell_intersections_20261009.py','exact_contact_role_context_v1_20261023.py']);module('complete_pair_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch,'complete-exact-original-pair-contact-footprint-context',refs,result);print(result,flush=True)

if __name__=='__main__':main()

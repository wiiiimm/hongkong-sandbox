"""PRIVATE bounded original-TIN return against captured current native terrain.
Reuses the exact V17 source-envelope and 3m return algorithm, but never replaces
its basis with a coarse-parent template. No validator/publisher is modified;
this unapproved diagnostic must pass separate partition and acceptance checks.
"""
import copy
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from rectangular_native_fragments_v1_20261101 import drawn,cut,pack
from coordinated_native_boundary_v1_20261023 import seam_segments,seam_comparison_report
from collections import Counter
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from ronsdale_local_inset_v2_20261022 import plane,lift,parent_fragment_lift
from exact_affine_halfplane_clip_v2_20261030 import lower_region,REPAIR_AUDIT
from affine_terrain_blend_v1 import sector as blend_sector,evaluate as blend_evaluate
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-one-peking-after-twin-';BATCH=P+'three-member-original-return-v1-20261101'
def main():
    doc=BASE/BATCH;assert not doc.exists();prior=P+'private-original-inset-v1-20261101';receipt,pins=authenticate(BASE/prior);refs=[Path(__file__),BASE/prior/'result.json',HERE/'selected_original_local_inset_v17_20261030.py']
    assert digest(refs[-1].read_bytes())==pins[str(refs[-1].relative_to(ROOT))]
    def take(path):
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
    saved_lineage=take(BASE/prior/'lineage.json.gz');core=shapely.from_wkt(saved_lineage['coreWKT']);outer=shapely.from_wkt(saved_lineage['outerWKT']);assert core.buffer(3,join_style='mitre').equals(outer)
    baseline_context=take(HERE/'local'/prior/'parent.json');baseline=np.asarray(baseline_context['triangles']);template=take(ROOT/receipt['candidate']['path'])
    for path,sha in baseline_context['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(manifest.read_bytes());assert msha==pins[str(manifest.relative_to(ROOT))];refs.append(manifest)
    binding=P+'cached-original-terrain-binding-v1-20261101';binding_receipt,binding_pins=authenticate(BASE/binding);refs.append(BASE/binding/'result.json');path=BASE/binding/'summary.json';assert digest(path.read_bytes())==binding_pins[str(path.relative_to(ROOT))];refs.append(path);checked=next(r for r in read(path)['rows']if r['uid']=='landsd/233985:0');assert checked['sourceSHA256']==receipt['sourceSHA256ByUid'][checked['uid']]
    a,b,c,d=outer.bounds;doc.mkdir()
    decoder = module('selected_inset_source', HERE / 'xl-second-pass.py')
    decoder.LOCAL = HERE / 'local' / BATCH
    source, source_refs, source_planes = [], [], []
    for name in checked['sourceTerrainPaths']:
        path = ROOT / name
        metadata = take(path)
        for buffer in metadata.get('buffers', []):
            member = path.parent / buffer['uri']
            assert digest(member.read_bytes()) == pins[str(member.relative_to(ROOT))]
            refs.append(member)
        source_refs.append(dict(path=name, sha256=pins[name]))
        values = decoder.terrain_triangles(path)
        for face in values[(values[:, :, 0].max(1) >= a) & (values[:, :, 0].min(1) <= c) & (values[:, :, 2].max(1) >= b) & (values[:, :, 2].min(1) <= d)]:
            polygon = shapely.Polygon(face[:, [0, 2]])
            if polygon.area > 1e-10:
                # Keep the authored source plane through clipping. Tiny derived
                # triangles can be ill-conditioned for a second plane fit;
                # no clipped primitive or source facet is discarded here.
                coefficients = plane(face)
                parts = lift(polygon.intersection(outer), coefficients)
                source.extend(parts)
                source_planes.extend(coefficients.copy() for _ in parts)
    source = np.asarray(source)
    polygons = shapely.polygons(source[:, :, [0, 2]])
    union = shapely.union_all(polygons)
    assert len(source_planes) == len(source)
    planes = source_planes
    tree = shapely.STRtree(polygons)
    upper, upperlineage = [], []
    for i, polygon in enumerate(polygons):
        cuts = []
        for j in tree.query(polygon, predicate='intersects'):
            if i == j:
                continue
            overlap = polygon.intersection(polygons[j])
            if overlap.area <= 1e-10:
                continue
            if np.array_equal(planes[i], planes[j]):
                if j < i:
                    cuts.append(overlap)
            else:
                cuts.append(lower_region(overlap, planes[j]-planes[i]))
        kept = polygon.difference(shapely.union_all(cuts)) if cuts else polygon
        for face in lift(kept, planes[i]):
            upper.append(face)
            upperlineage.append(i)
    source = np.asarray(upper)
    assert np.array_equal(source, np.asarray(saved_lineage['sourceFaces'])), 'Original highest source terrain changed'
    polygons = shapely.polygons(source[:, :, [0, 2]])
    from exact_local_planar_partition_v1_20261030 import verify as verify_local_partition
    save(doc / 'upper-envelope-local-partition.json', verify_local_partition(polygons, union))
    refs.append(HERE / 'exact_local_planar_partition_v1_20261030.py')
    planes = [planes[i] for i in upperlineage]
    tree = shapely.STRtree(polygons)

    cap=P+'two-leaf-parent-capture-v2-20261101';cr,cp=authenticate(BASE/cap);refs.append(BASE/cap/'result.json');parentpath=ROOT/'3d-viewer/city/data/government-xl-academy69025-nested-original-terrain-20261029.json';assert digest(parentpath.read_bytes())==cp[str(parentpath.relative_to(ROOT))];refs.append(parentpath);parent=read(parentpath);assert len(parent['patches'])==17
    rootbatch=P+'root-grid-classification-v1-20261101';rr,rp=authenticate(BASE/rootbatch);refs.append(BASE/rootbatch/'result.json');rootpath=HERE/'local'/rootbatch/'root-grid.json';assert digest(rootpath.read_bytes())==rp[str(rootpath.relative_to(ROOT))];refs.append(rootpath)
    rootfaces,_=cut(np.asarray(read(rootpath)['triangles']),[1002.5,-1017.5,1092.5,-967.5]);assert rootfaces
    bodies={'retained-12':drawn(parent['patches'][12]),'retained-15':drawn(parent['patches'][15]),'new-root':np.asarray(rootfaces)};members={};outputs={};totalchanged=0;alllineage={}
    def key(face):
        f=[tuple(map(float,p))for p in face];return min(tuple(f[i:]+f[:i])for i in range(3))
    def shape(name,faces):
        if name=='new-root':
            n=copy.deepcopy(template);g=n['meta']['georef'];cell=n['cell'];b=[1002.5,-1017.5,1092.5,-967.5];c0=round((b[0]+834500-g['bE'])/cell);r0=round((b[1]-816500+g['bN'])/cell);w=round((b[2]-b[0])/cell)+1;hh=round((b[3]-b[1])/cell)+1
            for field in ['elev','renderedElev','vegetation']:
                if field in n:n[field]=[x for row in range(r0,r0+hh)for x in template[field][row*template['w']+c0:row*template['w']+c0+w]]
            n.update(w=w,h=hh);n['meta']['georef']={**g,'bE':834500+b[0],'bN':816500-b[1],'W':w,'H':hh};pg=parent['meta']['georef'];n['coarseCells']=[round((b[0]+834500-pg['bE'])/parent['cell']),round((b[1]-816500+pg['bN'])/parent['cell']),round((b[2]+834500-pg['bE'])/parent['cell']),round((b[3]-816500+pg['bN'])/parent['cell'])];n['meta']['targetUids']=receipt['uids']
        else:n=copy.deepcopy(parent['patches'][int(name.split('-')[1])]);n['meta']['targetUids']=sorted(set(n['meta']['targetUids'])|set(receipt['uids']))
        n['id']='private-one-peking-'+name;n['meta']['parentTerrain']=str(parentpath.relative_to(ROOT/'3d-viewer'));n['meta']['parentSha256']=digest(parentpath.read_bytes());positions,indices=pack(faces);n['nativeMesh']={'position':positions,'index':indices,'source':{'policy':'private-exact-current-parent-with-bounded-original-source-return','verticalDatum':'HKPD','verticalScale':1,'privateDiagnosticOnly':True}};return n
    for name,baseline in bodies.items():
        memberdoc=doc/name;memberdoc.mkdir();saved_doc=doc;doc=memberdoc
        sectors = [(core, None)]
        for polygon in shapely.get_parts(shapely.constrained_delaunay_triangles(outer.difference(core))):
            if polygon.geom_type != 'Polygon' or polygon.area <= 0:
                continue
            xz = np.asarray(polygon.exterior.coords[:3])
            weights = []
            for x, z in xz:
                point = shapely.Point(x, z)
                inside, outside = point.distance(core.boundary) < 1e-8, point.distance(outer.boundary) < 1e-8
                assert inside != outside
                weights.append(0. if inside else 1.)
            sectors.append((polygon, blend_sector(xz, weights)))
        output, lineage, changed = [], [], []
        removed = inserted = 0.
        area_cases = []
        for i, face in enumerate(baseline):
            polygon = shapely.Polygon(face[:, [0, 2]])
            if polygon.area <= 1e-10 or not polygon.intersects(outer):
                output.append(face)
                lineage.append(dict(kind='unchanged', parentFace=i))
                continue
            parentplane, cuts, added = plane(face), [], []
            for j in tree.query(polygon, predicate='intersects'):
                intersection = polygon.intersection(polygons[j])
                if intersection.area <= 1e-10:
                    continue
                lower = lower_region(intersection, parentplane-planes[j])
                if lower.area <= 1e-10:
                    continue
                cuts.append(lower)
                for region, weightplane in sectors:
                    for part in lift(lower.intersection(region), planes[j]):
                        if weightplane is not None:
                            weights = blend_evaluate(part[:, [0, 2]], weightplane)
                            oldheight = part[:, [0, 2]] @ parentplane[:2]+parentplane[2]
                            part[:, 1] = part[:, 1]*(1-weights)+oldheight*weights
                        assert part[:, 1].min() >= 1.2, 'new-inset-surface-below-existing-clamp'
                        added.append((part, int(j)))
            if not cuts:
                output.append(face)
                lineage.append(dict(kind='unchanged', parentFace=i))
                continue
            cut = shapely.union_all(cuts)
            local_inserted = sum(shapely.Polygon(part[:, [0, 2]]).area for part, _ in added)
            if abs(cut.area-local_inserted) > 1e-9:
                area_cases.append(dict(parentFace=i, removedAreaM2=cut.area, insertedAreaM2=local_inserted, signedDifferenceM2=cut.area-local_inserted, parentTriangle=face.tolist(), cutWKT=cut.wkt, insertedTriangles=[part.tolist() for part, _ in added], sourceFaceIds=[j for _, j in added]))
            removed += cut.area
            changed.append(i)
            for part in parent_fragment_lift(polygon.difference(cut), parentplane):
                output.append(part)
                lineage.append(dict(kind='parent-fragment', parentFace=i))
            for part, j in added:
                output.append(part)
                lineage.append(dict(kind='original-inset-or-return', parentFace=i, sourceFace=j))
                inserted += shapely.Polygon(part[:, [0, 2]]).area
        save(doc / 'area-conservation-diagnostic.json.gz', dict(removedAreaM2=removed, insertedAreaM2=inserted, signedDifferenceM2=removed-inserted, existingLimitM2=1e-6, allLocalDiscrepanciesAboveOneBillionthM2=area_cases, toleranceChanged=False, installationApproved=False))
        assert abs(removed-inserted) < 1e-6
        output = np.asarray(output)


        doc=saved_doc;candidate=shape(name,output);before=shape(name,baseline);path=doc/(name+'-after.json');bp=doc/(name+'-before.json');save(path,candidate);save(bp,before);refs.extend([path,bp]);outputs[name]=drawn(candidate);totalchanged+=len(changed)
        # Every untouched source face survives with effective Float32 winding/multiplicity.
        raw_unchanged=[baseline[r['parentFace']]for r in lineage if r['kind']=='unchanged'];actual=drawn(candidate);unchanged=actual[[i for i,r in enumerate(lineage)if r['kind']=='unchanged']];assert Counter(key(f)for f in raw_unchanged)==Counter(key(f)for f in unchanged)
        alllineage[name]=dict(outputLineage=lineage,changedParentFaces=changed,coreWKT=core.wkt,outerWKT=outer.wkt)
        members[name]=dict(before={'path':str(bp.relative_to(ROOT)),'sha256':digest(bp.read_bytes())},candidate={'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())},beforeFaces=len(baseline),afterFaces=len(output),changedParentFaces=len(changed),unchangedParentFaces=len(raw_unchanged),unchangedFloat32WindingMultiplicityVerified=True,removedAreaM2=removed,insertedAreaM2=inserted)
    seams=[]
    for names,axis,c,lo,hi in [(['retained-12','retained-15'],2,-967.5,852.5,1002.5),(['retained-12','new-root'],2,-967.5,1002.5,1092.5),(['retained-15','new-root'],0,1002.5,-1017.5,-967.5)]:
        try:report=seam_comparison_report(*(seam_segments(outputs[n],axis,c,lo,hi)for n in names),lo,hi)
        except AssertionError as error:report={'passed':False,'error':str(error)}
        seams.append(dict(members=names,axis=axis,coordinate=c,lower=lo,upper=hi,report=report))
    assert digest(manifest.read_bytes())==msha
    save(doc/'lineage.json.gz',alllineage);save(doc/'source-upper-planes.json.gz',dict(sourceFaces=source.tolist(),originalPlanes=[p.tolist()for p in planes]))
    result=dict(uids=receipt['uids'],currentManifestSHA256=msha,parentURL=str(parentpath.relative_to(ROOT/'3d-viewer')),parentSHA256=digest(parentpath.read_bytes()),members=members,seams=seams,allFiniteSeamsPassed=all(r['report']['passed']for r in seams),changedParentFaces=totalchanged,boundedClipRepairs=list(REPAIR_AUDIT),sourceGeometryChanges=0,buildingGeometryChanges=0,sourcePoseChanges=0,canonicalTerrainValidationPassed=False,physicalAcceptance=False,publication=False,installationApproved=False,nextAction='Independent complete three-member retention, coverage, boundary, runtime and affected actor checks, then original source and browser qualification. No current public terrain changed.')
    save(doc/'summary.json',result);refs.extend(HERE/n for n in ['rectangular_native_fragments_v1_20261101.py','coordinated_native_boundary_v1_20261023.py','ronsdale_local_inset_v2_20261022.py','exact_affine_halfplane_clip_v2_20261030.py','affine_terrain_blend_v1.py','exact_local_planar_partition_v1_20261030.py','xl-second-pass.py'])
    module('one_peking_three_member_return_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-two-full-retained-leaves-and-bounded-new-root-original-return',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()

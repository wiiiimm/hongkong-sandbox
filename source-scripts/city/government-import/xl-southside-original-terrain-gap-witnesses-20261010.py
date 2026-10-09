"""Prove missing original terrain points without costly full polygon subtraction."""
import numpy as np,shapely
from run import ROOT,read,save,digest
from exact_original_projection_coverage_20261009 import point,cross,signed_area
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
SOURCE=ROOT/'docs/astra-city/government-import/government-xl-southside-station-original-pair-source-tin-context-20261010'
INPUT=ROOT/'docs/astra-city/government-import/government-xl-southside-current-bound-source-inputs-20261010'
DOC=ROOT/'docs/astra-city/government-import/government-xl-southside-original-terrain-gap-witnesses-20261010'
def contains(triangle,p):
    t=[point(v) for v in triangle];s=signed_area(t)
    if s==0:return False
    if s<0:t.reverse()
    return all(cross(a,b,p)>=0 for a,b in zip(t,t[1:]+t[:1]))
def main():
    assert not DOC.exists();x=read(SOURCE/'complete-original-source-tin.json.gz');g=np.asarray(x['position'],float).reshape(-1,3)[np.asarray(x['index']).reshape(-1,3)];assert digest(g.astype('<f8').tobytes())==x['worldTriangleSHA256']
    cap=read(INPUT/'current-inputs.json.gz');row=read(INPUT/'selection.json.gz')['rows'][0];t=np.concatenate([decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes()),decode_original_world_triangles((ROOT/cap['relatedOriginalPath']).read_bytes())]);gxz=g[:,:,[0,2]];polygons=shapely.polygons(gxz);tree=shapely.STRtree(polygons);records=[]
    for raw in read(SOURCE/'diagnostic.json.gz')['allOriginalPairFaceContexts']:
        if raw['groundProjectionCovered']:continue
        i=raw['sourceFace'];face=t[i][:,[0,2]];poly=shapely.Polygon(face);candidate=tree.query(poly,predicate='intersects');missing=poly.difference(shapely.union_all(polygons[candidate]));witnesses=[]
        for part in shapely.get_parts(missing):
            probes=[part.representative_point(),part.centroid]
            for probe in probes:
                if probe.is_empty:continue
                p=point([probe.x,probe.y]);inside=contains(face,p)
                hit=np.flatnonzero(np.all(gxz.max(axis=1)>=np.asarray([probe.x,probe.y]),axis=1)&np.all(gxz.min(axis=1)<=np.asarray([probe.x,probe.y]),axis=1));covering=[int(j) for j in hit if contains(gxz[j],p)]
                if inside and not covering:witnesses.append({'pointXZ':[probe.x,probe.y],'pointExactFractions':list(map(str,p)),'insideExactOriginalFace':True,'outsideEveryExactOriginalTerrainFacet':True,'allGroundFacesAccounted':len(g),'candidateGroundFacetIds':list(map(int,hit))})
        result={'sourceFace':i,'sourceFaceVertices':t[i].tolist(),'rawMissingFace':raw,'exactUncoveredPointWitnesses':witnesses,'genuineMissingOriginalTerrain':bool(witnesses),'otherwise':'full-finite-coverage-still-unresolved' if not witnesses else None};records.append(result);save(DOC/'progress.json.gz',{'rows':records,'complete':False});print({'sourceFace':i,'witnesses':len(witnesses),'geosMissingAreaM2DiagnosticOnly':float(missing.area)},flush=True)
    save(DOC/'result.json.gz',{'rows':records,'rawMissingFaces':len(records),'genuineMissingFaces':sum(bool(r['exactUncoveredPointWitnesses']) for r in records),'completeOriginalTerrainFaces':len(g),'completeOriginalSourceFaces':len(t),'sourceWorldSHA256':digest(t.astype('<f8').tobytes()),'groundWorldSHA256':digest(g.astype('<f8').tobytes()),'inputHashes':{str((SOURCE/'diagnostic.json.gz').relative_to(ROOT)):digest((SOURCE/'diagnostic.json.gz').read_bytes()),str((SOURCE/'complete-original-source-tin.json.gz').relative_to(ROOT)):digest((SOURCE/'complete-original-source-tin.json.gz').read_bytes())},'physicalAccepted':False,'noToleranceCredit':True,'qualification':'GEOS is only a witness proposal. Fraction finite-face containment and absence from every exact nonzero original ground facet proves each recorded missing point. No-witness cases receive zero coverage credit; no original geometry changed.'})
if __name__=='__main__':main()

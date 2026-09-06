"""Resample only actual source TIN triangles onto the existing city 5 m lattice.
Absent source coverage is null, never interpolated across gaps or extrapolated.
"""
import hashlib,json,pathlib
import numpy as np
import shapely
from shapely import STRtree
from bake_model_geometry import decode
from prepare_model_sample import model_geometry
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[3];ASSETS=HERE/'model-sample'


def main():
    manifest=json.loads((ASSETS/'manifest.json').read_text());spec=manifest['terrain'];path=ASSETS/spec['url'];data=json.loads(path.read_text())
    # This retained terrain contains one triangle primitive; fail on a new source layout.
    assert len(data['meshes'])==1 and len(data['meshes'][0]['primitives'])==1
    primitive=data['meshes'][0]['primitives'][0]
    positions,count=model_geometry(data,lambda uri:(path.parent/uri).read_bytes())
    indices=decode(data,primitive['indices'],path.parent).reshape(-1) if 'indices' in primitive else np.arange(len(positions))
    triangles=positions[indices].reshape(-1,3,3);assert len(triangles)==count
    footprints=shapely.polygons(triangles[:,:,[0,2]])
    areas=shapely.area(footprints);valid_triangles=areas>1e-12
    usable=triangles[valid_triangles];tree=STRtree(footprints[valid_triangles])
    base_georef={'aE':5,'bE':815712.5,'aN':-5,'bN':816467.5}
    bounds=spec['worldBounds'];g=base_georef
    c0=int(np.ceil((bounds[0][0]+834500-g['bE'])/g['aE']));c1=int(np.floor((bounds[1][0]+834500-g['bE'])/g['aE']))
    r0=int(np.ceil((816500-bounds[0][2]-g['bN'])/g['aN']));r1=int(np.floor((816500-bounds[1][2]-g['bN'])/g['aN']))
    w=c1-c0+1;h=r1-r0+1
    xs=g['bE']+np.arange(c0,c1+1)*g['aE']-834500;zs=816500-(g['bN']+np.arange(r0,r1+1)*g['aN']);xx,zz=np.meshgrid(xs,zs)
    points=np.c_[xx.reshape(-1),zz.reshape(-1)];pi,ti=tree.query(shapely.points(points),predicate='covered_by')
    abc=usable[ti];v0=abc[:,1,:][:,[0,2]]-abc[:,0,:][:,[0,2]];v1=abc[:,2,:][:,[0,2]]-abc[:,0,:][:,[0,2]];v2=points[pi]-abc[:,0,:][:,[0,2]]
    den=v0[:,0]*v1[:,1]-v0[:,1]*v1[:,0]
    u=(v2[:,0]*v1[:,1]-v2[:,1]*v1[:,0])/den;v=(v0[:,0]*v2[:,1]-v0[:,1]*v2[:,0])/den
    heights=abc[:,0,1]+u*(abc[:,1,1]-abc[:,0,1])+v*(abc[:,2,1]-abc[:,0,1])
    # Shared triangle edges may produce two equivalent hits. Retain the uppermost surface if source overlaps.
    elev=np.full(len(points),-np.inf);np.maximum.at(elev,pi,heights);valid=np.isfinite(elev)
    grid_bounds=[float(xs[0]),float(zs[0]),float(xs[-1]),float(zs[-1])]
    payload={'schemaVersion':1,'w':w,'h':h,'elev':[float(x) if ok else None for x,ok in zip(elev,valid)],
      'valid':valid.tolist(),'meta':{'georef':{**g,'bE':g['bE']+c0*g['aE'],'bN':g['bN']+r0*g['aN']}},
      'source':{'provider':'Lands Department, Hong Kong SAR Government','datasetId':manifest['datasetId'],
        'tile':manifest['tile'],'tileRevision':manifest['tileRevision'],'archiveSha256':manifest['sourceArchiveSha256'],
        'gltf':spec['sourceEntry'],'sourceHashes':spec['sourceHashes'],'metadataUrl':'https://portal.csdi.gov.hk/csdi-webpage/metadata/landsd_rcd_1742809441342_98380/html'},
      'bounds':grid_bounds,'sourceTerrainBounds':spec['worldBounds'],'origin':[834500,816500],'crs':'EPSG:2326','verticalDatum':'Hong Kong Principal Datum',
      'cityGrid':{'georef':g,'cropIndicesInclusive':[c0,r0,c1,r1]},
      'method':'Exact glTF node transforms followed by source TIN barycentric interpolation at existing 5 m city grid nodes. Only triangles whose projected footprint covers the sample contribute. Maximum height is retained when multiple source triangles overlap; missing coverage remains null. No fill, height offset, simplification, or artificial shoreline. A subsequently rendered grid is a resampling and does not reproduce every source TIN edge.',
      'counts':{'sourceTriangles':len(triangles),'nonDegenerateProjectedTriangles':int(valid_triangles.sum()),'gridNodes':len(points),'coveredGridNodes':int(valid.sum()),'missingGridNodes':int((~valid).sum()),'multipleTriangleNodes':int((np.bincount(pi,minlength=len(points))>1).sum())}}
    raw=json.dumps(payload,separators=(',',':'),allow_nan=False).encode();out=ASSETS/'terrain-source-5m.json';out.write_bytes(raw)
    proof_path=HERE/'model-browser-proof.json';proof=json.loads(proof_path.read_text()) if proof_path.exists() else None
    comparison=[]
    if proof:
        # Direct source TIN consistency at independent browser raycast points.
        for row in proof['audit']:
            if row['sourceGround'] is None:continue
            box=np.array(row['actualBounds']);point=box.mean(axis=0)[[0,2]];candidates=tree.query(shapely.Point(point),predicate='covered_by')
            source_values=[]
            for index in candidates:
                tri=usable[index];bary=np.linalg.solve((tri[1:,:][:,[0,2]]-tri[0,[0,2]]).T,point-tri[0,[0,2]])
                source_values.append(float(tri[0,1]+bary[0]*(tri[1,1]-tri[0,1])+bary[1]*(tri[2,1]-tri[0,1])))
            if source_values:comparison.append(abs(max(source_values)-row['sourceGround']))
    summary={'file':out.name,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'w':w,'h':h,'bounds':grid_bounds,'georef':payload['meta']['georef'],'cityGridCrop':payload['cityGrid']['cropIndicesInclusive'],**payload['counts'],
      'minimumHKPD':float(elev[valid].min()),'maximumHKPD':float(elev[valid].max()),'browserTINCrossChecks':len(comparison),'maximumBrowserTINHeightDifference':max(comparison) if comparison else None}
    assert not comparison or max(comparison)<1e-6
    (HERE/'model-terrain-resample.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()

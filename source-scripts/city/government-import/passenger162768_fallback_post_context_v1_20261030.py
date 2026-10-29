"""Measure existing surveyed post clearance from the local buried-roof target."""
from pathlib import Path
import subprocess
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
P='government-xl-passenger162768-after-civic-five-'
BATCH=P+'fallback-post-context-v1-20261030'

def main():
    base=ROOT/'docs/astra-city/government-import';doc=base/BATCH;assert not doc.exists()
    refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:
            pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        path=base/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    forms=take(P+'source-scope-v1-20261030','162768:0-forms.json.gz')
    b=next(r['building'] for r in forms if r['building']['uid']=='landsd/161745:0')
    source=take(P+'buried-context-v1-20261030','162768:0.json')
    upward=[r for r in source['buriedFaces'] if r['upward']]
    assert [r['faceIndex'] for r in upward]==[461,540,541,574,575]
    projection=shapely.union_all([shapely.Polygon(np.asarray(r['vertices'])[:,[0,2]]) for r in upward])
    core=projection.buffer(1,join_style='mitre');outer=core.buffer(3,join_style='mitre')
    save(doc/'input.json',dict(expectedUid=b['uid'],building=b))
    tool=HERE/'basic_form_parts_context_v1_20261030.mjs';refs.append(tool)
    subprocess.run(['node',str(tool),str((doc/'input.json').relative_to(ROOT)),str((doc/'parts.json').relative_to(ROOT))],cwd=ROOT,check=True)
    parts=read(doc/'parts.json');assert parts['description']['openSided']
    for path,sha in parts['inputHashes'].items():
        assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    rows=[]
    for i,part in enumerate(parts['description']['parts']):
        if part['kind']!='post':continue
        footprint=shapely.Polygon(part['rings'][0],part['rings'][1:])
        rows.append(dict(partIndex=i,bottom=part['bottom'],top=part['top'],footprintWKT=footprint.wkt,sourceUpwardDistanceM=footprint.distance(projection),insideSourceUpwardM2=footprint.intersection(projection).area,insideCoreM2=footprint.intersection(core).area,insideReturnM2=footprint.intersection(outer).area))
    assert rows
    result=dict(uids=['landsd/162768:0',b['uid']],sourceSHA256=source['sourceSHA256'],rows=rows,sourceGeometryChanges=0,terrainEdits=False,installationApproved=False,qualification='Unchanged production surveyed BASIC post footprints versus the five exact original upward facets that caused the terrain inset. Distances and overlap only; no post extension, terrain correction or support acceptance.')
    save(doc/'summary.json',result)
    module('passenger_fallback_posts_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'surveyed-basic-fallback-post-versus-original-upward-domain',refs,result)
    print([(r['partIndex'],r['sourceUpwardDistanceM'],r['insideCoreM2'],r['insideReturnM2']) for r in rows])

if __name__=='__main__':main()

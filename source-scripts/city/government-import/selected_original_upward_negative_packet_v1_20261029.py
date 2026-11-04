"""Nominate explicit upward original facets proven negative in all four worlds.

This supplies unchanged vertices to the existing private terrain-return tool.
Winding and measured clearance nominate geometry, not architectural function.
"""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

def main():
    p=argparse.ArgumentParser()
    for key in ['batch','runtime','low-faces','uid']:p.add_argument('--'+key,required=True)
    p.add_argument('--face',type=int,action='append',required=True);a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch and 0<len(a.face)==len(set(a.face))<=50
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    source=next(r for r in take(a.runtime,base/a.runtime/'selection.json.gz')['rows']if r['uid']==a.uid);low=take(a.low_faces,base/a.low_faces/'summary.json');assert low['sourceSHA256']==source['sourceSHA256']and low['uids']==[a.uid]and len(low['rows'])==4
    assert all(set(a.face)<=set(r['exactAffectedFaces'])for r in low['rows'])
    path=ROOT/source['candidate']['path'];assert digest(path.read_bytes())==source['sourceSHA256'];refs.append(path);triangles=decode_original_world_triangles(path.read_bytes());rows=[]
    for face in sorted(a.face):
        assert 0<=face<len(triangles);t=triangles[face];normal=np.cross(t[1]-t[0],t[2]-t[0]);length=float(np.linalg.norm(normal));assert length>0 and normal[1]>.25*length
        rows.append(dict(face=face,vertices=t.tolist(),normalYRatio=float(normal[1]/length),areaM2=length/2))
    result=dict(uids=[a.uid],sourceSHA256=source['sourceSHA256'],completeSourceFaces=len(triangles),rows=rows,allNominatedFacetsUpwardAndFourWorldNegative=True,architectureReview=False,physicalAcceptance=False,installationApproved=False,sourceGeometryChanges=0,qualification='Explicit unchanged source facets with positive upward normals and authenticated complete-ground negative intersection in every coordinate representation. Private terrain-return input only; no architectural-role, geometry edit, burial waiver or installation approval.')
    save(out/'summary.json',result);refs.append(HERE/'exact_packed_world_geometry_20261009.py')
    module('upward_negative_packet_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'explicit-exact-original-upward-negative-facet-nomination',refs,result)

if __name__=='__main__':main()

"""Measure exact original horizontal caps; diagnostics, never an acceptance waiver."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
SRC=BASE/'government-xl-citywalk-current294-face-descriptors-v1-20261015'
BATCH='government-xl-citywalk-horizontal-caps-context-v1-20261015'
DOC=BASE/BATCH

def main():
    receipt=read(SRC/'result.json')
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
    rows=[]
    for row in read(SRC/'descriptors.json.gz')['rows']:
        for face in row['faces']:
            if face['heightSpan'] != 0: continue
            v=np.asarray(face['sourceVertices'],dtype=float)
            cross=np.cross(v[1]-v[0],v[2]-v[0])
            rows.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],originalFaceID=face['originalFaceID'],vertices=face['sourceVertices'],areaM2=float(np.linalg.norm(cross)/2),normalY=face['normalY'],centroid=v.mean(axis=0).tolist(),sourceRoleApproved=False))
    assert len(rows)==3
    DOC.mkdir(exist_ok=False)
    save(DOC/'caps.json',dict(rows=rows,acceptance=False,interpretation='Three horizontal source caps remain explicitly included. Small area is not grounds for dismissal. Review authored podium intersections and visible/collision context before acceptance.'))
    module('cap_context_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-horizontal-cap-context-v1',[Path(__file__),SRC/'result.json',SRC/'descriptors.json.gz'],dict(uids=['landsd/134332:0'],horizontalCaps=len(rows),fullAcceptance=False,nextStep='Resolve original podium junction roles, preserving all three horizontal caps and the failed contact results.'))
    print({'horizontalCaps':len(rows),'installed':0})
if __name__=='__main__':main()

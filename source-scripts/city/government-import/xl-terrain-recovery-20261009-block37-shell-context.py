"""Exact rational self-intersections for every original buried Block37 shell."""
import json
import numpy as np
from run import ROOT,read,save,reservations
from exact_original_shell_intersections_20261009 import shell_self_intersections


def main():
    lease=read('/tmp/xl-terrain-recovery-20261009-228547-lease.json')
    assert reservations.heartbeat(lease)['ok']
    row=next(r for r in read(ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-shell-cohort/diagnostic.json.gz')['rows'] if r['uid']=='landsd/228547:0')
    g=read(ROOT/row['runtimeGeometry'])['rows'][0]
    assert g['sourceSHA256']==row['sourceSHA256']
    tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
    shells=[]
    for i,shell in enumerate(row['shells']):
        assert shell['triangles']==92 and shell['outwardPositiveVolume']
        proof=shell_self_intersections(tri[shell['componentFaces']].tolist())
        proof.update(shellIndex=i,originalSourceFaces=shell['componentFaces'])
        shells.append(proof);assert reservations.heartbeat(lease)['ok']
        print(json.dumps({'shell':i,'faces':92,'selfIntersectionFree':proof['selfIntersectionFree']}),flush=True)
    result={'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'wholeSourceFaces':len(tri),
        'originalBuriedComponentFaces':sum(s['triangles'] for s in row['shells']),
        'allBuriedComponentsExamined':True,'shells':shells,
        'allSelfIntersectionFree':all(s['selfIntersectionFree'] for s in shells),
        'sourceGeometryChanges':0,'installationApproved':False,'newlyInstalled':0,
        'publication':False,'providerBelowGradeAuthorisation':False}
    output=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-block37-wall-context/shell-self-intersections.json.gz'
    assert not output.exists(),'Fresh immutable source proof required'
    save(output,result)


if __name__=='__main__':main()

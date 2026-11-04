"""Locate failed private seams against exact current source geometry; no admission."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from rectangular_native_fragments_v1_20261101 import drawn
from coordinated_native_boundary_v1_20261023 import seam_segments,seam_comparison_report
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-one-peking-after-twin-';BATCH=P+'fragment-seam-audit-v1-20261101'
def intervals(segments,lo,hi):
    pieces=sorted((max(float(a),lo),min(float(b),hi))for a,b,*_ in segments if b>=lo and a<=hi)
    cursor=lo;gaps=[]
    for a,b in pieces:
        if a>cursor:gaps.append([cursor,a])
        cursor=max(cursor,b)
    if cursor<hi:gaps.append([cursor,hi])
    return gaps

def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];batch=P+'private-fragment-set-v2-20261101';receipt,pins=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
    def take(path):
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
    summary=take(BASE/batch/'summary.json');seams=take(BASE/batch/'seams.json')['rows'];meshes={}
    for name,m in summary['members'].items():
        meshes[name]={kind:drawn(take(ROOT/m[kind]['path']))for kind in ['before','candidate']}
    rows=[]
    for seam in seams:
        a,b=seam['members'];axis,c,lo,hi=[seam[k]for k in ['axis','coordinate','lower','upper']];row=dict(members=[a,b],axis=axis,coordinate=c,lower=lo,upper=hi)
        for kind in ['before','candidate']:
            left=seam_segments(meshes[a][kind],axis,c,lo,hi);right=seam_segments(meshes[b][kind],axis,c,lo,hi)
            try:report=seam_comparison_report(left,right,lo,hi)
            except AssertionError as error:report=dict(passed=False,error=str(error),leftUncoveredIntervals=intervals(left,lo,hi),rightUncoveredIntervals=intervals(right,lo,hi))
            row[kind]=report
        rows.append(row)
    result=dict(uids=receipt['uids'],rows=rows,currentManifestSHA256=summary['currentManifestSHA256'],sourceGeometryChanges=0,publication=False,physicalAcceptance=False,installationApproved=False,nextAction='Rebuild the bounded original-source return against exact current captured terrain instead of the standalone coarse-parent template. Preserve the standalone failed candidate and all original thresholds. Investigate pre-existing versus clipping seam gaps separately; no installation until full partition contract and current checks pass.')
    save(out/'summary.json',result);refs.extend([HERE/'rectangular_native_fragments_v1_20261101.py',HERE/'coordinated_native_boundary_v1_20261023.py']);module('one_peking_seam_audit_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-current-versus-private-fragment-finite-seam-audit',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()

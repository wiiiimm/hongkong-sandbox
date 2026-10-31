"""Bind original attachment paths to every exact current canonical rim warning.

Reuse only authenticated unchanged actual-ground roots. No rounded witness
matching, source edits, role/physical approval, or publication.
"""
import argparse,sys,uuid
from pathlib import Path
from fractions import Fraction
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_assembly_four_world_pair_context_v3_20261101 import represented
from original_wall_rim_accounting_20261009 import original_samples
from original_face_attachment_minimax_v2_20261024 import attachment_paths

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--plan',required=True);ap.add_argument('--owned',action='store_true');a=ap.parse_args()
    base=ROOT/'docs/astra-city/government-import';pp=(ROOT/a.plan).resolve();assert pp.is_relative_to(base);plan=read(pp);batch=plan['batch'];assert batch.startswith('government-xl-')and'/'not in batch
    out=base/batch;lp=HERE/'local'/batch/'reservation.json';uids=set(plan['uids']);assert len(uids)==len(plan['uids'])and set(plan['rimsByUid'])==uids
    required={'building:'+u for u in uids}|{'terrain:city/data/terrain.json'};assert required<=set(plan['resources'])
    if not a.owned:
        assert not out.exists()and not lp.parent.exists();c=reservations.claim('exact-canonical-ground-paths-'+str(uuid.uuid4()),plan['resources'],batch=batch,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--plan',a.plan,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(plan['resources'])and not out.exists();refs=[Path(__file__),pp];pins={};direct={}
    def take(batch,path):
        if batch not in pins:_,pins[batch]=authenticate(base/batch);refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);direct[str(path.relative_to(ROOT))]=digest(path.read_bytes());return read(path)
    rt=plan['runtime'];at=plan['attributes'];prior=plan['priorPaths'];selection=take(rt,base/rt/'selection.json.gz');geometry={r['uid']:r for r in take(rt,HERE/'local'/rt/'runtime-geometry.json.gz')['rows']};attrs=take(at,base/at/'attributes.json.gz');assert attrs['startEndAllInputsVerified'];attrs={r['uid']:r for r in attrs['rows']}
    oldsummary=take(prior,base/prior/'summary.json');assert set(oldsummary['uids'])==uids
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest);direct[str(manifest.relative_to(ROOT))]=digest(manifest.read_bytes());rows=[];out.mkdir()
    for source in selection['rows']:
        uid=source['uid']
        if uid not in uids:continue
        asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256']==geometry[uid]['sourceSHA256']==attrs[uid]['sourceSHA256'];refs.append(asset);direct[str(asset.relative_to(ROOT))]=digest(asset.read_bytes())
        attr=attrs[uid];ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3);worlds=represented(attr,decode_original_world_triangles(asset.read_bytes()));literal=np.asarray(attr['completeLiteralWorldPosition'],dtype='<f8').reshape(-1,3);assert len(set(ix.ravel()))==len(literal)
        positions=dict(literal=literal,leftF32=np.asarray(attr['completeExplicitLeftAssociatedFloat32WorldPosition'],dtype='<f8').reshape(-1,3),balancedF32=np.asarray(attr['completeExplicitBalancedFloat32WorldPosition'],dtype='<f8').reshape(-1,3));positions['original']=literal.copy();positions['original'][ix.ravel()]=worlds['original'].reshape(-1,3)
        ground=np.asarray(geometry[uid]['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);gsha=digest(ground.tobytes());rim=plan['rimsByUid'][uid]
        for mode,tri in worlds.items():
            assert reservations.owns(lease)and np.array_equal(positions[mode][ix],tri);sha=digest(tri.astype('<f8').tobytes());raw=take(rim,base/rim/(mode+'.json.gz'));old=take(prior,base/prior/uid.split('/')[1]/mode/'paths.json.gz');assert raw['sourceWorldSHA256']==old['sourceWorldSHA256']==sha and raw['groundSHA256']==old['completeDrawnGroundSHA256']==gsha
            expected=original_samples(positions[mode],ix,float(positions[mode][:,1].min()));actual=raw['completeOriginalSamples'];assert len(actual)==len(expected)==raw['samples']
            for r,e in zip(actual,expected):assert all(r[k]==v for k,v in e.items())and r['gap']==r['point'][1]-r['ground']
            bad=[(i,r)for i,r in enumerate(actual)if r['low']and(r['gap']<-.5 or r['gap']>1)];assert [{k:v for k,v in r.items()if k!='low'}for _,r in bad]==raw['rawRimFailures']
            roots=old['canonicalStrictRoots'];verified={r['sampleIndex']:r for r in old['independentRootReplay']if r['accepted']};assert len(roots)==old['independentlyVerifiedStrictRootCount']and roots
            for root in roots:
                proof=verified[root['sampleIndex']];gap=min(Fraction(r['proof']['exactMinimumFiniteColumnGapM'])for r in proof['proofs']);assert gap==Fraction(proof['exactMinimumGapM'])and Fraction(-1,10)<=gap<=1
            real=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)>0;targets=[];zero=[]
            for i,r in bad:
                incident=[int(f)for f in r['originalIncidentFaces']if real[f]];w=dict(position=r['point'],sampleIndex=i,kind=r['kind'],rawGroundGapM=r['gap'],originalIncidentFaces=r['originalIncidentFaces'])
                if not incident:zero.append(w);continue
                targets.append(dict(witness=w,incidentFaces=incident))
            paths=attachment_paths(tri,dict(targets=targets,proof=dict(contacts=[])),[],strict_anchors=roots);assert [r['witness']for r in paths]==[t['witness']for t in targets]
            passed=all(r['hasUnrestrictedFiniteAttachment']and r['passesExistingEndpointHeight']and r['riseAboveEndpointsM']==0 and r['maximumResidualM']<=.001 for r in paths)
            doc=dict(uid=uid,mode=mode,sourceWorldSHA256=sha,completeGroundSHA256=gsha,wholeOriginalSamples=len(actual),completeRawCanonicalWarningIndices=[i for i,_ in bad],nonrenderingOnlyWarnings=zero,canonicalStrictRoots=roots,rows=paths,everyRenderingCanonicalWarningAccounted=len(paths)+len(zero)==len(bad),allRenderingCanonicalWarningPathsPass=passed,physicalAcceptance=False)
            save(out/uid.split('/')[1]/(mode+'.json.gz'),doc);rows.append(dict(uid=uid,mode=mode,sourceSHA256=source['sourceSHA256'],canonicalWarnings=len(bad),renderingWarnings=len(paths),nonrenderingOnlyWarnings=len(zero),pathsPassed=passed,sourceWorldSHA256=sha,completeGroundSHA256=gsha));print(rows[-1],flush=True)
    assert {r['uid']for r in rows}==uids and len(rows)==4*len(uids)and reservations.owns(lease)
    for name,h in direct.items():assert digest((ROOT/name).read_bytes())==h
    refs.extend(HERE/n for n in ['original_wall_rim_accounting_20261009.py','original_face_attachment_minimax_v2_20261024.py','exact_packed_world_geometry_20261009.py','original_assembly_four_world_pair_context_v3_20261101.py'])
    summary=dict(uids=plan['uids'],rows=rows,allCanonicalRenderingWarningsHavePaths=all(r['pathsPassed']for r in rows),noRoundedWitnessMatching=True,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification=__doc__+' Full current original sample inventory and ordered raw warning indices independently reproduced. Each warning uses its actual incident source faces and exact current position; strict roots, source/ground arrays, original endpoint ceiling and .001m incidence limits remain unchanged. Zero-area-only warnings are retained separately and receive no path/root credit.')
    save(out/'summary.json',summary);module('exact_canonical_ground_paths_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-current-original-canonical-rim-ground-root-path-context',refs,summary)

if __name__=='__main__':main()

"""Trace original elevated rim probes to already measured strict ground roots."""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_face_attachment_minimax_v2_20261024 import attachment_paths


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','attributes','diagnostic','uid']:p.add_argument('--'+k,required=True)
    a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert a.batch.startswith('government-xl-')and'/'not in a.batch and not out.exists()
    refs=[Path(__file__)];pins={}
    def take(n,path):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        assert digest(path.read_bytes())==pins[n][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    source=next(r for r in take(a.runtime,base/a.runtime/'selection.json.gz')['rows']if r['uid']==a.uid)
    g=next(r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']if r['uid']==a.uid)
    attr=next(r for r in take(a.attributes,base/a.attributes/'attributes.json.gz')['rows']if r['uid']==a.uid)
    asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256']==attr['sourceSHA256']==g['sourceSHA256'];refs.append(asset)
    ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
    worlds={'original':decode_original_world_triangles(asset.read_bytes()),**{m:np.asarray(attr[k]).reshape(-1,3)[ix]for m,k in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]}}
    ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);rows=[]
    for mode,tri in worlds.items():
        d=take(a.diagnostic,base/a.diagnostic/(mode+'.json.gz'))
        assert d['sourceSHA256']==source['sourceSHA256'] and d['sourceWorldSHA256']==digest(tri.astype('<f8').tobytes())
        assert d['completeDrawnGroundSHA256']==digest(ground.tobytes())
        roots=[dict(position=r['point'],supportHeight=r['ground'],gap=r['gap'],incidentFaces=r['originalIncidentFaces'],strictAccepted=True)for r in d['completeOriginalSamples']if r['low']and-.1<=r['gap']<=.1]
        targets=[dict(witness=dict(position=r['point'],gap=r['gap'],kind=r['kind']),incidentFaces=r['originalIncidentFaces'])for r in d['failedSamplesVerbatim']]
        assert roots and targets and all(r['witness']['gap']>1 for r in targets)
        paths=attachment_paths(tri,dict(proof=dict(contacts=[]),targets=targets),[],strict_anchors=roots)
        assert len(paths)==len(targets)
        save(out/(mode+'.json.gz'),dict(sourceWorldSHA256=d['sourceWorldSHA256'],completeDrawnGroundSHA256=d['completeDrawnGroundSHA256'],strictGroundRoots=roots,originalSourcePaths=paths,canonicalDirectRimFailuresPreserved=targets))
        row=dict(mode=mode,strictGroundRoots=len(roots),targets=len(targets),finitePaths=sum(r['hasUnrestrictedFiniteAttachment']for r in paths),endpointCeilingPassed=sum(r.get('passesExistingEndpointHeight',False)for r in paths),supportApproved=False)
        rows.append(row);print(row,flush=True)
    result=dict(uids=[a.uid],sourceSHA256=source['sourceSHA256'],rows=rows,
                allTargetsHaveFiniteEndpointBoundedPaths=all(r['targets']==r['finitePaths']==r['endpointCeilingPassed']for r in rows),
                sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,
                qualification='Uses authenticated canonical sample/ground evidence and existing strict[-.1,.1] root samples. Exact shared original edges only; no source-coordinate edits, tolerance joins, inter-actor roof dependency or direct-rim failure removal. Finite paths are source-role context, not engineering/physical/publication approval.')
    save(out/'summary.json',result)
    refs += [HERE/'original_face_attachment_minimax_v2_20261024.py',HERE/'pool_incident_wall_contacts_v1_20261017.py',HERE/'exact_packed_world_geometry_20261009.py']
    module('original_ground_rim_paths_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'original-elevated-rim-to-strict-ground-root-path-context',refs,result)


if __name__=='__main__':main()

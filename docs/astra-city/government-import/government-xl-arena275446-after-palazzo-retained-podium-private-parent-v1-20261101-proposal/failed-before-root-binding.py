"""Capture the existing corrected private podium terrain as a composition parent.

Uses the existing actual renderer and clipped-face lineage, including verticals.
No candidate is generated, model geometry edited, or source approval transferred.
"""
import argparse,json,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-arena275446-after-palazzo-';BATCH=P+'retained-podium-private-parent-v1-20261101'
OLD=P+'five-original-terrain-binding-v1-20261101';COVER=P+'podium-mall3-original-inset-v2-20261101';INV='government-xl-after-palazzo-renderer-bound-inventory-v1-20261101';CAP=P+'five-original-selection-v1-20261101'

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args();out=BASE/BATCH;local=HERE/'local'/BATCH;lp=local/'reservation.json';refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    prior=take(OLD,BASE/OLD/'summary.json');cover=take(COVER,BASE/COVER/'summary.json');assert prior['status']==cover['status']=='private-terrain-validator-passed'
    old=take(OLD,ROOT/prior['candidate']['path']);new=take(COVER,ROOT/cover['candidate']['path']);rootpath=ROOT/'3d-viewer/city/data/terrain.json';root=take(INV,rootpath)
    assert old['meta']['parentSha256']==new['meta']['parentSha256']==digest(rootpath.read_bytes())
    builder=module('arena_composition_parent_extent',HERE/'resolve-pass-indexed-parent-clipping.py');cells=[min(old['coarseCells'][0],new['coarseCells'][0])-1,min(old['coarseCells'][1],new['coarseCells'][1])-1,max(old['coarseCells'][2],new['coarseCells'][2])+1,max(old['coarseCells'][3],new['coarseCells'][3])+1];assert 0<=cells[0]<cells[2]<root['w'] and 0<=cells[1]<cells[3]<root['h'];bounds=builder.extent(cells,root)
    inventory=take(INV,BASE/INV/'complete-bounds.json.gz');manifest=ROOT/'3d-viewer/city/data/manifest.json';sha=digest(manifest.read_bytes());assert pins[INV][str(manifest.relative_to(ROOT))]==sha;refs.append(manifest)
    selected=take(CAP,BASE/CAP/'selection.json.gz');assert selected['manifestSHA256']==sha;targets=set(old['meta']['targetUids'])|set(new['meta']['targetUids']);sources={r['uid']:r for r in selected['rows']};assert targets<=set(sources)
    native=[r for r in inventory['rows'] if not closed_disjoint(r['completeFourWorldBounds'],bounds)]
    final=module('arena_composition_parent_forms',HERE/'xl-final-script-pass.py');forms=[]
    for form,poly,tile in final.load_forms(bounds):
        path=ROOT/'3d-viewer'/tile;assert digest(path.read_bytes())==inventory['currentFormTileHashes'][str(path.relative_to(ROOT))];refs.append(path);forms.append(dict(building=form,tile=tile,tileSHA256=digest(path.read_bytes())))
    resources={'terrain:city/data/terrain.json'}|{'building:'+u for u in targets}|{'building:'+r['uid'] for r in native}|{('building:'if f['building']['uid'].startswith('landsd/')else'source-form:')+f['building']['uid']for f in forms}
    if not a.owned:
        assert not out.exists() and not local.exists();claim=reservations.claim('arena-private-parent-'+str(uuid.uuid4()),sorted(resources),batch=BATCH,ttl=3600);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease) and set(lease['resources'])==resources and not out.exists();out.mkdir()
    save(out/'scope.json',dict(bounds=bounds,cells=cells,uids=sorted(targets),installationApproved=False));save(out/'private-parent-candidates.json',[prior['candidate']]);save(out/'form-obligations.json.gz',forms)
    tool=HERE/'selected_original_parent_capture_v3.mjs';command=['node',str(tool),str((out/'scope.json').relative_to(ROOT)),str((local/'parent.json').relative_to(ROOT)),str((out/'private-parent-candidates.json').relative_to(ROOT))];save(out/'command.json',dict(command=command,toolSHA256=digest(tool.read_bytes())))
    with(out/'capture.log').open('w') as log:subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    parent=read(local/'parent.json');assert parent['domain']==bounds and parent['triangles'] and len(parent['triangles'])==len(parent['lineage'])
    for name,h in parent['inputHashes'].items():assert digest((ROOT/name).read_bytes())==h;refs.append(ROOT/name)
    assert parent['inputHashes'][prior['candidate']['path']]==prior['candidate']['sha256'];assert reservations.owns(lease) and digest(manifest.read_bytes())==sha
    result=dict(uids=sorted(targets),sourceSHA256ByUid={u:sources[u]['sourceSHA256']for u in targets},currentManifestSHA256=sha,retainedPrivateCandidate=prior['candidate'],coverageCandidateOnlyNotRendered=cover['candidate'],cells=cells,bounds=bounds,actualDrawnParentFaces=len(parent['triangles']),affectedForms=len(forms),touchingNativeUids=sorted(r['uid']for r in native),resources=sorted(resources),parentCaptureTool='selected_original_parent_capture_v3.mjs',privateParentAlreadyCorrected=True,compositionCandidateGenerated=False,sourceGeometryChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification=__doc__+' The proposed composition domain includes both coarse rectangles plus an unchanged parent-cell border. Only the old corrected podium candidate is added to the private scene; the Mall3candidate supplies coverage bounds only. Full actual facet lineage and all current terrain input hashes are captured. Future terrain construction and full regression/acceptance remain required.')
    save(out/'summary.json',result);refs.extend([tool,local/'parent.json',HERE/'xl-final-script-pass.py',HERE/'resolve-pass-indexed-parent-clipping.py']);module('arena_private_parent_capture_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'actual-private-corrected-parent-composition-domain-capture',list(dict.fromkeys(refs)),result);print({k:result[k]for k in ['actualDrawnParentFaces','affectedForms','touchingNativeUids','compositionCandidateGenerated']},flush=True)

if __name__=='__main__':main()

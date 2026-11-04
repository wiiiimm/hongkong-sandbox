"""Bind the exact North original-TIN candidate to the existing two-member policy.

Private surface validation only; source/retained actor and browser acceptance remain.
"""
import copy,json,sys,traceback
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from float32_coverage import approve_roundoff
sys.path.insert(0,str(HERE.parent/'assembly-support-review'))
import terrain_patches as terrain
INTEGRATION=HERE.parent/'island-detail-integration'
if str(INTEGRATION)not in sys.path:sys.path.insert(0,str(INTEGRATION))
from coordinated_native_boundary import POLICY,canonical_sha,validate_effective_coordinated_members

def main():
    base=ROOT/'docs/astra-city/government-import';prefix='government-xl-west-kowloon-north-pair-after-ocean-'
    batch=prefix+'canonical-surface-v1-20261027';out=base/batch;local=HERE/'local'/batch
    assert not out.exists() and not local.exists()
    refs=[HERE/'north_pair_original_canonical_surface_v1_20261027.py',HERE.parent/'assembly-support-review/terrain_patches.py'];pins={};receipts={}
    for suffix in ['parent-v3-20261027','partitioned-inset-v3-20261027','partitioned-seams-v3-20261027']:
        receipt,bound=authenticate(base/(prefix+suffix));receipts[suffix]=receipt;refs.append(base/(prefix+suffix)/'result.json')
        for name,sha in bound.items():
            assert name not in pins or pins[name]==sha
            pins[name]=sha
    for name,sha in pins.items():assert digest((ROOT/name).read_bytes())==sha
    proposal=receipts['partitioned-inset-v3-20261027'];parents=receipts['parent-v3-20261027'];seams=receipts['partitioned-seams-v3-20261027']
    uids=['landsd/182397:0','landsd/309340:0']
    assert proposal['uids']==parents['uids']==seams['uids']==uids
    assert proposal['status']=='private-partition-faces-coverage-passed' and len(proposal['rows'])==2
    rendered=[s for s in seams['seams']if s['mode']=='renderedFloat32']
    assert len(rendered)==1 and all(s['passed'] for s in rendered)
    # Raw false flags remain in the receipt. Source role acceptance is separate.
    assert all((r['fullyBuriedTriangles'],r['fullyBuriedUpwardTriangles'])==((35,24)if r['uid']==uids[0]else(0,0)) for r in seams['foundations'])
    rootpath=ROOT/'3d-viewer/city/data/terrain.json';root=read(rootpath);refs.append(rootpath)
    def ref(path):return dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))
    before={'south':ROOT/'3d-viewer/city/data/government-native-island-cheong-shing-north-v1-20261023.json',
            'north':ROOT/'3d-viewer/city/data/government-native-272986-0.json'}
    manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);refs.append(manifestpath)
    assert all(sum(e['url']==str(p.relative_to(ROOT/'3d-viewer')) for e in manifest['terrainPatches'])==1 for p in before.values())
    newwork=sum(r['privateFaces']-r['exactUnchangedParentFaces']for r in proposal['rows'])
    assert newwork<=25000
    result=dict(uids=uids,sourceSHA256ByUid=proposal['sourceSHA256ByUid'],members=[],installationApproved=False,publication=False,
                sourceGeometryChanges=0,newTerrainWorkFaces=newwork,rawSeamFlagsPreserved=seams['seams'])
    try:
        skeletons={};members={};grids=[]
        for name,row in zip(['south','north'],proposal['rows']):
            old=read(before[name]);refs.append(before[name]);candidate=copy.deepcopy(old)
            assert old['meta']['parentTerrain']=='city/data/terrain.json' and old['meta']['parentSha256']==digest(rootpath.read_bytes())
            bounds=row['bounds'];g=root['meta']['georef']
            cells=[(bounds[0]+834500-g['bE'])/g['aE'],(bounds[1]-816500+g['bN'])/-g['aN'],
                   (bounds[2]+834500-g['bE'])/g['aE'],(bounds[3]-816500+g['bN'])/-g['aN']]
            assert all(v==int(v)for v in cells);cells=list(map(int,cells))
            og=old['meta']['georef'];step=old['cell'];assert step==5 and og['aE']==-og['aN']==step
            w=round((bounds[2]-bounds[0])/step)+1;h=round((bounds[3]-bounds[1])/step)+1
            offset=round((og['bE']-834500-bounds[0])/step)
            assert bounds[1]==816500-og['bN'] and h==old['h'] and offset>=0 and offset+old['w']==w
            if offset:
                raw_sampler=terrain.fine.DemSampler(root);sampler=terrain.fine.DemSampler(root,rendered=True)
                arrays={k:[] for k in ['elev','renderedElev','vegetation']}
                for r in range(h):
                    for c in range(w):
                        if c>=offset:
                            for key in arrays:arrays[key].append(old[key][r*old['w']+c-offset])
                        else:
                            x,z=bounds[0]+c*step,bounds[1]+r*step
                            raw=raw_sampler.ground(x,z);ground=sampler.ground(x,z)
                            arrays['elev'].append(float(raw)if raw<=0 or ground<=0 else float(ground))
                            arrays['renderedElev'].append(float(ground))
                            cc=min(root['w']-1,max(0,round((x+834500-g['bE'])/g['aE'])))
                            rr=min(root['h']-1,max(0,round((z-816500+g['bN'])/-g['aN'])))
                            arrays['vegetation'].append(root['vegetation'][rr*root['w']+cc])
                candidate.update(arrays);candidate.update(w=w,h=h,coarseCells=cells)
                candidate['meta']['georef'].update(bE=bounds[0]+834500,bN=816500-bounds[1],W=w,H=h)
            else:assert candidate['coarseCells']==cells and candidate['w']==w and candidate['h']==h
            for key in ['elev','renderedElev','vegetation']:
                for r in range(h):assert candidate[key][r*w+offset:(r+1)*w]==old[key][r*old['w']:(r+1)*old['w']]
            grids.append(dict(member=name,retainedGridNodes=old['w']*old['h'],newWesternColumns=offset,allOldGridArraysExact=True))
            if offset and 'parentWaterMask' in candidate['meta'].get('source',{}):
                mask=np.asarray(candidate['elev'])<=0
                candidate['meta']['source']['parentWaterMask'].update(waterNodes=int(mask.sum()),landNodes=int((~mask).sum()))
            candidate['meta']['targetUids']=sorted(set(old['meta']['targetUids'])|set(uids))
            path=ROOT/row['privateFacesPath'];assert digest(path.read_bytes())==row['privateFacesSHA256'];refs.append(path)
            faces=np.asarray(read(path)['triangles'],float);assert len(faces)==row['privateFaces'] and np.isfinite(faces).all()
            mesh=candidate['nativeMesh'];oldsource=copy.deepcopy(mesh['source'])
            mesh['position']=faces.reshape(-1).tolist();mesh['index']=list(range(faces.size//3));mesh.pop('sourceOverlap',None)
            mesh['source']=dict(verticalDatum='HKPD',verticalScale=1,policy='Authenticated original-TIN lower inset and affine return, retaining actual drawn parent faces outside the edit; no model geometry changes.')
            mesh['source']['originalPartitionedInset']=dict(proposal=ref(base/(prefix+'partitioned-inset-v3-20261027')/'result.json'),
                previousSourceMetadata=oldsource,sourceModelSHA256ByUid=proposal['sourceSHA256ByUid'])
            approve_roundoff(candidate,bounds)
            path=local/(name+'-unbound.json');save(path,candidate);refs.append(path);skeletons[name]=candidate
            members[name]=dict(before=ref(before[name]),candidate=ref(path),canonicalSHA256=canonical_sha(candidate))
        proofpath=out/'finite-boundary-proof.json';save(proofpath,dict(policy=POLICY,parent=ref(rootpath),members=members,editRegionWKT=proposal['outerWKT']));refs.append(proofpath)
        builder=module('north_pair_existing_validator',HERE/'validated_parent_roundoff_template_v2.py');validated=[]
        for name in ['south','north']:
            node=copy.deepcopy(skeletons[name]);node['nativeMesh']['source']['coordinatedBoundary']=dict(policy=POLICY,proof=ref(proofpath),member=name)
            overlap=module('north_pair_overlap_'+name,HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');overlap.DOC=out/(name+'-overlap');overlap.DOC.mkdir()
            overlap.overlap_proof(node,[ROOT/members[name]['candidate']['path'],proofpath,HERE/'north_pair_original_canonical_surface_v1_20261027.py'])
            assert node['nativeMesh']['position']==skeletons[name]['nativeMesh']['position'] and node['nativeMesh']['index']==skeletons[name]['nativeMesh']['index']
            builder.validate_patch(node,root)
            path=local/(name+'-candidate.json');save(path,node);refs.append(path);validated.append(node)
            result['members'].append(dict(member=name,candidate=ref(path),replaces=dict(url=str(before[name].relative_to(ROOT/'3d-viewer')),sha256=digest(before[name].read_bytes()),retainedUids=read(before[name])['meta']['targetUids']),surfaceValidated=True))
            print('Validated canonical member',name,flush=True)
        validate_effective_coordinated_members(validated)
        result.update(status='private-coordinated-surface-validator-passed',bothEffectiveMembersRequired=True,currentManifest=ref(manifestpath),retainedGridChecks=grids)
    except Exception as error:
        result.update(status='private-canonical-surface-investigation',reason=str(error),errorType=type(error).__name__)
        save(out/'failure.json',dict(errorType=type(error).__name__,message=str(error),traceback=traceback.format_exc()))
    for name,sha in pins.items():assert digest((ROOT/name).read_bytes())==sha
    refs.extend([INTEGRATION/'coordinated_native_boundary.py',INTEGRATION/'native_terrain_validation.py',INTEGRATION/'publish.py',HERE/'validated_parent_roundoff_template_v2.py',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py'])
    save(out/'summary.json',result)
    module('north_pair_canonical_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'private-original-pair-existing-canonical-surface-validation',list(dict.fromkeys(refs)),result)
    print(dict(status=result['status'],reason=result.get('reason')),flush=True)

if __name__=='__main__':main()

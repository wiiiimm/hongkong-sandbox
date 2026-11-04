"""Unexecuted atomic-three guard: full POSITION/masks and immutable pure replays.

Canonical current adapters retain their exact df35 binding. Post-apply replay
uses the identical mathematical inputs, separately from the exact scene delta;
it does not claim a fresh canonical role at a substituted manifest digest.
"""
from pathlib import Path
import importlib.util,json
import numpy as np
from run import ROOT,HERE,read,digest
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from complete_actual_native_position_bounds_separation_20261011 import strict_planar_separation
BASE=ROOT/'docs/astra-city/government-import'
FIELDS=['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']
MODES=['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def full_bounds(row,actual):
 assert row['uid']==actual['uid'] and row['sourceSHA256']==actual['sourceSHA256']
 source=ROOT/row['candidate']['path'];proof=packed_world_bounds(source.read_bytes())
 assert proof['sourceSHA256']==row['sourceSHA256'] and proof['allOriginalPositionVerticesAccounted']
 out={'providerOriginal':proof['originalWholeSourceBounds']}
 for mode,field in zip(MODES[1:],FIELDS):
  p=np.asarray(actual[field],float).reshape(-1,3)
  assert len(p)==proof['completeOriginalPositionVertices'] and np.isfinite(p).all()
  out[mode]=[p.min(0).tolist(),p.max(0).tolist()]
 return dict(uid=row['uid'],source=ref(source),completeWholeOriginalPOSITIONProof=proof,completeFourWorldPOSITIONBounds=out)

def domain(terrain,parent):
 assert not terrain.get('replaces') and not terrain.get('replacesMany')
 path=ROOT/terrain['source'];t=read(path);assert ref(path)['sha256']==terrain['sha256']
 assert not t.get('patches') and t['meta']['parentTerrain']=='city/data/terrain.json'
 assert t['meta']['parentSha256']==ref(ROOT/'3d-viewer/city/data/terrain.json')['sha256']
 p=np.asarray(t['nativeMesh']['position'],float).reshape(-1,3);idx=np.asarray(t['nativeMesh']['index'],int)
 assert len(idx)%3==0 and idx.min()>=0 and idx.max()<len(p) and np.isfinite(p).all()
 origin=parent['meta']['origin'];g=t['meta']['georef'];pg=parent['meta']['georef'];i0,j0,i1,j1=t['coarseCells']
 assert i0<i1 and j0<j1
 bbox=[g['bE']-origin[0],origin[1]-g['bN'],g['bE']-origin[0]+(t['w']-1)*g['aE'],origin[1]-g['bN']-(t['h']-1)*g['aN']]
 assert bbox==[pg['bE']+i0*pg['aE']-origin[0],origin[1]-(pg['bN']+j0*pg['aN']),pg['bE']+i1*pg['aE']-origin[0],origin[1]-(pg['bN']+j1*pg['aN'])]
 assert np.all(p[:,0]>=bbox[0]) and np.all(p[:,0]<=bbox[2]) and np.all(p[:,2]>=bbox[1]) and np.all(p[:,2]<=bbox[3])
 corners=np.asarray([[bbox[0],p[:,1].min(),bbox[1]],[bbox[2],p[:,1].max(),bbox[3]]])
 points=np.concatenate([p,corners,p.astype(np.float32).astype(float),corners.astype(np.float32).astype(float)])
 return dict(source=ref(path),completeTriangles=len(idx)//3,coarseCells=[i0,j0,i1,j1],completeDeclaredDomain=bbox,wholeDomainIncludingFloat32=[points.min(0).tolist(),points.max(0).tolist()])

def separation(twin,evangel,twin_rows,evangel_row):
 ta=read(BASE/'xl-terrain-recovery-20261011-twin-regency-two-current-render-attribute-capture-v1/actual-render-attributes.json.gz')
 ea=read(BASE/'government-xl-evangel-college-91306-current-actual-ground-capture-v1-20261011/complete-current-actual-source-and-ground.json.gz')
 assert len(ta['rows'])==2 and {r['uid']for r in ta['rows']}==twin.UIDS
 bounds=[full_bounds(r,next(a for a in ta['rows']if a['uid']==r['uid']))for r in twin_rows]+[full_bounds(evangel_row,ea)]
 parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath)
 plans=[read(s.STAGE/'plan.json')for s in [twin,evangel]]
 assert all(len(p['areas'])==len(p['topLevelTerrainPatches'])==1 for p in plans)
 domains=[domain(p['topLevelTerrainPatches'][0],parent)for p in plans]
 assert [d['completeTriangles']for d in domains]==[2513,7579]
 a,b=[d['coarseCells']for d in domains]
 assert a[2]<b[0] or b[2]<a[0] or a[3]<b[1] or b[3]<a[1]
 proofs=[dict(kind='whole-declared-routing-domain',**strict_planar_separation(domains[0]['wholeDomainIncludingFloat32'],domains[1]['wholeDomainIncludingFloat32']))]
 for own in bounds:
  other=domains[1 if own['uid']in twin.UIDS else 0]
  for mode,box in own['completeFourWorldPOSITIONBounds'].items():
   proofs.append(dict(kind='whole-owned-source-versus-other-terrain',uid=own['uid'],mode=mode,**strict_planar_separation(box,other['wholeDomainIncludingFloat32'])))
 for t in bounds[:2]:
  for tm,tb in t['completeFourWorldPOSITIONBounds'].items():
   for em,eb in bounds[2]['completeFourWorldPOSITIONBounds'].items():
    proofs.append(dict(kind='complete-source-pair',twinUID=t['uid'],twinMode=tm,evangelMode=em,**strict_planar_separation(tb,eb)))
 return dict(completeOwnedSources=bounds,completeAlteredTerrainDomains=domains,completeExactStrictSeparationProofs=proofs,parent=ref(parentpath),sameParentRoutingMasksStrictlyDisjoint=True,noNativeReacceptance=True,noGeometryOrToleranceChange=True)

def prepare_math(twin_role,evangel_role):
 fixture=module('atomic_three_twin_fixture',HERE/'twin_regency1120_complete_actual_fixture_v1_20261011.py')
 tk=module('atomic_three_twin_policy',HERE/'twin_regency1120_complete_original_role_composition_v1_20261011.py')
 args,_,pins,_=fixture.actual_fixture();expected=json.loads(json.dumps(tk.verify(**args)))
 assert expected==twin_role['completeFourStreamRoleComposition']
 bound=module('atomic_three_evangel_bound',HERE/'evangel_college_whole_current_role_bound_20261011.py')
 policy=module('atomic_three_evangel_policy',HERE/'evangel_college_whole_current_role_policy_20261011.py')
 docs={k:read(p/('proposal.json.gz'if k in {'standing','remaining'}else'diagnostic.json.gz'))for k,p in bound.DOCS.items()if k not in {'source','identity','native_input'}}
 guards={k:read(bound.DOCS['physical']/n)for k,n in dict(metrics='metrics.json',validation='validation.json',foundation='foundation.json',neighbours='neighbour-checks.json',native_checks='native-neighbour-checks.json').items()}
 data=read(bound.DOCS['source']/'complete-four-stream-ground-inputs.json.gz')
 rt=read(HERE/'local'/bound.DOCS['physical'].name/'runtime-geometry.json.gz')['rows'][0]
 eargs=dict(data=data,ground=np.asarray(rt['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3),identity=read(bound.DOCS['identity']/'identity.json'),current_manifest=evangel_role['currentManifest'],**docs,**guards)
 ep=json.loads(json.dumps(policy.compose(**eargs)));assert all(evangel_role[k]==v for k,v in ep.items())
 return dict(twinPolicy=tk,twinArgs=args,twinExpected=expected,evangelPolicy=policy,evangelArgs=eargs,evangelExpected=ep)

def replay_math(prepared):
 assert json.loads(json.dumps(prepared['twinPolicy'].verify(**prepared['twinArgs'])))==prepared['twinExpected']
 assert json.loads(json.dumps(prepared['evangelPolicy'].compose(**prepared['evangelArgs'])))==prepared['evangelExpected']
 return dict(originalCanonicalBindingRetained=True,immutableTwinAndEvangelMathematicalResultsExact=True,newManifestNotSubstitutedIntoCanonicalRole=True,postSceneDeltaMustBeVerifiedSeparately=True,nativeReacceptance=False)

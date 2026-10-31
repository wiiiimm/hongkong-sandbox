"""Hermetic original/captured actual Lippo fixtures; no current live assertions."""
import numpy as np
from run import ROOT,read
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from lippo_tower_current_basic_mainbody_join_role_v1_20261011 import WORLD,CARRIER
BASE=ROOT/'docs/astra-city/government-import'
INPUT=BASE/'government-xl-lippo-tower-only-current-complete-inputs-v3-20261011'
SUPPORT=BASE/'government-xl-lippo-current-basic-bounded-wall-grade-clear-cap-tower-paths-v3-20261011'
PARTITION=BASE/'government-xl-lippo-tower-current-basic-complete-lower-interface-partition-v2-20261011'
FOREIGN=BASE/'government-xl-lippo-tower-only-complete-current-foreign-finite-contacts-v1-20261011'
def fixture():
 inp=read(INPUT/'input.json.gz');geo=read(INPUT/'complete-current-geometry.json.gz');row=inp['rows'][0];rr=geo['row'];ix=np.array(rr['completeOriginalIndex'],dtype=np.int64).reshape(-1,3)
 worlds={'providerOriginal':decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes())}
 for mode,key in [('actualLiteral','completeLiteralWorldPosition'),('explicitLeftAssociatedF32ModelMatrix','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32ModelMatrix','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(rr[key],dtype='<f8').reshape(-1,3)[ix]
 raw=next(r for r in geo['completeCurrentBasicGeometry'] if r['uid']==CARRIER);basic=np.asarray(raw['position'],dtype='<f8').reshape(-1,3)[np.asarray(raw['index'],dtype=np.int64).reshape(-1,3)]
 actors=read(FOREIGN/'diagnostic.json.gz')['actors'];carrier=next(a for a in actors if a['uid']==CARRIER)
 finite={}
 for mode in WORLD:
  filename=mode if mode!='explicitBalancedF32ModelMatrix' else 'explicitLeftAssociatedF32ModelMatrix'
  finite[mode]=read(SUPPORT/('complete-tower-finite-'+filename+'.json.gz'))
 return dict(sourceSHA256=row['sourceSHA256'],towerCurrentForm=row['source']['building'],carrierCurrentForm=raw['currentForm'],carrierIdentityModelMatrix=raw['identityModelMatrix'],basic=basic,groundSHA256=geo['completeCurrentDrawnTerrain']['worldSHA256'],worlds=worlds,finite=finite,otherForeignActors=[a for a in actors if a['uid']!=CARRIER],carrierPaths=read(SUPPORT/'diagnostic.json.gz'),basicGraph=read(SUPPORT/'bounded-basic-grade-roof-paths.json.gz'),basicFinite=read(SUPPORT/'complete-actual-basic-finite-facets.json.gz'),partition=read(PARTITION/'diagnostic.json.gz'),carrierContacts={r['ownedMode']:r for r in carrier['trials']})

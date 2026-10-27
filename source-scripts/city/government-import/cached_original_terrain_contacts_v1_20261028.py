"""Test one cached neighbouring original TIN against the immutable source.

Source-only diagnostics; no terrain construction, source edits or acceptance.
"""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE=ROOT/'docs/astra-city/government-import'
def main():
 p=argparse.ArgumentParser()
 for key in ['batch','uid','selection','terrain-proof','terrain','lease']:p.add_argument('--'+key,required=True)
 a=p.parse_args();out=BASE/a.batch;assert a.batch.startswith('government-xl-')and '/'not in a.batch and not out.exists();lease=read(Path(a.lease));assert reservations.owns(lease)and 'building:'+a.uid in lease['resources'];refs=[Path(__file__)]
 _,pins=authenticate(BASE/a.selection);path=BASE/a.selection/'selection.json.gz';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.extend([BASE/a.selection/'result.json',path]);row=next(r for r in read(path)['rows']if r['uid']==a.uid);asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset);source=decode_original_world_triangles(asset.read_bytes())
 _,terrain_pins=authenticate(BASE/a.terrain_proof);refs.append(BASE/a.terrain_proof/'result.json');path=(ROOT/a.terrain).resolve();assert path.is_relative_to(ROOT.resolve())and digest(path.read_bytes())==terrain_pins[str(path.relative_to(ROOT))];refs.append(path)
 for buffer in read(path)['buffers']:
  uri=buffer['uri'];assert not uri.startswith('data:');part=(path.parent/uri).resolve();assert part.is_relative_to(path.parent.resolve())and digest(part.read_bytes())==terrain_pins[str(part.relative_to(ROOT))];refs.append(part)
 context=module('nominated_cached_original_tin_reader',HERE/'pending-context.py');ground=context.triangles(path);bounds=np.array([ground.min(axis=(0,1)),ground.max(axis=(0,1))]);lo,hi=source.min(axis=(0,1)),source.max(axis=(0,1));overlap=bool(np.all(bounds[0][[0,2]]<=hi[[0,2]])and np.all(bounds[1][[0,2]]>=lo[[0,2]]))
 proof=exact_finite_contacts(source,list(range(len(source))),ground,list(range(len(ground))));positive=[c for c in proof['contacts']if c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2]
 result=dict(uids=[a.uid],uid=a.uid,sourceSHA256=row['sourceSHA256'],sourceWorldSHA256=digest(source.astype('<f8').tobytes()),originalTerrainWorldSHA256=digest(ground.astype('<f8').tobytes()),originalTerrainWorldBounds=bounds.tolist(),sourceWorldBounds=[lo.tolist(),hi.tolist()],boundsOverlapXZ=overlap,sourceFaces=len(source),completeOriginalTerrainFaces=len(ground),finiteContacts=len(proof['contacts']),positiveFiniteSurfaceContacts=len(positive),sourceFacesOmitted=0,terrainFacesOmitted=0,sourceGeometryChanges=0,physicalSupportAccepted=False,installationApproved=False,qualification='Complete exact original source/TIN finite contacts from an authenticated cached adjacent-sheet acquisition. Every source and terrain facet supplied, with native node transforms/fixed1x placement. No point-height inference, repair, new terrain, datum correction, support or current-scene acceptance.')
 save(out/'original.json.gz',dict(**result,proof=proof));save(out/'summary.json',result);assert reservations.owns(lease);refs.extend([HERE/'pending-context.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_finite_triangle_contacts_20261010.py']);module('cached_adjacent_tin_contacts_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-cached-original-adjacent-tin-contacts',refs,result);print({k:result[k]for k in ['originalTerrainWorldBounds','boundsOverlapXZ','completeOriginalTerrainFaces','finiteContacts']},flush=True)
if __name__=='__main__':main()

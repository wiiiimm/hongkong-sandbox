"""Independent current-parent retention and coverage audit of PRIVATE three members.
Creates only a private successor; no acceptance, validator changes or publication.
"""
import copy
from collections import Counter
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from rectangular_native_fragments_v1_20261101 import drawn
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-one-peking-after-twin-';BATCH=P+'three-member-retention-v1-20261101'
def main():
 out=BASE/BATCH;assert not out.exists();batch=P+'three-member-original-return-v2-20261101';receipt,pins=authenticate(BASE/batch);refs=[Path(__file__),BASE/batch/'result.json']
 def take(path):
  assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
 summary=take(BASE/batch/'summary.json');assert summary['allFiniteSeamsPassed'];lineage=take(BASE/batch/'lineage.json.gz');parentpath=ROOT/'3d-viewer'/summary['parentURL'];parent=take(parentpath);assert len(parent['patches'])==17;successor=copy.deepcopy(parent);meshes={};coverage=[]
 for name,member in summary['members'].items():
  candidate=take(ROOT/member['candidate']['path']);actual=drawn(candidate);meshes[name]=actual;rows=lineage[name]['outputLineage'];assert len(rows)==len(actual);source=drawn(parent['patches'][int(name.split('-')[1])])if name.startswith('retained-')else drawn(take(ROOT/member['before']['path']))
  if name.startswith('retained-'):
   old=parent['patches'][int(name.split('-')[1])];assert candidate['coarseCells']==old['coarseCells'];assert set(candidate['meta']['targetUids'])==set(old['meta']['targetUids'])|set(receipt['uids'])
   expected=copy.deepcopy(old)
   for k in ['id','nativeMesh']:expected[k]=candidate[k]
   for k in ['parentTerrain','parentSha256','targetUids']:expected['meta'][k]=candidate['meta'][k]
   assert candidate==expected,'Retained non-geometry data changed'
   successor['patches'][int(name.split('-')[1])]=candidate
  else:successor['patches'].append(candidate)
  covered_parent=set();unchanged_count=0;outer=shapely.from_wkt(lineage[name]['outerWKT']);outside_ids={i for i,f in enumerate(source)if not shapely.Polygon(f[:,[0,2]]).intersects(outer)}
  for i,r in enumerate(rows):
   parent_id=r['parentFace'];assert 0<=parent_id<len(source);covered_parent.add(parent_id)
   if r['kind']=='unchanged':assert np.array_equal(actual[i],source[parent_id]);unchanged_count+=1
   else:assert parent_id not in outside_ids
  assert covered_parent==set(range(len(source))),'Current parent face lost';assert outside_ids<=set(r['parentFace']for r in rows if r['kind']=='unchanged')
  # Exact unchanged source metadata is checked above; coverage is measured from
  # every effective Float32 indexed nonvertical face under existing tolerances.
  polygons=shapely.polygons(actual[:,:,[0,2]]);areas=shapely.area(polygons);nonvertical=polygons[areas>1e-10];union=shapely.union_all(nonvertical);g=candidate['meta']['georef'];bounds=[g['bE']-834500,816500-g['bN'],g['bE']-834500+(candidate['w']-1)*g['aE'],816500-g['bN']-(candidate['h']-1)*g['aN']];rect=shapely.box(*bounds);gap=union.symmetric_difference(rect).area;tol=max(.001,rect.area*1e-7);excess=float(shapely.area(nonvertical).sum()-union.area)
  coverage.append(dict(member=name,bounds=bounds,faces=len(actual),unchangedFaces=unchanged_count,allCurrentParentFacesRepresented=True,outsideReturnFacesExact=True,coverageGapM2=gap,existingCoverageToleranceM2=tol,coverageWithinOrdinaryTolerance=gap<tol,projectedExcessM2=excess,requiresFreshOverlapEvidence=excess>=tol))
 targets=set(parent['meta'].get('targetUids',[]))|set(receipt['uids']);successor['meta']['targetUids']=sorted(targets)
 assert len(successor['patches'])==18
 for i in range(17):
  if i not in [12,15]:assert successor['patches'][i]==parent['patches'][i]
 stripped_before=copy.deepcopy(parent);stripped_after=copy.deepcopy(successor)
 for x in [stripped_before,stripped_after]:x.pop('patches');x['meta'].pop('targetUids',None)
 assert stripped_before==stripped_after,'Root grid or unrelated metadata changed'
 boxes=[shapely.box(*r['bounds'])for r in coverage]
 assert all(a.intersection(b).area==0 for i,a in enumerate(boxes)for b in boxes[i+1:])
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==summary['currentManifestSHA256'];refs.append(manifest);save(out/'unapproved-successor-terrain.json',successor)
 result=dict(uids=receipt['uids'],currentManifestSHA256=summary['currentManifestSHA256'],parentURL=summary['parentURL'],parentSHA256=summary['parentSHA256'],candidate={'path':str((out/'unapproved-successor-terrain.json').relative_to(ROOT)),'sha256':digest((out/'unapproved-successor-terrain.json').read_bytes())},coverage=coverage,retainedUnrelatedChildren=15,rootGridAndUnrelatedMetadataExact=True,allOldNativeFacesAccountedFor=True,outsideReturnFacesExact=True,allThreeFiniteSeamsPassed=True,rectanglesDisjoint=True,sourceGeometryChanges=0,physicalAcceptance=False,canonicalTerrainValidationPassed=False,installationApproved=False,publication=False,nextAction='Fresh overlap/coverage/boundary admission proof, actual drawn candidate scope and full affected actor regression, original source/physical review and desktop/mobile browser checks.')
 save(out/'summary.json',result);refs.append(HERE/'rectangular_native_fragments_v1_20261101.py');module('one_peking_retention_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-full-current-parent-and-float32-native-retention-coverage',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()

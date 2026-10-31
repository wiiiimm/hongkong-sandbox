"""Bind fresh current primary canopy identity to the two complete source searches.
Specific recoverability hold, never permanent or territory-wide absence.
"""
from pathlib import Path
import importlib.util,json,sys
from run import ROOT,HERE,read,save,digest
sys.path.insert(0,str(HERE.parent/'landsd-territory'));from source import request
sys.path.insert(0,str(HERE.parent/'citywide-source'));from discover import ac
BATCH='government-xl-villa-canopy-authentic-source-specific-hold-v1-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH
BASE=DOC.parent;SEARCHES=['government-xl-villa-canopy-authentic-source-directory-search-v1-20261010','government-xl-villa-canopy-authentic-individualised-source-directory-search-v1-20261010']
PENETRATION=BASE/'government-xl-villa-canopy-exact-closed-roof-penetration-v1-20261010'
URL='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0/query'
def main():
 assert not (DOC/'result.json').exists();DOC.mkdir(parents=True,exist_ok=True)
 raw,rec=request(URL,dict(f='json',where="BuildingCSUID='2162233384T20211022'",outFields='*',returnGeometry='true',outSR='2326',resultRecordCount='1000',orderByFields='OBJECTID'))
 (DOC/'fresh-exact-current-primary.json').write_bytes(raw);save(DOC/'fresh-exact-current-primary.request.json',rec)
 data=json.loads(raw);assert len(data['features'])==1 and not data.get('exceededTransferLimit');a=data['features'][0]['attributes']
 assert a['Status']=='Active' and a['GeoRefNo']=='2162233384' and a['BuildingID']==1910216544 and a['BuildingBlockType']=='Open-sided Structure'
 rows=[];refs=[Path(__file__),PENETRATION/'result.json',PENETRATION/'diagnostic.json.gz']
 for name in SEARCHES:
  folder=BASE/name;search=read(folder/'diagnostic.json.gz');assert not search['exactCurrentPrefixFound']
  for r in search['formats']:
   directory=folder/r['format']/'zip-directory.bin';blob=directory.read_bytes();assert digest(blob)==r['directorySHA256'];entries,checked=ac.parse_directory(blob)
   matches=[e.filename for e in entries if '2162233384' in e.filename]
   assert not matches,'Other-class exact GeoRef needs independent acquisition, not absence'
   rows.append(dict(dataset=name,format=r['format'],sourceURL=r['sourceURL'],revision=r['revision'],etag=r['etag'],completeDirectorySHA256=r['directorySHA256'],allClassesExactGeoRefMembers=matches,completeDirectoryEntries=len(entries)))
  refs += [p for p in folder.rglob('*') if p.is_file()]
 penetration=read(PENETRATION/'diagnostic.json.gz');assert penetration['positiveRenderedRoofVolumePenetration'] and penetration['strictInteriorPenetrationWitnesses']
 result=dict(uid='landsd/325786:0',csuid=a['BuildingCSUID'],buildingID=a['BuildingID'],freshUniqueActivePrimary=a,sourceSearches=rows,exactSourceAvailableInSearchedCurrentArchives=False,territoryWideAbsenceClaimed=False,permanentRejection=False,governmentGeometryCorruptClaimed=False,currentCanopyHeightsEstimated=True,originalFiveModelOwnGatesRemainPositive=True,strictProceduralRoofPenetrationRemains=True,penetratingSourceWalls=sorted({x['sourceFace'] for x in penetration['strictInteriorPenetrationWitnesses']}),sourceGeometryChanges=0,sourceSuppression=0,thresholdChanges=0,identityAccepted=False,fullAcceptance=False,installation=False,humanDecisionRequired=False,humanStatus='held-current-foreign-procedural-roof-penetration-authentic-canopy-lineage-not-found-in-six-pinned-archives',revisitConditions=['Acquire exact source-qualified current canopy original from a new official revision or independently mapped original source with complete identity/component/physical/current gates.','Alternatively separately reviewed source-backed current procedural canopy correction; retain exact original model bytes, all foreign actors, and every strict terrain/collision gate.'],qualification='All classes in complete fresh ETag-pinned GLTF/FBX/MAX directories of both official datasets searched for exact current GeoRef. Search absence is bounded to these six archive versions; no source availability or geometry impossibility claimed outside that scope. Estimated procedural canopy remains a genuine current-render conflict; no suppression or threshold waiver.')
 save(DOC/'diagnostic.json.gz',result)
 refs += [p for p in DOC.rglob('*') if p.is_file()]
 spec=importlib.util.spec_from_file_location('villa_canopy_hold_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(BATCH,'fresh-unique-primary-canopy-six-current-archive-exact-lineage-negative-and-render-conflict-specific-hold-v1',sorted(set(refs)),dict(result,uids=['landsd/325786:0','landsd/89917:0']))
 print(dict(completeCurrentArchives=len(rows),uniquePrimaryCSUID=a['BuildingCSUID'],specificSourceHeld=True,permanentRejection=False),flush=True)
if __name__=='__main__':main()

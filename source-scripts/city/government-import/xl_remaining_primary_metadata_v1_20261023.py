"""Batch official source metadata for fixed remaining XL GeoRef model identities.
Read-only source investigation, not screening, queueing or installation approval.
"""
import sys,gzip,re
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from source import request
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-remaining-186-primary-metadata-v1-20261023'
PRIOR='government-xl-fu-wong-retained-original-installed-v7-20261023'
URL='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer'
def chunks(rows,n=50):
 for i in range(0,len(rows),n):yield rows[i:i+n]
def main():
 doc=BASE/BATCH;assert not doc.exists();refs=[Path(__file__),HERE.parent/'landsd-territory/source.py'];_,pins=authenticate(BASE/PRIOR);refs.append(BASE/PRIOR/'result.json')
 p=BASE/PRIOR/'full-xl-current-count.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);count=read(p);assert count['counts']==dict(total=521,installedVerified=334,remaining=187)
 rows=[r for r in count['rows']if not r['installedVerified']and r['uid']!='landsd/228219:0'];assert len(rows)==186
 for r in rows:
  model=r['sourceKey'].split('/')[-1];assert re.match(r'^B\d{10}',model);r['originalModelId']=model;r['geoRefNo']=model[1:11]
 save(doc/'source-scope.json',dict(rows=rows,excludedAlreadyReviewedInLiveInstallation=['landsd/228219:0'],installationApproved=False))
 def query(name,table,where):
  raw,receipt=request(URL+'/'+str(table)+'/query',dict(f='json',where=where,outFields='*',returnGeometry='false',resultRecordCount='2000',orderByFields='OBJECTID'),json_expected=False)
  decoded=gzip.decompress(raw)if raw.startswith(b'\x1f\x8b')else raw
  p=doc/(name+'.json');p.write_bytes(decoded);save(doc/(name+'-request.json'),dict(**receipt,decodedSHA256=digest(decoded),gzipDecoded=raw!=decoded))
  if raw!=decoded:(doc/(name+'-wire.gz')).write_bytes(raw)
  data=read(p);assert not data.get('error')and not data.get('exceededTransferLimit');print(name,len(data['features']),flush=True);return [r['attributes']for r in data['features']]
 def quoted(values):return ','.join("'"+s.replace("'","''")+"'"for s in values)
 footprints=[]
 for i,group in enumerate(chunks(sorted({r['geoRefNo']for r in rows})),1):footprints+=query('footprints-'+str(i),0,'GeoRefNo IN ('+quoted(group)+')')
 csuids=sorted({r['BuildingCSUID']for r in footprints});relations=[]
 for i,group in enumerate(chunks(csuids),1):relations+=query('relations-'+str(i),1002,'BuildingCSUID IN ('+quoted(group)+')')
 ids=sorted({int(r['BuildingStructureID'])for r in relations});structures=[]
 for i,group in enumerate(chunks(ids),1):structures+=query('structures-'+str(i),1003,'BuildingStructureID IN ('+','.join(map(str,group))+')')
 permits=sorted({r['OPNo']for r in structures if r.get('OPNo')});permit_structures=[]
 for i,group in enumerate(chunks(permits),1):permit_structures+=query('permit-structures-'+str(i),1003,'OPNo IN ('+quoted(group)+')')
 permit_ids=sorted({int(r['BuildingStructureID'])for r in permit_structures});permit_relations=[]
 for i,group in enumerate(chunks(permit_ids),1):permit_relations+=query('permit-relations-'+str(i),1002,'BuildingStructureID IN ('+','.join(map(str,group))+')')
 by_structure={int(r['BuildingStructureID']):r for r in structures};output=[]
 for source in rows:
  matches=[r for r in footprints if str(r['GeoRefNo'])==source['geoRefNo']];cs={r['BuildingCSUID']for r in matches};links=[r for r in relations if r['BuildingCSUID']in cs];related=sorted({int(r['BuildingStructureID'])for r in links});op=sorted({by_structure[i]['OPNo']for i in related if by_structure[i].get('OPNo')})
  output.append(dict(**source,footprintMatches=matches,structureLinks=links,structureIds=related,occupationPermits=op,sourceIdentityAccepted=False,supportApproved=False,installationApproved=False))
 save(doc/'metadata.json.gz',dict(rows=output,structures=structures,completePermitStructures=permit_structures,completePermitRelations=permit_relations,installationApproved=False))
 result=dict(uids=[r['uid']for r in rows],sourceModels=len(rows),queriedGeoRefs=len({r['geoRefNo']for r in rows}),modelsWithPrimaryMatches=sum(bool(r['footprintMatches'])for r in output),modelsWithMultiplePrimaryMatches=sum(len(r['footprintMatches'])>1 for r in output),modelsWithoutPrimaryMatches=sum(not r['footprintMatches']for r in output),primaryRecords=len(footprints),structureRecords=len(structures),occupationPermits=len(permits),completePermitStructureRecords=len(permit_structures),completePermitRelationRecords=len(permit_relations),sourceGeometryChanges=0,installationApproved=False,newlyInstalled=0,sourceIdentityAccepted=False,qualification='Official metadata by exact indexed original ModelId GeoRef prefix for all186remaining sources excluding already-reviewed live FuTor. GeoRef matches, structure links and complete nonempty permit membership retained as source evidence only. No exact targetCSUID disambiguation, legal ownership, support role, geometry repair, current placement/physical/browser approval, model queue or skip/install credit.')
 save(doc/'summary.json',result);module('remaining_primary_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'remaining-original-xl-official-primary-metadata',refs,result);print(result,flush=True)
if __name__=='__main__':main()

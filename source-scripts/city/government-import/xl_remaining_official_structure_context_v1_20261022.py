"""Acquire bounded official structure metadata for the complete unfinished XL ledger."""
import sys,gzip
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
sys.path.insert(0,str(HERE.parent/'landsd-territory'));from source import request
B='government-xl-remaining-official-structure-context-v1-20261022';BASE=ROOT/'docs/astra-city/government-import';D=BASE/B
PREVIOUS='government-xl-tung-ping-retained-original-installed-v5-20261022'
URL='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer'
def main():
 assert not D.exists();receipt,pins=authenticate(BASE/PREVIOUS);count=BASE/PREVIOUS/'full-xl-current-count.json';assert digest(count.read_bytes())==pins[str(count.relative_to(ROOT))]
 ledger=read(count);remaining=[r for r in ledger['rows']if not r['installedVerified']];assert len(remaining)==189 and len(ledger['rows'])==521
 manifest=ROOT/'3d-viewer/city/data/manifest.json';manifestsha=digest(manifest.read_bytes());assert manifestsha==receipt['manifest']['sha256']
 wanted={r['uid']for r in remaining if r.get('uid')};forms={};refs=[Path(__file__),BASE/PREVIOUS/'result.json',count,manifest,HERE.parent/'landsd-territory/source.py']
 for tile in read(manifest)['tiles']:
  p=ROOT/'3d-viewer'/tile['url'];matches=[f for f in read(p)['buildings']if f['uid']in wanted]
  if matches:
   refs.append(p)
   for f in matches:assert f['uid']not in forms;forms[f['uid']]=f
 missing=sorted(wanted-set(forms));assert not missing,missing
 csuids=sorted({f['buildingCSUID']for f in forms.values()});assert all(s.isalnum()for s in csuids)
 D.mkdir();requests=[]
 def query(label,table,where):
  features=[];offset=0
  while True:
   params=dict(f='json',where=where,outFields='*',returnGeometry='false',resultRecordCount='1000',resultOffset=str(offset),orderByFields='OBJECTID')
   raw,meta=request(URL+'/'+str(table)+'/query',params,json_expected=False)
   decoded=gzip.decompress(raw)if raw.startswith(b'\x1f\x8b')else raw
   name=label+'-'+str(offset);p=D/(name+'.json');p.write_bytes(decoded);meta.update(decodedSHA256=digest(decoded),gzipDecoded=raw!=decoded);save(D/(name+'-request.json'),meta)
   if raw!=decoded:(D/(name+'-original.gz')).write_bytes(raw)
   data=read(p);assert not data.get('error'),data.get('error');rows=data['features'];features.extend(rows);requests.append(dict(label=name,table=table,rows=len(rows),sha256=digest(decoded)))
   if not data.get('exceededTransferLimit')and len(rows)<1000:break
   assert rows and offset<100000;offset+=len(rows)
  ids=[f['attributes']['OBJECTID']for f in features];assert len(ids)==len(set(ids))
  return features
 footprints=[];relations=[]
 for i in range(0,len(csuids),50):
  batch=csuids[i:i+50];where='BuildingCSUID IN ('+','.join("'"+s+"'"for s in batch)+')'
  footprints+=query('primary-'+str(i//50),0,where);relations+=query('relations-'+str(i//50),1002,where)
 structureids=sorted({int(f['attributes']['BuildingStructureID'])for f in relations});members=[];structures=[]
 for i in range(0,len(structureids),20):
  ids=structureids[i:i+20];where='BuildingStructureID IN ('+','.join(map(str,ids))+')'
  members+=query('members-'+str(i//20),1002,where);structures+=query('structures-'+str(i//20),1003,where)
 primary={}
 for f in footprints:primary.setdefault(f['attributes']['BuildingCSUID'],[]).append(f['attributes'])
 bycs={};byst={}
 for f in relations:
  a=f['attributes'];bycs.setdefault(a['BuildingCSUID'],set()).add(int(a['BuildingStructureID']))
 for f in members:
  a=f['attributes'];byst.setdefault(int(a['BuildingStructureID']),set()).add(a['BuildingCSUID'])
 rows=[]
 for r in remaining:
  form=forms.get(r.get('uid'));cs=form.get('buildingCSUID')if form else None;ids=sorted(bycs.get(cs,set()));group=sorted(set().union(*(byst.get(i,set())for i in ids)))if ids else[]
  records=primary.get(cs,[]);expected=r['sourceKey'].split('/')[-1][1:11]
  rows.append(dict(**r,buildingCSUID=cs,currentForm=form,officialPrimaryRecords=records,officialExactActiveRecord=bool(len(records)==1 and records[0].get('Status')=='Active'and records[0].get('GeoRefNo')==expected),officialStructureIDs=ids,officialStructureMemberCSUIDs=group,otherOfficialMembers=[v for v in group if v!=cs]))
 assert digest(manifest.read_bytes())==manifestsha
 summary=dict(uids=sorted(wanted),allUnfinishedXL=189,currentManifestSHA256=manifestsha,rows=rows,counts=dict(unfinished=189,exactActivePrimary=sum(r['officialExactActiveRecord']for r in rows),withStructureLink=sum(bool(r['officialStructureIDs'])for r in rows),withOtherOfficialMembers=sum(bool(r['otherOfficialMembers'])for r in rows)),sourceIdentityAccepted=False,installationApproved=False,newlyInstalled=0,permanentRejection=False,sourceGeometryChanges=0,scriptExternalAICalls=0,qualification='Complete fixed-ledger unfinished scope; fresh primary/structure membership only. A shared official structure is identity context, not geometry ownership, source validity, placement/collision/support approval or a publication instruction.')
 save(D/'summary.json',summary);save(D/'request-index.json',requests)
 module('remaining_structure_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(B,'all-unfinished-xl-official-structure-context',refs,summary)
 print(summary['counts'],flush=True)
if __name__=='__main__':main()

"""Fetch exact official identity/permit records for four unchanged originals."""
from pathlib import Path
import sys,gzip
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from source import request
URL='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer'

def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-island-cheong-shing-four-primary-identity-v1-20261023';out=base/batch;assert not out.exists();out.mkdir();capture='government-xl-island-cheong-shing-four-original-runtime-v2-20261023';_,pins=authenticate(base/capture);p=base/capture/'selection.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];rows=read(p)['rows'];refs=[Path(__file__),base/capture/'result.json',p,HERE.parent/'landsd-territory/source.py']
    def query(name,table,where):
        raw,receipt=request(URL+'/'+str(table)+'/query',dict(f='json',where=where,outFields='*',returnGeometry='false',resultRecordCount='2000',orderByFields='OBJECTID'),json_expected=False)
        decoded=gzip.decompress(raw)if raw.startswith(b'\x1f\x8b')else raw
        p=out/(name+'.json');p.write_bytes(decoded);save(out/(name+'-request.json'),dict(**receipt,decodedSHA256=digest(decoded),gzipDecoded=raw!=decoded));data=read(p);assert not data.get('error')and not data.get('exceededTransferLimit');return [r['attributes']for r in data['features']]
    def quoted(xs):return ','.join("'"+x.replace("'","''")+"'"for x in sorted(xs))
    csuids={r['source']['building']['buildingCSUID']for r in rows};footprints=query('exact-footprints',0,'BuildingCSUID IN ('+quoted(csuids)+')');relations=query('exact-relations',1002,'BuildingCSUID IN ('+quoted(csuids)+')');ids={int(r['BuildingStructureID'])for r in relations};assert ids
    structures=query('exact-structures',1003,'BuildingStructureID IN ('+','.join(map(str,sorted(ids)))+')');permits={r['OPNo']for r in structures if r.get('OPNo')};permit_structures=query('complete-permit-structures',1003,'OPNo IN ('+quoted(permits)+')')if permits else []
    permitids={int(r['BuildingStructureID'])for r in permit_structures};permit_relations=query('complete-permit-relations',1002,'BuildingStructureID IN ('+','.join(map(str,sorted(permitids)))+')')if permitids else []
    reports=[]
    for r in rows:
        form=r['source']['building'];csuid=form['buildingCSUID'];matches=[f for f in footprints if f['BuildingCSUID']==csuid];assert len(matches)==1;f=matches[0];assert f['Status']=='Active'and f['BaseHeight']==form['base']and abs(f['TopHeight']-form['base']-form['height'])<1e-8
        links=[v for v in relations if v['BuildingCSUID']==csuid];sids={int(v['BuildingStructureID'])for v in links};related=[s for s in structures if int(s['BuildingStructureID'])in sids]
        reports.append(dict(uid=r['uid'],sourceSHA256=r['sourceSHA256'],exactCurrentCSUID=csuid,officialFootprint=f,structureLinks=links,structures=related,occupationPermits=sorted({s['OPNo']for s in related if s.get('OPNo')}),exactActiveRecordAndCurrentFormHeightMatch=True,sourceIdentityAccepted=False,supportApproved=False))
    result=dict(uids=[r['uid']for r in rows],rows=reports,completePermitStructures=permit_structures,completePermitRelations=permit_relations,sourceGeometryChanges=0,installationApproved=False,qualification='Fresh exact official CSUID, active status and base/top record match, including separately attributed adjacent podium. Complete nonempty occupation-permit membership retained. These metadata facts alone do not establish geometry-component coverage, legal ownership, support paths, placement or model acceptance.')
    save(out/'summary.json',result);module('three_primary_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'fresh-exact-four-source-primary-identity-records',refs,result);print([dict(uid=r['uid'],permits=r['occupationPermits'])for r in reports],flush=True)

if __name__=='__main__':main()

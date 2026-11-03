"""Fetch exact current-form government records; no source association or approval."""
import argparse,gzip,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from source import request,BASE as URL

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','scope']:p.add_argument('--'+k,required=True)
    p.add_argument('--uid',action='append',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args()
    assert all(n.startswith('government-xl-')and '/'not in n for n in [a.batch,a.scope])
    assert 0<len(a.uid)==len(set(a.uid))<=40
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;lp=HERE/'local'/a.batch/'reservation.json';assert not out.exists()
    if not a.owned:
        assert not lp.parent.exists();c=reservations.claim('exact-current-form-primary-'+str(uuid.uuid4()),['building:'+u for u in sorted(a.uid)],batch=a.batch,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
    lease=read(lp);assert reservations.owns(lease)
    _,pins=authenticate(base/a.scope);fp=base/a.scope/'form-obligations.json.gz';assert digest(fp.read_bytes())==pins[str(fp.relative_to(ROOT))]
    forms={r['uid']:r for r in read(fp)};assert set(a.uid)<=set(forms)
    forms={u:forms[u]for u in a.uid};csuids=sorted({r['buildingCSUID']for r in forms.values()});assert len(csuids)==len(forms)and all(s.isalnum()for s in csuids)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes());assert mh==pins[str(manifest.relative_to(ROOT))]
    refs=[Path(__file__),base/a.scope/'result.json',fp,manifest,HERE.parent/'landsd-territory/source.py']
    for row in forms.values():
        tile=ROOT/'3d-viewer/city/data/tiles'/(row['tile']+'.json');assert digest(tile.read_bytes())==pins[str(tile.relative_to(ROOT))];assert next(r for r in read(tile)['buildings']if r['uid']==row['uid'])==row;refs.append(tile)
    out.mkdir();save(out/'current-requested-forms.json',list(forms.values()))
    def query(name,table,where,geometry):
        raw,receipt=request(URL+'/'+str(table)+'/query',dict(f='json',where=where,outFields='*',returnGeometry='true'if geometry else'false',outSR='2326',resultRecordCount='1000',orderByFields='OBJECTID'),json_expected=False)
        decoded=gzip.decompress(raw)if raw.startswith(b'\x1f\x8b')else raw;path=out/(name+'.json');path.write_bytes(decoded);save(out/(name+'-request.json'),dict(**receipt,decodedSHA256=digest(decoded),gzipDecoded=decoded!=raw))
        if decoded!=raw:(out/(name+'-original.gz')).write_bytes(raw)
        result=read(path);assert not result.get('error')and not result.get('exceededTransferLimit');return result['features']
    where='BuildingCSUID IN ('+','.join("'"+s+"'"for s in csuids)+')'
    footprints=query('footprints',0,where,True);relations=query('relations',1002,where,False)
    ids=sorted({int(r['attributes']['BuildingStructureID'])for r in relations})
    structures=query('structures',1003,'BuildingStructureID IN ('+','.join(map(str,ids))+')',False)if ids else[]
    returned={r['attributes']['BuildingCSUID']for r in footprints};assert returned<=set(csuids)
    assert digest(manifest.read_bytes())==mh and reservations.owns(lease)
    result=dict(uids=sorted(forms),requestedCSUIDs=csuids,missingRequestedCSUIDs=sorted(set(csuids)-returned),footprints=len(footprints),relations=len(relations),structureIDs=ids,structures=len(structures),currentManifestSHA256=mh,sourceGeometryChanges=0,viewerIdentityAssigned=False,identityAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False,scriptExternalAICalls=0,qualification='Exact selected current BASIC-form records only. A record query does not assign an unmatched original to a UID, equate different CSUIDs, approve support, or alter current viewer data. Missing/revised primary records remain explicit.')
    save(out/'summary.json',result)
    module('current_form_primary_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-current-form-government-primary-records-only',refs,result)
    print({k:result[k]for k in ['footprints','relations','structureIDs','structures','missingRequestedCSUIDs']},flush=True)
if __name__=='__main__':main()

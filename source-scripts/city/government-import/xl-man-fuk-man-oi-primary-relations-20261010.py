"""Freeze exact primary relations and official plans; grant no identity credit."""
import datetime, gzip, json, urllib.request, urllib.error, uuid
import sys
from run import ROOT, HERE, save, digest, reservations
sys.path.insert(0, str(HERE.parent/'landsd-territory'))
from source import request, BASE

BATCH='government-xl-man-fuk-man-oi-primary-relations-20261010'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
UIDS=['landsd/266062:0','landsd/75697:0']
CSUIDS=['3644619608P20050726','3647219454T20050430']

def query(table, where, name, geometry=False):
    params=dict(f='json',where=where,outFields='*',returnGeometry='true' if geometry else 'false',
                outSR='2326',resultRecordCount='1000',orderByFields='OBJECTID')
    raw, receipt=request(BASE+'/'+str(table)+'/query',params,json_expected=False)
    decoded=gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw
    (DOC/(name+'.json')).write_bytes(decoded)
    if decoded!=raw:(DOC/(name+'.provider-original.gz')).write_bytes(raw)
    receipt.update(decodedSHA256=digest(decoded),gzipDecoded=decoded!=raw)
    save(DOC/(name+'.request.json'),receipt)
    obj=json.loads(decoded)
    assert not obj.get('error') and not obj.get('exceededTransferLimit'),obj
    return obj['features']

def fetch_pdf(name,url):
    receipt=dict(url=url,retrievedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'HongKongSandbox-source-provenance/1.0'})
        with urllib.request.urlopen(req,timeout=60) as response:
            raw=response.read();receipt.update(status=response.status,resolvedURL=response.url,responseHeaders=dict(response.headers))
        receipt.update(bytes=len(raw),sha256=digest(raw),isPDF=raw.startswith(b'%PDF-'))
        (DOC/(name if receipt['isPDF'] else name+'.non-pdf-response')).write_bytes(raw)
    except urllib.error.HTTPError as error:
        receipt.update(status=error.code,available=False)
    except urllib.error.URLError as error:
        receipt.update(available=False,requestError=str(error.reason))
    save(DOC/(name+'.request.json'),receipt)
    return receipt

def main():
    assert not DOC.exists(),'Never replace a frozen attempt'
    claim=reservations.claim('man-fuk-primary-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=3600)
    assert claim['ok'],claim
    try:
        DOC.mkdir(parents=True)
        manifest=ROOT/'3d-viewer/city/data/manifest.json';raw=manifest.read_bytes();msha=digest(raw)
        (DOC/'captured-manifest.json').write_bytes(raw)
        where='BuildingCSUID IN ('+','.join("'"+c+"'" for c in CSUIDS)+')'
        primary=query(0,where,'exact-current-primary',True)
        assert {r['attributes']['BuildingCSUID'] for r in primary}==set(CSUIDS)
        relations=query(1002,where,'exact-current-structure-relations')
        ids=sorted({r['attributes']['BuildingStructureID'] for r in relations})
        structures=query(1003,'BuildingStructureID IN ('+','.join(map(str,ids))+')','exact-current-structures') if ids else []
        plans=[fetch_pdf('ha-man-oi-block-k.pdf','https://www.housingauthority.gov.hk/hdw/content/static/file/b5/residential/plans/chunmancourt_bK.pdf'),
               fetch_pdf('ha-chun-man-estate-url-probe.pdf','https://www.housingauthority.gov.hk/hdw/content/static/file/b5/residential/plans/estate/Chun%20Man%20Court.pdf')]
        assert digest(manifest.read_bytes())==msha,'Changed live manifest during primary investigation'
        save(DOC/'diagnostic.json',dict(uids=UIDS,csuids=CSUIDS,primary=primary,relations=relations,structures=structures,
             plans=plans,capturedManifestSHA256=msha,identityAccepted=False,physicalAccepted=False,
             installationApproved=False,sourceGeometryChanges=0,aiGeometryModelling=False,
             qualification='Exact active source relationship investigation only. A guessed official site-plan URL is a documented probe, not evidence unless returned PDF content is independently inspected. No common ownership, support or estate-wide overlap exemption is inferred.'))
        print(dict(primaryRecords=len(primary),relations=len(relations),structures=len(structures),plans=[{k:r.get(k) for k in ['url','status','isPDF','available']} for r in plans]),flush=True)
    finally:
        assert reservations.release(claim['reservation'])['ok']

if __name__=='__main__':main()

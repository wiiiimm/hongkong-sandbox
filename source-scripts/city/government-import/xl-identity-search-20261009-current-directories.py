"""Fresh official package directory search for four unresolved source versions.
Directory provenance only; nearby source names never establish component ownership.
"""
import json,sys,concurrent.futures
from run import ROOT,HERE,read,save
sys.path.insert(0,str(HERE.parent/'landsd-territory'));from source import request
sys.path.insert(0,str(HERE.parent/'citywide-source'));from discover import scan
DOC=ROOT/'docs/astra-city/government-import/government-xl-identity-search-20261009'
LOCAL=HERE/'local/government-xl-identity-search-20261009'
URL='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1742809441342_98380/FeatureServer/0/query'
def main():
 hist=read(LOCAL/'unmapped-directory-history.json.gz')['rows'];sheets=sorted({r['historicalDirectories'][0]['sheet'] for r in hist})
 params={'f':'json','where':'SHEETNO IN ('+','.join("'"+s+"'" for s in sheets)+')','outFields':'*','returnGeometry':'false','resultRecordCount':'1000'}
 raw,receipt=request(URL,params);data=json.loads(raw);assert len(data['features'])==4 and not data.get('exceededTransferLimit')
 (DOC/'current-package-index.json').write_bytes(raw);save(DOC/'current-package-index.request.json',receipt)
 def work(f):
  a=f['attributes'];r,_=scan(a,LOCAL/'fresh-directories'/a['SHEETNO'],refresh=True);return r
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:current=list(pool.map(work,data['features']))
 out=[];contexts={r['modelId']:r for r in read(DOC/'unmapped-context.json.gz')['rows']}
 for old in hist:
  prior=old['historicalDirectories'][0];fresh=next(r for r in current if r['sheet']==prior['sheet']);mid=old['modelId'];geo=mid[1:11]
  oldmember=next(m for m in prior['directory']['models'] if m['modelId']==mid)
  exact=[m for m in fresh['models'] if m['modelId']==mid];neighbors={f['GeoRefNo'] for f in contexts[mid]['nearbyFeatures']}
  matched=[m for m in fresh['models'] if m['geoRefNo'] in neighbors or m['geoRefNo']==geo]
  same=bool(len(exact)==1 and [(x['name'],x['crc32'],x['decodedBytes']) for x in exact[0]['members']]==[(x['name'],x['crc32'],x['decodedBytes']) for x in oldmember['members']])
  out.append({'modelId':mid,'sheet':fresh['sheet'],'currentRevision':fresh['revision'],'sourceURL':fresh['sourceURL'],'etag':fresh['etag'],'directorySHA256':fresh['directorySHA256'],'sameOriginalMemberContents':same,'exactCurrentModels':exact,'nearbyCurrentModels':matched,'identityAccepted':False,'installationApproved':False})
  print(json.dumps({'modelId':mid,'sheet':fresh['sheet'],'sameMembers':same,'models':[m['modelId'] for m in matched]}),flush=True)
 save(DOC/'current-package-research.json.gz',{'rows':out,'qualification':'Fresh provider index and ETag-bound ZIP directory queries. Same CRC/length is member continuity evidence, not geometry identity approval. Nearby renamed models require explicit GIS lineage before assignment.'})
if __name__=='__main__':main()

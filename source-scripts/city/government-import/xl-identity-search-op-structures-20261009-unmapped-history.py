"""Exact old GeoRef prefix queries against provider names/works/OP relationships."""
import importlib.util
from run import ROOT,HERE,read,save
s=importlib.util.spec_from_file_location('official_op_queries',HERE/'xl-identity-search-op-structures-20261009-discover.py');q=importlib.util.module_from_spec(s);s.loader.exec_module(q)
def main():
 rows=read(ROOT/'docs/astra-city/government-import/government-xl-identity-search-20261009/unmapped-context.json.gz')['rows'];out=[]
 for r in rows:
  geo=r['modelId'][1:11];data={str(t):q.query(t,"BuildingCSUID LIKE '"+geo+"%'",'unmapped-history-'+geo+'-'+str(t)) for t in [1000,1001,1002]};out.append({'modelId':r['modelId'],'sourceKey':r['sourceKey'],'sourceSHA256':r['sourceSHA256'],'exactGeoRefPrefixHistory':data,'identityAccepted':False,'installationApproved':False})
 save(q.DOC/'unmapped-provider-history.json.gz',{'rows':out,'qualification':'Exact old GeoRef prefix query, including names/works/occupation-structure relations. Empty results cannot prove demolition or absence of unexposed reassignment/merge/split lineage.'})
 print([(r['modelId'],{k:len(v) for k,v in r['exactGeoRefPrefixHistory'].items()}) for r in out],flush=True)
if __name__=='__main__':main()

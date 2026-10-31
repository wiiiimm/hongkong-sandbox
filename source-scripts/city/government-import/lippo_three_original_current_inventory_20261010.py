"""Exactly three current native originals and complete current catalogue census.

Recovered Silvercord remains source evidence, not an installed replacement.
"""
import json
from run import ROOT,NATIVE_RUN,digest
EXPECTED={
 'landsd/231645:0':('B355141753102063C0','cfe390f024ac815a8c8ae3f422724fd72e4cd5c164e7325f9404cd81fc1b46da',13725),
 'landsd/233997:0':('B355041762402063C0','11b03482304ea9f139e6863d259891f06aecc5def1df2e18abd921e0a0aebc5d',12258),
 'landsd/239465:0':('B355181755401063C0','2ca41f96bdce41f47c95891182450878c1fc694b12c3ae22bbeb29ff07cc276c',3597)}
def native_rows(connection):
 prefixes=[v[0][1:11] for v in EXPECTED.values()]
 return [dict(sourceKey=key+'/'+model['modelId'],model=model,resultSHA256=sha) for key,model,sha in connection.execute("SELECT r.cache_key,m,r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members s USING(cache_key),LATERAL jsonb_array_elements(r.result->'models')m WHERE s.run_id=%s AND substring(m->>'modelId',2,10)=ANY(%s) ORDER BY r.cache_key,m->>'modelId'",(NATIVE_RUN,prefixes)).fetchall()]
def verify_native_rows(rows):
 assert len(rows)==3 and len({r['sourceKey'] for r in rows})==3,'Three unique current native source versions required'
 by={r['model']['modelId']:r for r in rows};assert len(by)==3 and set(by)=={v[0] for v in EXPECTED.values()}
 for uid,(mid,sha,count) in EXPECTED.items():
  r=by[mid];assert r['model']['asset']['sha256']==sha and r['model']['triangles']==count
  assert len(r['sourceKey'].split('/'))==2 and r['sourceKey'].endswith('/'+mid)
 return True

def catalogue_inventory(manifest_bytes,read_bytes=lambda p:p.read_bytes()):
 manifest=json.loads(manifest_bytes);urls=manifest['officialModelCatalogues'];assert len(urls)==len(set(urls))
 hashes={};matches=[]
 for url in urls:
  path=(ROOT/'3d-viewer'/url).resolve();assert path.is_relative_to((ROOT/'3d-viewer').resolve())
  raw=read_bytes(path);hashes[url]=digest(raw);cat=json.loads(raw);assert isinstance(cat['models'],list)
  for entry in cat['models']:
   if entry['uid'] in EXPECTED:matches.append(dict(catalogue=url,entry=entry))
 assert not matches,'All three are recovered evidence only; unexpected installed actor requires a new current route'
 return dict(completeCatalogueHashes=hashes,matchingInstalledEntries=matches,threeOriginalsInstalled=False)

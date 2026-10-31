"""Unique current original source and complete live installed foreign inventory."""
import json
from pathlib import Path
from run import ROOT,NATIVE_RUN,digest
from one_peking_installed_hullett_finite_silhouette_identity_20261010 import OWN,FOREIGN,OWN_SHA,FOREIGN_SHA
MODEL='B355121744602063C0'
def native_rows(connection):
 return [dict(sourceKey=key+'/'+model['modelId'],model=model,resultSHA256=sha) for key,model,sha in connection.execute("SELECT r.cache_key,m,r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members s USING(cache_key),LATERAL jsonb_array_elements(r.result->'models')m WHERE s.run_id=%s AND m->>'modelId' LIKE 'B3551217446%%' ORDER BY r.cache_key,m->>'modelId'",(NATIVE_RUN,)).fetchall()]
def verify_native_rows(rows):
 assert len(rows)==1,'Exactly one current source version required'
 r=rows[0];assert r['model']['modelId']==MODEL and r['model']['asset']['sha256']==OWN_SHA and r['model']['triangles']==4114
 assert len(r['sourceKey'].split('/'))==2 and r['sourceKey'].endswith('/'+MODEL)
 return True
def installed_inventory(manifest_bytes,read_bytes=lambda p:p.read_bytes()):
 manifest=json.loads(manifest_bytes);urls=manifest['officialModelCatalogues'];assert len(urls)==len(set(urls))
 hashes={};matches=[]
 for url in urls:
  p=(ROOT/'3d-viewer'/url).resolve();assert p.is_relative_to((ROOT/'3d-viewer').resolve())
  raw=read_bytes(p);hashes[url]=digest(raw);cat=json.loads(raw)
  assert isinstance(cat['models'],list)
  for entry in cat['models']:
   if entry['uid']!=FOREIGN:continue
   e=dict(entry,rootTranslation=cat['rootTranslation'])
   path=(p.parent/entry['asset']).resolve();assert path.is_relative_to((ROOT/'3d-viewer').resolve())
   blob=read_bytes(path);assert digest(blob)==FOREIGN_SHA==entry['sha256']
   matches.append(dict(catalogue=url,catalogueSHA256=digest(raw),entry=e,assetPath=str(path.relative_to(ROOT)),assetSHA256=digest(blob)))
 assert len(matches)==1,'Exactly one complete live installed Hullett entry required'
 return dict(completeCatalogueHashes=hashes,installedForeign=matches[0])

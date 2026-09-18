"""Reproduce the bounded retained-source inventory without additional downloads."""
import gzip,hashlib,json,pathlib,sys,zipfile
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/ting-kau'
sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'));from prepare_model_sample import model_geometry
sha=lambda data:hashlib.sha256(data).hexdigest()
def inventory():
 rows=[];caches=[]
 for category,location in [('infrastructure',HERE/'sources'),('tower-identity',HERE/'towers/sources'),('individualised',HERE/'individual/sources'),('terrain',HERE/'terrain/sources')]:
  for folder in sorted(location.iterdir()):
   meta=json.loads((folder/'download.json').read_text());archive=folder/(folder.name+'.zip');assert sha(archive.read_bytes())==meta['sha256']
   caches.append({'category':category,'sheet':folder.name,'sourceUrl':meta['source'],'sourceRevision':meta['revisionDate'],'cacheBytes':meta['bytes'],'cacheSha256':meta['sha256'],'cacheKind':meta['cacheKind'],'remoteArchiveSha256':meta.get('archiveSha256'),'originalEntries':len(meta['entries'])})
   with zipfile.ZipFile(archive) as z:
    for e in meta['entries']:assert sha(z.read(e['name']))==e['sha256']
    if category=='terrain':continue # Existing terrain-staging.json already inventories source TINs.
    for entry in sorted(n for n in z.namelist() if n.endswith('.gltf')):
     d=json.loads(z.read(entry));parent=pathlib.PurePosixPath(entry).parent;p,t=model_geometry(d,lambda uri:z.read(str(parent/uri)))
     rows.append({'category':category,'id':pathlib.PurePosixPath(entry).stem,'sheet':folder.name,'entry':entry,'bounds':[p.min(axis=0).tolist(),p.max(axis=0).tolist()],'triangles':t})
 a=next(r for r in rows if r['id']=='I259872443407063C0');b=next(r for r in rows if r['id']=='I259872443407063A0');assert a['triangles']==b['triangles']==16995
 factsheet=HERE/'hyd-ting-kau-factsheet.pdf'
 report={'sourceScopeHK1980':[825850,824200,826800,825550],'models':rows,'caches':caches,'counts':{k:sum(r['category']==k for r in rows) for k in ['infrastructure','tower-identity','individualised']},'retainedEntryHashesVerified':True,'publishedModelId':a['id'],'individualisedComparison':{'sourceModelId':b['id'],'sourceTriangles':b['triangles'],'maximumBoundsDifferenceMetres':max(abs(x-y) for aa,bb in zip(a['bounds'],b['bounds']) for x,y in zip(aa,bb)),'interpretation':'Both versions contain the deck and three towers. Source inspection shows no inclined stay cables. The separate low GENERIC object is omitted.'},'primaryFactsheet':{'sourceUrl':'https://www.hyd.gov.hk/en/information_corner/hyd_factsheets/doc/e_Ting_Kau_Bridge.pdf','path':str(factsheet.relative_to(ROOT)),'bytes':factsheet.stat().st_size,'sha256':sha(factsheet.read_bytes())},'livePublished':False}
 (DOC/'source-inventory.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'counts':report['counts'],'caches':len(caches),'boundsDifference':report['individualisedComparison']['maximumBoundsDifferenceMetres']}));return report
if __name__=='__main__':inventory()

"""Verify retained original entries and inventory native Stonecutters geometry."""
import hashlib,json,pathlib,sys,zipfile
import numpy as np
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/stonecutters'
sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'))
from prepare_model_sample import model_geometry

def inventory():
    models=[];caches=[]
    for category,location in [('infrastructure',HERE/'sources'),('tower-identity',HERE/'towers/sources'),('individualised',HERE/'individual/sources'),('terrain',HERE/'terrain/sources')]:
        for folder in sorted(location.glob('*')):
            if not (folder/'download.json').exists():continue
            meta=json.loads((folder/'download.json').read_text());archive=folder/(folder.name+'.zip');assert hashlib.sha256(archive.read_bytes()).hexdigest()==meta['sha256']
            with zipfile.ZipFile(archive) as z:
                for e in meta['entries']:assert hashlib.sha256(z.read(e['name'])).hexdigest()==e['sha256']
                caches.append({'category':category,'sheet':folder.name,'sourceUrl':meta['source'],'sourceRevision':meta['revisionDate'],'cacheSha256':meta['sha256'],'cacheBytes':meta['bytes'],'cacheKind':meta['cacheKind'],'originalEntries':len(meta['entries'])})
                if category=='terrain':continue
                for entry in sorted(n for n in z.namelist() if n.endswith('.gltf')):
                    d=json.loads(z.read(entry));parent=pathlib.PurePosixPath(entry).parent;p,t=model_geometry(d,lambda uri:z.read(str(parent/uri)))
                    rows=np.unique(p,axis=0);models.append({'category':category,'id':pathlib.PurePosixPath(entry).stem,'sheet':folder.name,'entry':entry,'bounds':[p.min(axis=0).tolist(),p.max(axis=0).tolist()],'triangles':t,'uniqueVertices':len(rows),'highestVertices':rows[rows[:,1]>rows[:,1].max()-.02].tolist()[:80]})
    report={'scopeHK1980':[829450,820000,831100,821450],'models':models,'caches':caches,'retainedSourceHashesVerified':True,'livePublished':False}
    (DOC/'source-inventory.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps([{'id':m['id'],'sheet':m['sheet'],'triangles':m['triangles'],'bounds':m['bounds']} for m in models],indent=2));return report
if __name__=='__main__':inventory()

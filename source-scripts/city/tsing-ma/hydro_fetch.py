"""Retain bounded official land/sea source layers for the bridge channel."""
import subprocess,pathlib,json,urllib.parse,urllib.request,hashlib,zipfile,gzip,datetime
HERE=pathlib.Path(__file__).resolve().parent
BOUNDS=[824200,823000,826900,824000]
def fetch():
 index=HERE/'hydro-index.json';url='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637224243141_96556/MapServer/0/query?'+urllib.parse.urlencode(dict(f='json',geometry=','.join(map(str,BOUNDS)),geometryType='esriGeometryEnvelope',inSR=2326,outSR=2326,outFields='*',returnGeometry='true'))
 if not index.exists():index.write_bytes(urllib.request.urlopen(url,timeout=60).read())
 index.with_suffix('.request.txt').write_text(url+'\n');folder=HERE/'hydro-sources';folder.mkdir(exist_ok=True)
 for f in json.loads(index.read_text())['features']:
  a=f['attributes'];sheet=a['SHEETNO'];archive=folder/(sheet+'.zip');meta=folder/(sheet+'-download.json')
  if not archive.exists():subprocess.run(['curl','--fail','--silent','--show-error','--location','--max-time','120','--output',str(archive),a['GML']],check=True)
  entries=[]
  with zipfile.ZipFile(archive) as z:
   for layer in ['Relief/ContourPoly','Hydrography/HydrographyPoly','Hydrography/HydrographyLine','Transportation/RoadPoly']:
    name=sheet+'/Layers/'+layer+'.gml';raw=z.read(name);dest=folder/(sheet+'-'+layer.split('/')[-1]+'.gml.gz');dest.write_bytes(gzip.compress(raw,mtime=0));entries.append({'entry':name,'file':dest.name,'sha256':hashlib.sha256(raw).hexdigest()})
  record={'attributes':a,'archiveBytes':archive.stat().st_size,'archiveSha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'fetchedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'entries':entries}
  if meta.exists():record['fetchedAt']=json.loads(meta.read_text())['fetchedAt']
  meta.write_text(json.dumps(record,indent=2)+'\n');print(sheet,record['archiveBytes'],flush=True)
if __name__=='__main__':fetch()

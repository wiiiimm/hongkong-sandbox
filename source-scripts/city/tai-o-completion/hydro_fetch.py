"""Retain bounded public iB1000 sheets and compact original hydro GML layers."""
import concurrent.futures,datetime,gzip,hashlib,json,pathlib,subprocess,zipfile
HERE=pathlib.Path(__file__).resolve().parent
LAYERS=['Hydrography/HydroPolygon','Hydrography/HydroLine','Hydrography/Shoreline','Hydrography/CartoHydroLine','LandCover/LandCoverVector2']
def fetch(feature):
 a=feature['attributes'];tile=a['SHEETNO'];folder=HERE/'hydro-sources';path=folder/(tile+'.zip');record=folder/(tile+'-download.json');url=a['GML']
 if not path.exists():
  subprocess.run(['curl','--fail','--silent','--show-error','--location','--max-time','120','--output',str(path),url],check=True)
 with zipfile.ZipFile(path) as z:
  entries=[]
  for name in LAYERS:
   source=tile+'/Layers/'+name+'.gml'
   if source not in z.namelist():continue
   raw=z.read(source);dest=folder/(tile+'-'+name.split('/')[-1]+'.gml.gz');dest.write_bytes(gzip.compress(raw,mtime=0));entries.append({'file':dest.name,'sourceEntry':source,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
 report={'sheet':a,'sourceIndex':'../hydro-index.json','downloadURL':url,'archiveBytes':path.stat().st_size,'archiveSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'fetchedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'entries':entries,'transport':'Public direct download; curl with system TLS certificate validation. Original full ZIP retained as ignored cache.'}
 if record.exists():report['fetchedAtUTC']=json.loads(record.read_text()).get('fetchedAtUTC',report['fetchedAtUTC'])
 record.write_text(json.dumps(report,indent=2)+'\n');print(tile,path.stat().st_size,flush=True);return report
if __name__=='__main__':
 features=json.loads((HERE/'hydro-index.json').read_text())['features']
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(fetch,features))
 (HERE/'hydro-source-manifest.json').write_text(json.dumps({'provider':'Lands Department / HKSAR Government','dataset':'iB1000 Digital Topographic Map','datasetId':'landsd_rcd_1637223748322_25497','selectionBoundsHK1980':[802700,812300,804650,813750],'crs':'EPSG:2326','gmlAxes':'N,E,third-coordinate (preserved but not used as bathymetry)','sources':rows},indent=2)+'\n')

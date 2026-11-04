"""Small source/provenance helpers for reusing the retained official download."""
from __future__ import annotations
import datetime,gzip,hashlib,json,pathlib,re,time,urllib.parse,urllib.request

HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[2]
DOCS=ROOT/'docs/astra-city/landsd-territory'
BASE='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer'
DATASET='landsd_rcd_1637211194312_35158'
META=f'https://portal.csdi.gov.hk/csdi-webpage/metadata/{DATASET}/html'
SPEC='https://static.csdi.gov.hk/csdi-webpage/view/common/6eda6a766520bcffe13206378c060a59bdb54a3c6f92480b1f01174d25fd7194'
AGENT='HongKongSandbox-Astra/territory-building-source (CSDI public data, three bounded readers)'

def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def digest(raw):return hashlib.sha256(raw).hexdigest()
def encode(obj):return json.dumps(obj,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
def atomic(path,raw):
 path.parent.mkdir(parents=True,exist_ok=True);temporary=path.with_name(path.name+'.tmp');temporary.write_bytes(raw);temporary.replace(path)
def save_json(path,obj):atomic(path,json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False).encode()+b'\n')
def read_json(path):return json.loads(gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes())

def request(url,parameters=None,method='GET',json_expected=True):
 body=urllib.parse.urlencode(parameters or {}).encode()
 full=url+('?' +body.decode() if method=='GET' and body else '')
 attempts=[]
 for attempt in range(5):
  started=utc();clock=time.monotonic()
  try:
   headers={'User-Agent':AGENT}
   if method=='POST':headers['Content-Type']='application/x-www-form-urlencoded'
   req=urllib.request.Request(full,data=body if method=='POST' else None,headers=headers)
   with urllib.request.urlopen(req,timeout=60) as response:
    raw=response.read();response_headers={key:response.headers[key] for key in ['Date','ETag','Last-Modified','Content-Type','Content-Length'] if response.headers.get(key)}
   obj=json.loads(raw) if json_expected else None
   if isinstance(obj,dict) and obj.get('error'):raise ValueError('ArcGIS error '+str(obj['error']))
   return raw,{'url':url,'method':method,'parameters':parameters or {},'startedAtUTC':started,'retrievedAtUTC':utc(),'elapsedSeconds':round(time.monotonic()-clock,3),'bytes':len(raw),'sha256':digest(raw),'responseHeaders':response_headers,'earlierAttempts':attempts}
  except Exception as exc:
   attempts.append({'startedAtUTC':started,'error':str(exc)})
   if attempt==4:raise RuntimeError(f'{method} {url} failed: {attempts}') from exc
   time.sleep(min(12,2**attempt))

def retained(filename,url,parameters=None,json_expected=True):
 path=HERE/filename;meta=path.with_name(path.name+'.request.json')
 if path.exists() and meta.exists():return path.read_bytes(),read_json(meta)
 raw,info=request(url,parameters,json_expected=json_expected);atomic(path,raw);save_json(meta,info);return raw,info

def version(html):
 versions=set(re.findall(r'Building_Outline_Public_v(\d{8})',html))
 if len(versions)!=1:raise ValueError('Expected one advertised dataset version, got '+str(versions))
 return 'Building_Outline_Public_v'+versions.pop()

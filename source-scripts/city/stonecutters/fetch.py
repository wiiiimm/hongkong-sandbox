"""Stonecutters source queries + the existing original-entry range downloader."""
import argparse,datetime,hashlib,importlib.util,json,pathlib,urllib.parse,urllib.request
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BOUNDS=[829450,820000,831100,821450]
DATASETS={'models':('landsd_rcd_1742809441342_98380','FeatureServer'),'individual':('landsd_rcd_1671676915450_88604','FeatureServer'),'hydro':('landsd_rcd_1637224243141_96556','MapServer')}

def index(kind='models'):
    dataset,server=DATASETS[kind];name='index' if kind=='models' else kind+'-index';path=HERE/(name+'.json')
    if not path.exists():
        query=urllib.parse.urlencode({'f':'json','geometry':','.join(map(str,BOUNDS)),'geometryType':'esriGeometryEnvelope','inSR':2326,'spatialRel':'esriSpatialRelIntersects','outFields':'*','returnGeometry':'true','outSR':2326})
        url=f'https://portal.csdi.gov.hk/server/rest/services/common/{dataset}/{server}/0/query?'+query
        with urllib.request.urlopen(url,timeout=60) as r:raw=r.read();headers=dict(r.headers)
        omitted=[key for key in headers if key.lower() in {'set-cookie','authorization','proxy-authorization'}]
        headers={key:value for key,value in headers.items() if key not in omitted}
        d=json.loads(raw);assert d.get('features') and not d.get('exceededTransferLimit')
        path.write_bytes(raw);(HERE/(name+'.request.txt')).write_text(url+'\n')
        (HERE/(name+'.source.json')).write_text(json.dumps({'url':url,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'retrievedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'headers':headers,'omittedResponseHeaders':omitted},indent=2)+'\n')
    return path

def fetch(folder='sources',prefixes=None,tiles=None,individual=False):
    spec=importlib.util.spec_from_file_location('shared_fetch',HERE.parent/'mui-wo-models/fetch.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    target=HERE if folder=='sources' else HERE/folder;target.mkdir(parents=True,exist_ok=True)
    p=index('individual' if individual else 'models')
    if target!=HERE:(target/'index.json').write_bytes(p.read_bytes())
    data=json.loads(p.read_text());selected=tiles or [f['attributes']['SHEETNO'] for f in data['features']]
    m.fetch_tiles(here=target,tiles=selected,member_prefixes=prefixes or ['INFRASTRUCTURE/'])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--index-only',action='store_true');p.add_argument('--folder',default='sources');p.add_argument('--prefix',action='append');p.add_argument('--tile',action='append');p.add_argument('--individual',action='store_true');a=p.parse_args()
    if a.index_only:
        for kind in DATASETS:print(kind,index(kind))
    else:fetch(a.folder,a.prefix,a.tile,a.individual)

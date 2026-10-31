"""Stage narrow Pui O native-TIN corrections without editing live terrain."""
import collections,gzip,hashlib,importlib.util,json,math,pathlib,sys
import numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/pui-o-detail-completion';BASE=HERE.parent/'pui-o-completion';TERRAIN=HERE/'terrain';TARGETS=['landsd/11179:0','landsd/182169:0'];TILES=['14-NW-6B','13-NE-5D','13-NE-5B']
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def load(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,separators=(',',':'))+'\n')
sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'))
from prepare_model_sample import stage
from resample_model_terrain import terrain_index
fine=module('puio_shared_fine',HERE.parent/'mui-wo-buildings/fine_terrain_audit.py')
# Reuse native TIN barycentric sampling and exact piece-audit functions unchanged.
old_path=list(sys.path);sys.path.insert(0,str(HERE.parent/'mui-wo-final-review'))
previous_audit_module=sys.modules.get('audit');shared_audit=module('puio_shared_native_audit',HERE.parent/'mui-wo-final-review/audit.py');sys.modules['audit']=shared_audit
shared_refine=module('puio_shared_refine',HERE.parent/'mui-wo-final-review/refine.py');sys.path[:]=old_path
if previous_audit_module is None:sys.modules.pop('audit',None)
else:sys.modules['audit']=previous_audit_module

def fetch():
 TERRAIN.mkdir(exist_ok=True);index=load(HERE/'index.json');index['features']=[f for f in index['features'] if f['attributes']['SHEETNO'] in TILES];assert len(index['features'])==len(TILES);save(TERRAIN/'index.json',index)
 module('puio_shared_fetch',HERE.parent/'mui-wo-models/fetch.py').fetch_tiles(TERRAIN,TILES,['TERRAIN'])
 for tile in TILES:
  folder=TERRAIN/'sources'/tile;download=load(folder/'download.json');assert all(e['name'].startswith('TERRAIN') for e in download['entries']);out=TERRAIN/'staged'/tile
  if not (out/'manifest.json').exists():stage(folder/(tile+'.zip'),download,BASE/'official-selection.json.gz',out)

def build():
 baseline=ROOT/'3d-viewer/city/data/terrain-pui-o.json';parent=load(baseline);g=parent['meta']['georef'];old=fine.DemSampler(parent,rendered=True);raw_sampler=fine.DemSampler(parent);buildings={b['uid']:b for b in load(BASE/'building-selection.json.gz')['buildings']};models={m['uid']:m for m in load(HERE/'compact/catalogue.json')['models']};patches=[];rows=[]
 for n,uid in enumerate(TARGETS):
  b=buildings[uid];poly=Polygon(b['rings'][0],b['rings'][1:]);x0,z0,x1,z1=poly.buffer(15).bounds;c0=math.floor((x0+834500-g['bE'])/5);r0=math.floor((816500-z0-g['bN'])/-5);c1=math.ceil((x1+834500-g['bE'])/5);r1=math.ceil((816500-z1-g['bN'])/-5);x0=g['bE']+c0*5-834500;z0=816500-g['bN']+r0*5;x1=g['bE']+c1*5-834500;z1=816500-g['bN']+r1*5;extent=box(x0,z0,x1,z1);w=round(x1-x0)+1;h=round(z1-z0)+1;items=[];native_audits=[];sources=[]
  for folder in [*sorted((BASE/'staged').iterdir()),*sorted((TERRAIN/'staged').iterdir())]:
   if not (folder/'manifest.json').exists():continue
   m=load(folder/'manifest.json');bounds=m['terrain']['worldBounds']
   if not extent.intersects(box(bounds[0][0],bounds[0][2],bounds[1][0],bounds[1][2])):continue
   m,s,t,v,usable,tree=terrain_index(folder);items.append({'usable':usable,'tree':tree});sources.append({'manifest':str((folder/'manifest.json').relative_to(ROOT)),'tile':m['tile'],'revision':m['tileRevision'],'sourceHashes':s['sourceHashes']});metrics,_,_=shared_audit.source_piece_audit(poly,models[uid]['worldBounds'][1][1],(usable,tree));native_audits.append({'tile':m['tile'],**metrics})
  xx,zz=np.meshgrid(np.arange(w)+x0,np.arange(h)+z0);points=np.c_[xx.ravel(),zz.ravel()];native,hits=shared_refine.source_samples(points,items);elev=[];rendered=[];vegetation=[];changed_water=0;boundary_error=0
  for i,(x,z) in enumerate(points):
   c=i%w;r=i//w;old_y=old.ground(x,z);old_raw=raw_sampler.ground(x,z);alpha=min(1,min(c,r,w-1-c,h-1-r)/7.5)
   if not np.isfinite(native[i]) or old_raw<=0:alpha=0
   y=float(native[i]*alpha+old_y*(1-alpha)) if alpha else old_y
   # Keep non-positive raw mask and exact existing water display separately.
   raw=old_raw if old_raw<=0 else y;elev.append(round(raw,6));rendered.append(round(y,6));cc=min(parent['w']-1,max(0,round((x+834500-g['bE'])/5)));rr=min(parent['h']-1,max(0,round((816500-z-g['bN'])/-5)));vegetation.append(parent['vegetation'][rr*parent['w']+cc])
   if old_raw<=0 and raw>0:changed_water+=1
   if c in [0,w-1] or r in [0,h-1]:boundary_error=max(boundary_error,abs(y-old_y))
  patch={'id':f'pui-o-detail-refinement-{n+1}','w':w,'h':h,'cell':1,'elev':elev,'renderedElev':rendered,'vegetation':vegetation,'coarseCells':[c0,r0,c1,r1],'meta':{'title':'Pui O · source TIN detail correction','georef':{'aE':1,'aN':-1,'bE':x0+834500,'bN':816500-z0,'W':w,'H':h},'targetUids':[uid],'parentTerrain':'city/data/terrain-pui-o.json','parentSha256':sha(baseline),'transitionMetres':7.5,'source':{'provider':'Lands Department / HKSAR Government','crs':'EPSG:2326','verticalDatum':'HKPD','nativeSources':sources,'policy':'Actual original TIN sampled barycentrically at 1 m intervals. 7.5 m outer display transition joins unmodified parent triangles. Existing raw water mask/display retained. 1 m is sample spacing, not surveyed accuracy. No building elevations changed.'}}};new=fine.DemSampler(patch,rendered=True);before=old.extrema(poly);after=new.extrema(poly);roof=models[uid]['worldBounds'][1][1];rows.append({'uid':uid,'sourceRoof':roof,'before':before,'after':after,'nativeSource':native_audits,'resolved':bool(roof>=after['max']-.1),'gridVertices':w*h,'sourceCovered':int(np.isfinite(native).sum()),'waterMaskNodesChanged':changed_water,'boundaryError':boundary_error});patches.append(patch);save(HERE/'source-grids'/(patch['id']+'.json'),{'w':w,'h':h,'meta':{'georef':patch['meta']['georef']},'elev':[float(v) if np.isfinite(v) else None for v in native],'source':sources,'method':'Original TIN samples before display transition'});print(uid,rows[-1],flush=True)
 bundle={'schemaVersion':1,'kind':'nested-source-terrain-refinements','parentTerrainURL':'city/data/terrain-pui-o.json','parentSha256':sha(baseline),'patches':patches,'integration':'Attach to existing parent data.patches; parent coarseCells refer to 5 m lattice. Shared renderer must omit these parent cells and draw children exactly once. No building source fields change.'};save(HERE/'terrain-refinements.json',bundle);(DOC/'terrain-preparation.json').write_text(json.dumps({'staged':True,'parentSha256':sha(baseline),'refinementSha256':sha(HERE/'terrain-refinements.json'),'bytes':(HERE/'terrain-refinements.json').stat().st_size,'rows':rows,'sourceTransferredBytes':sum(load(TERRAIN/'sources'/t/'download.json')['transferredBytes'] for t in TILES)},indent=2)+'\n')
if __name__=='__main__':fetch() if 'fetch' in sys.argv else build()

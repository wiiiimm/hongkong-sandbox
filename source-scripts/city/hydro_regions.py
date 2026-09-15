"""Combine disjoint regional hydro packages without duplicating geometry arrays.

Each region retains its original metadata and ranges into unchanged flat arrays.
Original regional records can be reconstructed exactly. No new banks, elevations,
polygons or cut cells are generated here; overlapping scopes require source review.
"""
import argparse,hashlib,json,math,pathlib
ARRAYS=('water','terrainCuts','bedTriangles','bankTriangles')

def regions_of(hydro):
 if not hydro:return []
 if hydro.get('region')!='composite':return [hydro]
 records=[]
 for region in hydro['regions']:
  record={k:v for k,v in region.items() if k!='geometryRanges'}
  for key in ARRAYS:
   start,length=region['geometryRanges'][key];record[key]=hydro[key][start:start+length]
   if len(record[key])!=length:raise ValueError('Invalid composite range '+key)
  records.append(record)
 return records

def combine(hydros):
 byid={}
 for hydro in hydros:
  for region in regions_of(hydro):
   id=region.get('region');bounds=region.get('bounds')
   if not isinstance(id,str) or not id or id=='composite' or region.get('schemaVersion')!=1 or not isinstance(bounds,list) or len(bounds)!=4 or not all(isinstance(v,(int,float)) and math.isfinite(v) for v in bounds) or bounds[0]>=bounds[2] or bounds[1]>=bounds[3]:raise ValueError('Invalid regional hydro metadata')
   if 'geometryRanges' in region or not all(isinstance(region.get(k),list) for k in ARRAYS):raise ValueError('A complete derived regional hydro payload is required')
   if not isinstance(region.get('illustrativeBed'),(int,float)) or not math.isfinite(region['illustrativeBed']):raise ValueError('Invalid illustrative bed')
   byid[id]=region
 records=list(byid.values());owned={}
 for i,region in enumerate(records):
  a=region['bounds']
  for other in records[i+1:]:
   b=other['bounds']
   if max(a[0],b[0])<min(a[2],b[2]) and max(a[1],b[1])<min(a[3],b[3]):raise ValueError('Overlapping hydro study bounds require review: '+region['region']+' / '+other['region'])
  for group in region['terrainCuts']:
   for cell in group['cells']:
    key=(group['georef']['aE'],group['georef']['aN'],round(cell['x'],6),round(cell['z'],6))
    if key in owned:raise ValueError('Overlapping terrain cut ownership: '+owned[key]+' / '+region['region'])
    owned[key]=region['region']
 if not records:raise ValueError('No regional hydro to combine')
 if len(records)==1:return records[0]
 out={'schemaVersion':1,'region':'composite','bounds':[min(r['bounds'][0] for r in records),min(r['bounds'][1] for r in records),max(r['bounds'][2] for r in records),max(r['bounds'][3] for r in records)],'illustrativeBed':records[0]['illustrativeBed'] if len({r['illustrativeBed'] for r in records})==1 else None,'source':{'derivation':'Disjoint source-derived regional packages; original metadata and array ranges retained per region. Union bounds are an index extent, never a land polygon.'},'regions':[],**{k:[] for k in ARRAYS}}
 for region in records:
  meta={k:v for k,v in region.items() if k not in ARRAYS};meta['geometryRanges']={}
  for key in ARRAYS:
   meta['geometryRanges'][key]=[len(out[key]),len(region[key])];out[key].extend(region[key])
  out['regions'].append(meta)
 assert regions_of(out)==records,'Regional source reconstruction must be lossless'
 return out

def compose_terrain(base,updates):
 return {**base,'hydro':combine([base.get('hydro'),*updates])}

def write(path,value):
 raw=(json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode();temporary=path.with_suffix(path.suffix+'.tmp');temporary.write_bytes(raw);temporary.replace(path);return hashlib.sha256(raw).hexdigest()

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--base-terrain',type=pathlib.Path,required=True);ap.add_argument('--region',type=pathlib.Path,action='append',required=True);ap.add_argument('--output',type=pathlib.Path,required=True);args=ap.parse_args()
 base=json.loads(args.base_terrain.read_text());updates=[json.loads(p.read_text()) for p in args.region];out=compose_terrain(base,updates);assert {k:v for k,v in out.items() if k!='hydro'}=={k:v for k,v in base.items() if k!='hydro'}
 digest=write(args.output,out);print(json.dumps({'regions':[r['region'] for r in regions_of(out['hydro'])],'output':str(args.output),'sha256':digest,'bytes':args.output.stat().st_size,'rawTerrainUnchanged':True,'sourceRecordsLossless':True}))
if __name__=='__main__':main()

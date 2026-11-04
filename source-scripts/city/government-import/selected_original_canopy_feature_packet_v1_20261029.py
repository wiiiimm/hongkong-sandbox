"""Bind an explicit original/canopy pair to fresh primary records and roof components."""
import argparse,gzip,sys,uuid
from pathlib import Path
import numpy as np,shapely
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from source import request
URL='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer'

def main():
    p=argparse.ArgumentParser()
    for key in ['batch','runtime','scope','uid','basic']:p.add_argument('--'+key,required=True)
    p.add_argument('--owned',action='store_true');a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch and a.uid!=a.basic
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;lp=HERE/'local'/(a.batch+'-runner')/'reservation.json';assert not out.exists()
    if not a.owned:
        assert not lp.parent.exists();c=reservations.claim('canopy-feature-packet-'+str(uuid.uuid4()),['building:'+a.uid,'building:'+a.basic,'terrain:city/data/terrain.json'],batch=a.batch,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
    lease=read(lp);assert reservations.owns(lease);refs=[Path(__file__)];pins={}
    def take(n,p):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    selection=take(a.runtime,base/a.runtime/'selection.json.gz');row=next(r for r in selection['rows']if r['uid']==a.uid);asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset);tri=decode_original_world_triangles(asset.read_bytes())
    items=take(a.scope,base/a.scope/(a.uid.split('/')[1]+'-forms.json.gz'));b=next(r['building']for r in items if r['building']['uid']==a.basic)
    assert b['structureType']=='Open-sided Structure'and b['baseSource']=='terrain-estimated'and b['heightSource']=='estimated'and b['baseHeightHKPD']is None and b['topHeightHKPD']is None
    forms={a.uid:row['source']['building'],a.basic:b}
    for uid,form in forms.items():
        tile=ROOT/'3d-viewer/city/data/tiles'/(form['tile']+'.json');assert next(r for r in read(tile)['buildings']if r['uid']==uid)==form;refs.append(tile)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest);out.mkdir()
    def query(name,layer,csuid,geometry):
        assert csuid.isalnum();params=dict(f='json',where="BuildingCSUID='"+csuid+"'",outFields='*',returnGeometry='true'if geometry else'false',outSR='2326')
        raw,receipt=request(URL+'/'+str(layer)+'/query',params,out/(name+'.raw'));decoded=gzip.decompress(raw)if raw.startswith(b'\x1f\x8b')else raw
        (out/(name+'.json')).write_bytes(decoded);save(out/(name+'-request.json'),dict(receipt,decodedSHA256=digest(decoded),gzipDecoded=raw!=decoded));data=read(out/(name+'.json'));assert not data.get('error')and not data.get('exceededTransferLimit');return data['features']
    records={};shapes={};relations={}
    for label,uid in [('owner',a.uid),('canopy',a.basic)]:
        f=forms[uid];features=query('official-'+label,0,f['buildingCSUID'],True);assert len(features)==1
        official=features[0]['attributes'];assert official['Status']=='Active'and official['BuildingCSUID']==f['buildingCSUID']and official['BuildingBlockType']==f['structureType']
        records[uid]=official;relations[uid]=query('official-'+label+'-relations',1002,f['buildingCSUID'],False)
        shapes[uid]=shapely.symmetric_difference_all([shapely.Polygon([(x-834500,816500-y)for x,y in ring])for ring in features[0]['geometry']['rings']])
    basic=shapely.Polygon(b['rings'][0],b['rings'][1:]);normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);eligible=np.flatnonzero((normal[:,1]>0)&(tri[:,:,1].min(1)>b['base']+b['height']))
    polys={int(i):shapely.Polygon(tri[i][:,[0,2]])for i in eligible};seeds={i for i,p in polys.items()if p.intersection(basic).area>0};vertex_faces={}
    for i in map(int,eligible):
        for v in tri[i]:vertex_faces.setdefault(tuple(map(float,v)),set()).add(i)
    groups=[];seen=set()
    for start in sorted(seeds):
        if start in seen:continue
        group=set();pending=[start]
        while pending:
            i=pending.pop()
            if i in group:continue
            group.add(i)
            for v in tri[i]:pending.extend(vertex_faces[tuple(map(float,v))]-group)
        seen|=group;poly=shapely.union_all([polys[i]for i in group]);ids=sorted(group);t=tri[ids]
        groups.append(dict(sourceFaces=ids,completeComponentProjectedAreaM2=float(poly.area),basicFootprintOverlapM2=float(poly.intersection(basic).area),basicFootprintCoverage=float(poly.intersection(basic).area/basic.area),wholeComponentBounds=[t.min((0,1)).tolist(),t.max((0,1)).tolist()],projection=poly))
    groups.sort(key=lambda r:-r['basicFootprintOverlapM2']);assert groups
    fig,ax=plt.subplots(figsize=(10,8),layout='constrained')
    for poly,color in [(g['projection'],'#316ba7')for g in groups]+[(basic,'#d02d48'),(shapes[a.basic],'#111111')]:
        for part in shapely.get_parts(poly):
            if part.geom_type=='Polygon':ax.plot(*part.exterior.xy,color=color,linewidth=1.4)
    low=np.asarray(basic.bounds[:2])-2;high=np.asarray(basic.bounds[2:])+2;ax.set(xlim=(low[0],high[0]),ylim=(low[1],high[1]),aspect='equal',title='Original upper-roof component blue / BASIC red / fresh official black\nDisplay crop only; no replacement approval');ax.grid(alpha=.2);image=out/'original-roof-current-official-canopy.png';fig.savefig(image,dpi=150);plt.close(fig);refs.append(image)
    result=dict(uids=[a.uid,a.basic],sourceUid=a.uid,basicUid=a.basic,sourceSHA256=row['sourceSHA256'],sourceModelId=row['modelId'],currentForms=forms,officialRecords=records,officialRelations=relations,basicFootprintAreaM2=float(basic.area),basicOfficialFootprintHausdorffDistanceM=float(basic.hausdorff_distance(shapes[a.basic])),originalRoofComponents=[{k:v for k,v in g.items()if k!='projection'}for g in groups],image=dict(path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes())),sourceGeometryChanges=0,sourcePoseChanges=0,basicGeometryChanges=0,identityAccepted=False,featureReplacementApproved=False,suppressionApproved=False,installationApproved=False,publication=False,qualification='Exact current original/form bindings plus fresh primary active owner/canopy records and complete connected original upper-roof components. Extent/height/footprint differences retained. Component/outline correlation is nomination evidence, not a suppression, source identity, support or collision exemption. Metadata requests only; no government model/archive acquisition.')
    save(out/'summary.json',result);refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE.parent/'landsd-territory/source.py']);assert reservations.owns(lease)
    module('selected_canopy_feature_packet_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-original-canopy-feature-and-fresh-primary-source-packet',refs,result)
if __name__=='__main__':main()

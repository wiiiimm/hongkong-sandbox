"""Read-only check of official height fields against the existing terrain mesh."""
import gzip,json,math,pathlib,sys,hashlib
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE))
from compare_official import official_shape

def main():
    source=ROOT/'source-scripts/city/mui-wo-buildings/landsd-mui-wo.json.gz';raw=gzip.decompress(source.read_bytes());data=json.loads(raw)
    terrain=ROOT/'3d-viewer/city/data/terrain.json';dem=json.loads(terrain.read_text());g=dem['meta']['georef'];w=dem['w']
    def ground(x,z):
        c=(x+834500-g['bE'])/g['aE'];r=(816500-z-g['bN'])/g['aN']
        if not(0<=c<dem['w']-1 and 0<=r<dem['h']-1):return None,False
        i,j=int(c),int(r);u,v=c-i,r-j
        a,b,d,e=[dem['elev'][idx] for idx in (j*w+i,j*w+i+1,(j+1)*w+i,(j+1)*w+i+1)]
        dry=all(value>0 for value in ((a,b,d) if u+v<=1 else (b,d,e)))
        a,b,d,e=[max(1.2,h) if h>0 else -4 for h in (a,b,d,e)]
        height=a+(b-a)*u+(d-a)*v if u+v<=1 else e+(d-e)*(1-u)+(b-e)*(1-v)
        return max(1.2,height),dry
    records=[];missing=0
    for f in data['features']:
        p=official_shape(f);a=f['attributes'];point=p.representative_point();y,dry=ground(point.x,point.y)
        base,top=a.get('BaseHeight'),a.get('TopHeight')
        if not isinstance(base,(int,float)) or not isinstance(top,(int,float)):
            missing+=1;continue
        records.append({'objectId':a['OBJECTID'],'buildingCSUID':a['BuildingCSUID'],'name':a.get('BuildingNameEN'),'kind':a['BuildingBlockType'],'sourceBaseHKPD':base,'sourceTopHKPD':top,'terrainY':round(y,3),'sourceBaseMinusTerrain':round(base-y,3),'sourceTopBelowTerrain':top<y,'fullyDryTriangle':dry,'pointWorld':[round(point.x,3),round(point.y,3)]})
    values=sorted(r['sourceBaseMinusTerrain'] for r in records)
    percentile=lambda q:values[round((len(values)-1)*q)]
    worst=sorted(records,key=lambda r:abs(r['sourceBaseMinusTerrain']),reverse=True)[:20]
    report={'result':'diagnostic only; no vertical adjustment applied','officialSnapshot':str(source.relative_to(ROOT)),'officialSha256':hashlib.sha256(raw).hexdigest(),'terrainSha256':hashlib.sha256(terrain.read_bytes()).hexdigest(),'counts':{'sourceForms':len(data['features']),'withBothSourceHeights':len(records),'missingAtLeastOneSourceHeight':missing,'absoluteBaseDifferenceOver5m':sum(abs(r['sourceBaseMinusTerrain'])>5 for r in records),'sourceTopBelowRenderedTerrain':sum(r['sourceTopBelowTerrain'] for r in records),'sourceFootprintRepresentativePointNotOnFullyDryTriangle':sum(not r['fullyDryTriangle'] for r in records)},'baseMinusTerrainMetres':{'minimum':min(values),'p10':percentile(.1),'median':percentile(.5),'p90':percentile(.9),'maximum':max(values)},'method':'Compare LandsD BaseHeight/TopHeight fields with rendered70m terrain-triangle interpolation at each official footprint representative point. Positive terrain vertices are clamped to1.2m, sea vertices are-4m, then sampled height is clamped to1.2m, matching the current sampler.','limits':['Official BaseHeight and TopHeight are approximate metres above Hong Kong Principal Datum, per retained data specification.','A source top below terrain indicates a model/source conflict, not evidence that the official building is underground.','Only one representative point per footprint is sampled; this does not replace a full triangle-footprint intersection audit.','Terrain source age, coarse sampling and ground-object contamination can differ from official building geometry. No source elevations or terrain are altered.'],'worstBaseDifferences':worst,'records':records}
    (HERE/'terrain-comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('records','worstBaseDifferences')},indent=2))
if __name__=='__main__':main()

"""Compare rendered 5 m grid triangles against browser source-TIN raycasts."""
import json,pathlib,statistics
HERE=pathlib.Path(__file__).resolve().parent
proof=json.loads((HERE/'model-browser-proof.json').read_text())
grid=json.loads((HERE/'model-sample/terrain-source-5m.json').read_text())
elev=grid['elev'];g=grid['meta']['georef'];rows=[]
for item in proof['audit']:
    x,y,z=[(a+b)/2 for a,b in zip(*item['actualBounds'])]
    c=(x+834500-g['bE'])/g['aE'];r=(816500-z-g['bN'])/g['aN']
    if not(0<=c<grid['w']-1 and 0<=r<grid['h']-1):continue
    i,j=int(c),int(r);u,v=c-i,r-j;k=j*grid['w']+i
    a,b,d,e=elev[k],elev[k+1],elev[k+grid['w']],elev[k+grid['w']+1]
    if any(value is None for value in [a,b,d,e]):continue
    value=a+(b-a)*u+(d-a)*v if u+v<=1 else e+(d-e)*(1-u)+(b-e)*(1-v)
    rows.append({'id':item['id'],'resampledHeight':value,'sourceTINHeight':item['sourceGround'],
        'resampleDifference':value-item['sourceGround'] if item['sourceGround'] is not None else None,
        'sourceModelRoofBelowResample':item['actualBounds'][1][1]<value,
        'sourceModelRoofBelowExistingFineTerrain':item['sourceModelRoofBelowFineTerrain']})
differences=[abs(r['resampleDifference']) for r in rows if r['resampleDifference'] is not None]
result={'method':'Rendered triangle interpolation of the resampled 5 m grid at model-bounds centres, compared to independent original source TIN browser raycast. Centres outside the resampled grid or without valid sampled triangle coverage are excluded.',
 'modelCentresInsideResampledGrid':len(rows),'sourceModelRoofsBelowResampledTerrain':sum(r['sourceModelRoofBelowResample'] for r in rows),
 'sourceModelRoofsBelowExistingFineTerrainInSameCoverage':sum(r['sourceModelRoofBelowExistingFineTerrain'] for r in rows),
 'absoluteResampleDifferenceMetres':{'median':statistics.median(differences),'maximum':max(differences)},'records':rows}
(HERE/'model-terrain-grid-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))

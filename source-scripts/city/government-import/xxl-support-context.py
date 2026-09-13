"""Additional source-triangle support evidence; never membership approval or publication."""
import importlib.util,sys,json,shutil,uuid
from pathlib import Path
import numpy as np
import shapely
spec=importlib.util.spec_from_file_location('xxl_second',Path(__file__).with_name('xxl-second-pass.py'));s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)

def surface(tri):
    polys=shapely.polygons(tri[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;return tri[valid],shapely.STRtree(polys[valid])

def samples_below(points,tri,tree,ceiling):
    pi,ti=tree.query(shapely.points(points),predicate='covered_by');abc=tri[ti];ab=abc[:,1,[0,2]]-abc[:,0,[0,2]];ac=abc[:,2,[0,2]]-abc[:,0,[0,2]];ap=points[pi]-abc[:,0,[0,2]];det=ab[:,0]*ac[:,1]-ab[:,1]*ac[:,0];u=(ap[:,0]*ac[:,1]-ap[:,1]*ac[:,0])/det;v=(ab[:,0]*ap[:,1]-ab[:,1]*ap[:,0])/det;ys=abc[:,0,1]+u*(abc[:,1,1]-abc[:,0,1])+v*(abc[:,2,1]-abc[:,0,1]);ok=ys<=ceiling;out=np.full(len(points),-np.inf);np.maximum.at(out,pi[ok],ys[ok]);return out

def start():
    resources=set(s.read(s.LOCAL/'elements/stage-reservation.json')['resources'])|{'building:landsd/76364:0','building:landsd/232025:0'}
    claim=s.reservations.claim('codex-xxl-support-'+str(uuid.uuid4()),sorted(resources),batch=s.BATCH+'-support');assert claim['ok'];s.save(s.LOCAL/'support-reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    s.call([sys.executable,str(s.HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(s.LOCAL/'support-reservation.json'),'--',sys.executable,__file__,'owned'])

def owned():
    assert s.reservations.owns(s.read(s.LOCAL/'support-reservation.json'));rows=s.read(s.DOC/'selection.json.gz')['rows'];tower=next(r for r in rows if r['uid']=='landsd/76364:0');podium=s.read(s.LOCAL/'saxon-support/input.json.gz')['native'][0];m=podium['model'];raw=s.LOCAL/'saxon-support'/m['asset']['asset'];assert s.h(raw)==m['asset']['sha256'];shutil.copyfile(raw,s.LOCAL/m['asset']['asset']);p=s.glb_triangles({'modelId':m['modelId'],'sourceSHA256':m['asset']['sha256'],'triangles':m['triangles'],'native':podium});t=s.glb_triangles(tower);points,bottom=s.resolution.sample_points({'position':t.reshape(-1).tolist(),'index':list(range(len(t)*3))});low=points[points[:,1]<=bottom+.35];tri,tree=surface(p);heights=s.context.shared.samples(low[:,[0,2]],tri,tree);covered=np.isfinite(heights);gaps=low[:,1]-heights;source=s.read(s.LOCAL/'saxon-support/geometry-inputs.json')['rows'][0]
    result={'uid':tower['uid'],'supportUid':source['uid'],'towerSHA256':tower['sourceSHA256'],'supportSHA256':m['asset']['sha256'],'lowRimSamples':len(low),'covered':int(covered.sum()),'contactWithin01m':int((covered&(np.abs(gaps)<=.1)).sum()),'gapRange':[float(gaps[covered].min()),float(gaps[covered].max())] if covered.any() else None,'supportIdentity':{k:source['candidate']['entry'][k] for k in ['overlapOfSmallerFootprint','footprintCentroidDistanceMetres']},'supportAccepted':False,'aiCalls':0};s.save(s.DOC/'saxon-support-triangles.json',result);print(json.dumps(result),flush=True)
    # Current native terrain contact for the podium, with every vertex/centre/rim point.
    native=[]
    for path in (s.LOCAL/'sheets'/podium['sheet']/'terrain').rglob('*.gltf'):native.append(s.context.triangles(path))
    pp,pbottom=s.resolution.sample_points({'position':p.reshape(-1).tolist(),'index':list(range(len(p)*3))});result['podiumNativeTerrain']=s.resolution.audit_native(pp,pbottom,np.concatenate(native));s.save(s.DOC/'saxon-support-triangles.json',result);print(json.dumps({'podiumNativeTerrain':result['podiumNativeTerrain']}),flush=True)
    # Check actual Elements geometry below each flagged source base (diagnostic only).
    element=next(r for r in rows if r['uid']=='landsd/273061:0');tri,tree=surface(s.glb_triangles(element));doc=s.DOC/'elements';neighbours=s.read(doc/'neighbour-checks.json');forms={r['building']['uid']:r['building'] for r in s.read(doc/'neighbour-inputs.json.gz')['rows']};out=[]
    for r in neighbours['rows']:
        if not r['reasons']:continue
        b=forms[r['uid']];points=np.array([v for ring in b['rings'] for v in ring]);base=b['base']+b.get('minimum',0);height=samples_below(points,tri,tree,base+.1);ok=np.isfinite(height);gaps=base-height
        out.append({'uid':b['uid'],'base':base,'vertexChecks':len(points),'nativeSurfaceBelowBase':int(ok.sum()),'contactWithin05m':int((ok&(np.abs(gaps)<=.5)).sum()),'gapRange':[float(gaps[ok].min()),float(gaps[ok].max())] if ok.any() else None,'originalReasons':r['reasons'],'supportAccepted':False})
    s.save(doc/'neighbour-support-triangles.json',{'rows':out,'aiCalls':0,'publication':False,'qualification':'Diagnostic source-footprint vertices against actual native surfaces below each base; not complete source assembly or interior support acceptance.'});print(json.dumps({'neighbourForms':len(out),'allVerticesWithin05m':sum(r['contactWithin05m']==r['vertexChecks'] for r in out)}),flush=True)

if __name__=='__main__':owned() if len(sys.argv)>1 else start()

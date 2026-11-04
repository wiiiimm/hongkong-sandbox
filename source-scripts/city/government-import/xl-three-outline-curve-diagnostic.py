"""Read-only full original/current circular-arc lineage diagnostic."""
from pyproj import Transformer
from run import ROOT,HERE,read,save
from original_outline_curves import verify_polygon
BASE=ROOT/'docs/astra-city/government-import';SOURCE=BASE/'government-xl-three-outline-provenance-20261008';DOC=BASE/'government-xl-three-outline-curve-diagnostic-v3-20261008'
def main():
 assert not DOC.exists();archive=read(SOURCE/'archive-features.json')['features'];true=read(SOURCE/'official-true-curves.json')['features'];official=read(BASE/'government-xl-22-complete-group-official-context-v2-20261008/official-context.json')['rows'];project=Transformer.from_crs(4326,2326,always_xy=True);rows=[];uids={r['csuid']:r['uid'] for r in official};wanted={uids[f['properties']['BuildingCSUID']] for f in archive};forms={b['uid']:b for t in read(ROOT/'3d-viewer/city/data/manifest.json')['tiles'] for b in read(ROOT/'3d-viewer'/t['url'])['buildings'] if b['uid'] in wanted}
 for f in archive:
  csuid=f['properties']['BuildingCSUID'];uid=uids[csuid];geometry=f['geometry'];assert geometry['type']=='Polygon';curves=next(r for r in true if r['attributes']['BuildingCSUID']==csuid)['geometry']['curveRings'];archived=[[list(project.transform(*p)) for p in ring] for ring in geometry['coordinates']];viewer=[[[p[0]+834500,816500-p[1]] for p in ring] for ring in forms[uid]['rings']];current=[[[p[0]+834500,816500-p[1]] for p in ring] for ring in next(r for r in official if r['uid']==uid)['officialRings']];row={'uid':uid,'csuid':csuid,'archive':verify_polygon(archived,curves),'viewer':verify_polygon(viewer,curves),'currentDensified':verify_polygon(current,curves),'installationApproved':False};rows.append(row);save(DOC/(uid.split('/')[1].replace(':','-')+'.json'),row);print(uid,[(k,row[k]['passed'],row[k].get('reason')) for k in ('archive','viewer','currentDensified')],flush=True)
 save(DOC/'summary.json',{'rows':rows,'newlyInstalled':0,'publication':False,'modelGeometryChanges':0})
if __name__=='__main__':main()

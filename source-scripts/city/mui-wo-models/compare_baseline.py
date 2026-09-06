"""Compare displayed roof extrema against the old/new rendered terrain, identically."""
import collections,importlib.util,json,pathlib,subprocess
from shapely.geometry import Polygon
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'3d-viewer/city/data';DOC=ROOT/'docs/astra-city/mui-wo-buildings/extension'
spec=importlib.util.spec_from_file_location('fine',HERE.parent/'mui-wo-buildings/fine_terrain_audit.py');fine=importlib.util.module_from_spec(spec);spec.loader.exec_module(fine)
def main():
 package=json.loads((OUT/'mui-wo-buildings.json').read_text());uids={b['uid'] for b in package['buildings']};tiles={b['tile'] for b in package['buildings']};terrain=fine.DemSampler(json.loads(subprocess.check_output(['git','show','ff68cf1:3d-viewer/city/data/terrain-mui-wo.json'],cwd=ROOT)))
 old={}
 for tile in tiles:
  data=json.loads(subprocess.check_output(['git','show',f'ff68cf1:3d-viewer/city/data/tiles/{tile}.json'],cwd=ROOT))
  for b in data['buildings']:
   if b['uid'] not in uids:continue
   t=terrain.extrema(Polygon(b['rings'][0],b['rings'][1:]));top=b['modelGeometry']['worldBounds'][1][1] if b.get('modelGeometry') else b['base']+b['height'];old[b['uid']]={'model':bool(b.get('modelGeometry')),'top':top,'terrain':t,'whollyBelow':top<t['min']-.1,'partlyBelow':top<t['max']-.1}
 new={b['uid']:b for b in json.loads((DOC/'integration.json').read_text())['rows']};assert set(old)==set(new)==uids
 counts=lambda data:{'forms':len(data),'whollyBelow':sum(b['whollyBelow'] for b in data.values()),'partlyBelow':sum(b['partlyBelow'] for b in data.values())}
 transitions=collections.Counter(f'{old[uid]["whollyBelow"]}->{new[uid]["whollyBelow"]}' for uid in uids)
 output={'baselineCommit':'ff68cf1','before':counts(old),'after':counts(new),'wholeRoofTransitions':dict(transitions),'method':'Same highest display-roof elevation versus exact extrema of rendered 5 m triangles within each unchanged official footprint, 0.1 m tolerance. Detailed model tops are used where present; otherwise preserved outline/fallback top. This diagnoses conflicts, not every roof-face occlusion.','remaining':[{**new[uid],'before':old[uid]} for uid in sorted(uids) if new[uid]['partlyBelow']]}
 (DOC/'terrain-comparison.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps({k:v for k,v in output.items() if k!='remaining'},indent=2))
if __name__=='__main__':main()

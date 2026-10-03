"""Record reviewed original walking faces; all other source triangles stay intact."""
import json,pathlib
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/mui-wo-completion'
def main():
 inventory=json.loads((DOC/'infrastructure-inventory.json').read_text());out={'schemaVersion':1,'models':{}}
 named={
 'I178501443703063C0':('Wang Tong crossing · lower source component','橫塘河過河設施（下層來源組件）',None,None),
 'I178581445403063C0':('Wang Tong twin bridge','橫塘河雙橋',[18,19],'https://www.hyd.gov.hk/en/our_projects/walkability_projects/district_facilities/6850th/index.html'),
 'I173601429902063C0':('Mui Wo Rural Committee Road crossing','梅窩鄉事會路過河橋',None,None),
 'I173791415003063C0':('River Silver footbridge · west','銀河行人橋（西）','below-6','https://www.openstreetmap.org/way/1387785789'),
 'I174261416603063C0':('River Silver footbridge · east','銀河行人橋（東）','below-6','https://www.openstreetmap.org/way/724691044'),
 'I175121409703063C0':('Nam Bin Wai river footbridge','南邊圍河道行人橋',[0,1],'https://www.openstreetmap.org/way/111581456'),
 'I176281410402063C0':('Ngan Shek Street bridge','銀石街橋',None,None),
 'I178531420303063C0':('River Silver cycle bridge','銀河單車橋',None,None),
 'I178571420503063C0':('River Silver pedestrian bridge','銀河行人橋',[172,173],'https://www.openstreetmap.org/way/701768072'),
 'I178711420803063C0':('Silvermine Bay waterfront promenade','銀礦灣海濱長廊','promenade-floor','https://www.discoverhongkong.com/eng/place-to-go/travel.guide-mui-wo.html')}
 for m in inventory:
  name,zh,rule,reference=named[m['id']]
  if rule=='below-6':indices=[f['index'] for f in m['upwardFaces'] if f['bounds'][1][1]<6 and f['projectedArea']>1]
  elif rule=='promenade-floor':indices=[f['index'] for f in m['upwardFaces'] if 3486<=f['index']<=3800 and f['bounds'][1][1]<5.3]
  else:indices=rule or []
  out['models'][m['id']]={'name':name,'zh':zh,'reviewedSourceGltfSha256':m['sourceGltfSha256'],'walkTriangleIndices':indices,'walkable':bool(indices),'publicAccessSource':reference,'floorSelectionNote':'Selected original upward deck faces after source plan/elevation review. Curbs, railing tops, canopy roofs and cycle-only surfaces excluded. Source triangle indices and heights are unchanged. Wang Tong public support uses only the west pedestrian span of the upper twin-bridge source object; its lower overlapping source component remains visual/collision geometry only.'}
 (HERE/'infrastructure-config.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()

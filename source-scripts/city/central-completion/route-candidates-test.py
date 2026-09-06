"""Source topology/provenance checks; deliberately not a navigation acceptance test."""
import collections,gzip,json,math,pathlib,unittest
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
class CandidateTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.payload=json.loads((ROOT/'docs/astra-city/central-completion/route-candidates.json').read_text())
  cls.source={f['attributes']['PedestrianRouteID']:f for f in json.loads(gzip.decompress((HERE/'pedestrian-network.json.gz').read_bytes()))['features']}
  cls.access=json.loads((HERE/'pedestrian-access.json').read_text())
 def test_original_vertices_and_attributes(self):
  for route in self.payload['routes']:
   self.assertGreater(route['sourceLengthMetres'],1000)
   last=None;distance=0
   for segment in route['segments']:
    source=self.source[segment['pedestrianRouteId']];part=int(segment['id'].split(':')[1])
    self.assertEqual(segment['nativeCentreline'],source['geometry']['paths'][part]);self.assertEqual(segment['attributes'],source['attributes'])
    line=segment['centrelineXYZ'][::-1] if segment['reverse'] else segment['centrelineXYZ']
    for native,p in zip(segment['nativeCentreline'],segment['centrelineXYZ']):self.assertEqual(p,[native[0]-834500,native[2],816500-native[1]])
    if last:self.assertLess(math.dist(last,line[0]),.002)
    last=line[-1];distance+=sum(math.dist(a,b) for a,b in zip(line,line[1:]))
   self.assertLess(abs(distance-route['sourceLengthMetres']),.01)
 def test_public_source_and_restricted_facility_exclusion(self):
  ids=set(self.access['accessTimeIdsRequested']);self.assertEqual(ids,{r['AccessTimeID'] for r in self.access['tables']['AccessTime']})
  for route in self.payload['routes']:
   for segment in route['segments']:
    a=segment['attributes'];self.assertEqual((a['Location'],a['Enabled'],a['PositionCertainty'],a['Direction']),(1,1,1,0));self.assertNotIn(a['FeatureType'],[5,8,9,10])
    if a['AccessTimeID'] is not None:
     records=[r for r in self.access['tables']['AccessTimeDetails'] if r['AccessTimeID']==a['AccessTimeID']]
     self.assertTrue(any(r['DayCode']=='ED' and r['FromTime']==0 and r['ToTime']==2359 for r in records))
 def test_all_bridges_remain_explicit_unverified_gaps(self):
  for route in self.payload['routes']:
   bridges={s['id'] for s in route['segments'] if s['kind']=='footbridge'}
   self.assertEqual(bridges,{g['segment'] for g in route['gaps']});self.assertEqual(route['status'],'source-connected-runtime-unverified');self.assertNotIn('walkCentreline',route)
if __name__=='__main__':unittest.main()

"""Keep the retained public beach-edge footway as an exact continuous route.
The inland village connection crosses shared roads and remains a separate review.
"""
import gzip,hashlib,json,math,sys
from run import HERE,ROOT,DOC,module
sys.path.insert(0,str(HERE.parent));from build_city import xy
shared=module('existing_public_route',HERE.parent/'tai-o-completion/route_build.py')
def main():
 source=HERE.parent/'snapshots/outlying-west.json.gz';raw=source.read_bytes();data=json.loads(gzip.decompress(raw));way=next(e for e in data['elements'] if e['type']=='way' and e['id']==107501760)
 assert shared.permitted(way['tags']);line=[list(xy(p['lon'],p['lat'])) for p in way['geometry']];assert len(line)==len(way['nodes'])
 length=sum(math.dist(a,b) for a,b in zip(line,line[1:]));route={'schemaVersion':1,'id':'pui-o-beach-edge-walk','title':'Pui O beach edge','sectionId':'10.7','stage':'source-grounded continuous-navigation verification pending','centreline':line,'nodeIds':way['nodes'],'lengthMetres':length,'segments':[{'fromIndex':0,'toIndex':len(line)-1,'sourceWayId':way['id'],'sourceUrl':'https://www.openstreetmap.org/way/107501760','tags':way['tags'],'kind':'path'}],'stops':[{'id':'beach-west-edge','index':0,'sourceNodeId':way['nodes'][0]},{'id':'beach-east-edge','index':len(line)-1,'sourceNodeId':way['nodes'][-1]}],'publicAccessReviewed':True,'continuousWalkVerified':False,'sourceOffsets':[],'sources':[{'file':str(source.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'snapshot':data['osm3s']['timestamp_osm_base'],'attribution':'OpenStreetMap contributors','licence':'ODbL-1.0'},{'url':'https://www.islands.gov.hk/en/explores-lantau-south-pui-o-beach.php','publisher':'Islands District Office','reviewed':'2026-09-07','supports':'Public beach and its visitor facilities; current source page revised 15 May 2026. Exact line comes from retained OSM, not a traced photograph.'}],'limits':['Exact retained public footway only; no invented connectors or private wetland access.','The inland connection from the existing Pui O village arrival uses unclassified/residential roads and needs separate shared-road review.','No survey-level access or tide clearance claim; actual staged-terrain navigation is checked separately.']}
 (DOC/'route.json').write_text(json.dumps(route,indent=2)+'\n');print(json.dumps({'lengthMetres':length,'vertices':len(line),'first':line[0],'last':line[-1]}))
if __name__=='__main__':main()

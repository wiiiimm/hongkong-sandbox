"""Join the repaired Mui Wo arrival to the existing route through source-node topology."""
import json,math,pathlib
from shapely.geometry import Point,LineString
from routes import graph_data,shared,xy,HERE,DOC

def main():
 config,raw,data,ways,nodes,graph=graph_data();repair=json.loads((DOC/'arrivals-staged.json').read_text())['repairs'][0];start=repair['spawn'];wayid=int(repair['arrivalSource'].split('/')[-1]);way=ways[wayid]
 # Add only the already documented rounded spawn and its exact projection on
 # the source segment, keeping original geometry and graph nodes unchanged.
 choices=[]
 for a,b in zip(way['nodes'],way['nodes'][1:]):
  segment=LineString([nodes[a],nodes[b]]);p=segment.interpolate(segment.project(Point(start)));choices.append((p.distance(Point(start)),a,b,[p.x,p.y]))
 distance,a,b,projection=min(choices);assert distance<.1
 nodes[-1]=projection;graph[-1]=[(a,math.dist(projection,nodes[a]),wayid),(b,math.dist(projection,nodes[b]),wayid)]
 mainroute=json.loads((DOC/'routes-staged.json').read_text());stop=next(p for p in mainroute['stops'] if p['id']=='ferry-promenade');edges=shared.shortest(graph,-1,stop['sourceNode']);line=[start,projection]+[nodes[e[1]] for e in edges]
 result={'schemaVersion':1,'placeId':'muiwo','from':start,'to':stop['id'],'sourceProjectionOffsetMetres':distance,'centreline':line,'sourceWayIds':list(dict.fromkeys([wayid,*[e[2] for e in edges]])),'lengthMetres':sum(math.dist(a,b) for a,b in zip(line,line[1:])),'policy':'A sub-decimetre rounding join onto the same public source way, then unchanged source-node-connected public paths to the ferry-promenade route start. No invented street connectors.'}
 (HERE/'arrival-connector.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='centreline'},indent=2))
if __name__=='__main__':main()

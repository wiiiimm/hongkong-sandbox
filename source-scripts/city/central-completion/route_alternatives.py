"""Reuse the source routing graph with separately recorded obstacle exclusions."""
import hashlib,json
from route_candidates import DOC,HERE,HINTS,main as build

def main():
 audit_path=DOC/'contact-edge-audit.json';audit=json.loads(audit_path.read_text());source=HERE/'pedestrian-network.json.gz';assert hashlib.sha256(source.read_bytes()).hexdigest()==audit['sourceSha256']
 original_path=DOC/'route-candidates.json';original=json.loads(original_path.read_text());blocked=set(audit['blocked'])|set(audit['outsideIds']);results=[];failures=[]
 for name,hints in HINTS.items():
  try:
   payload=build(blocked_ids=blocked,output_name=f'route-alternative-{name}.json',selected_hints={name:hints});route=payload['routes'][0];before=next(r for r in original['routes'] if r['id']==route['id'])
   old={s['id'] for s in before['segments']};new={s['id'] for s in route['segments']};route['alternativeEvidence']={'originalRoute':'route-candidates.json','lengthChangeMetres':route['sourceLengthMetres']-before['sourceLengthMetres'],'addedSourceSegments':sorted(new-old),'removedSourceSegments':sorted(old-new),'anchorChanges':[{'title':a['title'],'originalSourceWorldXYZ':a['sourceWorldXYZ'],'alternativeSourceWorldXYZ':b['sourceWorldXYZ']} for a,b in zip(before['anchors'],route['anchors']) if a['sourceWorldXYZ']!=b['sourceWorldXYZ']]};assert not new&blocked;results.append(route)
  except AssertionError as e:
   failures.append({'route':'central-'+name,'reason':str(e)})
   if name=='waterfront':
    # Keep the intended park arrival explicitly unresolved; this additional
    # public promenade alternative ends at its northern approach, not inside.
    alternative_hints=hints[:-1]+[('Tamar Park northern approach',600,550,5)]
    payload=build(blocked_ids=blocked,output_name='route-alternative-waterfront-approach.json',selected_hints={name:alternative_hints});route=payload['routes'][0]
    route['id']='central-waterfront-approach';route['status']='source-connected-partial-destination';route['unresolvedDestination']={'title':hints[-1][0],'hintWorldXYZ':[hints[-1][1],hints[-1][3],hints[-1][2]],'reason':'The original public-network arrival is disconnected when the current podium collision is retained. This route stops at the northern public approach; it does not claim access through the podium.'};results.append(route)
 report={**{k:v for k,v in original.items() if k!='routes'},'status':'source-alternatives-staged','originalRouteSha256':hashlib.sha256(original_path.read_bytes()).hexdigest(),'edgeAuditSha256':hashlib.sha256(audit_path.read_bytes()).hexdigest(),'obstacleScreen':audit['actorScreen'],'routes':results,'failures':failures,'limits':original['limits']+['Original route-candidates.json remains unchanged.','Alternatives exclude source segments contacting existing building volumes on either terrain version. No collision suppression or geometry editing.','Continuous real navigation, exact stairs and source bridge surfaces remain required.']}
 (DOC/'route-alternatives.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('Completed alternatives',len(results),'failures',failures)
if __name__=='__main__':main()

"""Stage narrowly reviewed illustrative-post metadata without moving roofs or sources."""
import copy,json,math

def stage_illustrative_foundations(root,plan,manifest,edits,report,load,sha,encoded):
 updates=plan.get('illustrativeFoundations',[])
 if not updates:return
 seen=set();applied=[]
 for update in updates:
  uid=update['uid'];assert uid not in seen,'Duplicate illustrative foundation';seen.add(uid)
  tile=update['tile'];matches=[t for t in manifest['tiles'] if t['url']==tile];assert len(matches)==1,'Unknown foundation tile'
  path=(root/'3d-viewer'/tile).resolve();assert path.is_relative_to((root/'3d-viewer/city/data/tiles').resolve()),'Invalid foundation tile path'
  assert sha(path)==update['tileSHA256'],'Foundation tile changed'
  # Compose with earlier edits, but require the exact pre-reviewed building.
  data=json.loads(edits[path]) if path in edits else copy.deepcopy(load(path))
  buildings=[b for b in data['buildings'] if b['uid']==uid];assert len(buildings)==1
  building=buildings[0];assert building==update['before'],'Foundation form changed'
  assert not building.get('modelGeometry') and building.get('foundationBase') is None
  assert building.get('kind')=='roof' and building.get('structureType')=='Open-sided Structure'
  assert building.get('baseSource')=='terrain-estimated' and building.get('heightSource')=='estimated'
  assert building.get('baseHeightHKPD') is None and building.get('topHeightHKPD') is None
  value=update['foundationBase'];assert type(value) in (int,float) and math.isfinite(value) and value<building['base']
  # Acceptance is source/terrain-bound by the publication guard, not inferred here.
  evidence=root/update['evidence']['path'];assert sha(evidence)==update['evidence']['sha256']
  proposal_path=root/update['proposal']['path'];assert sha(proposal_path)==update['proposal']['sha256'];proposal=load(proposal_path);assert proposal['uid']==uid and proposal['foundationBase']==value and proposal['originalBase']==building['base']
  qualification=load(evidence);assert qualification['uid']==uid and qualification['fullPostFootprintsMeetGround'] and qualification['wholeRoofClear']
  building['foundationBase']=value;building['foundationPolicy']='terrain-derived-illustrative-posts'
  after=copy.deepcopy(building);after.pop('foundationBase');after.pop('foundationPolicy');assert after==update['before'],'Unrelated building fields changed'
  edits[path]=encoded(data);matches[0]['bytes']=len(edits[path]);applied.append(dict(uid=uid,foundationBase=value,evidence=update['evidence']))
 report['illustrativeFoundations']=applied

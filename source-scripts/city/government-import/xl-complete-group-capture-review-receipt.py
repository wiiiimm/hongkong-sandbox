"""Persist bounded AI interpretation of 22 unchanged original source captures.

No geometry generation, source substitution, blanket ownership or suppression.
"""
import json,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,connect,jobs,Jsonb,dict_row
BATCH='government-xl-22-original-component-capture-review-20261008';DOC=ROOT/'docs/astra-city/government-import'/BATCH
SOURCE=ROOT/'docs/astra-city/government-import/government-xl-22-complete-group-official-context-v2-20261008'
OBSERVATIONS={
227380:'Low elongated podium/landscaped roof is visible; the June Garden T3 tall shaft is absent. A remote maximum source height cannot establish coverage over the tower footprint.',
313033:'Market In is a low broad podium with rooftop circular/sports areas. The two tall Hoi Wah/Hoi Cheong shafts are absent; other rooftop ancillary forms remain separate until demonstrated complete.',
285509:'Broad curved Seaview Garden podium and landscape/sports roof are visible. Eight tall residential shafts are absent; preserve them and the ancillary current form.',
81743:'Ocean Walk is a long low curved podium with columns/roof details and setbacks. Six Pierhead Garden towers are absent. Retain all 17 other group forms, including substations, station and roof structures; complete footprint context is not suppression.',
273672:'YOHO Mall II lower complex/landscaped roof is visible. Sun Yuen Long Centre tall shafts are absent. Similar names/shared footprint do not establish upper component inclusion.',
91827:'Festival Walk lower source appears as one low footprint slab. It is a separate vertical source from the upper Festival Walk mesh; combining them still needs original contact/terrain checks.',
104302:'Festival Walk upper source contains raised mall roof forms/setbacks. It is not proof that the distinct lower source can be suppressed; retain both current component representations pending physical assembly acceptance.',
195849:'Gleneagles complex has two raised curved masses and a joining lower slab in this capture. Original source maximum is 40.216m, below the recorded 55.2m tower tops. The image does not establish complete north/south tower coverage; preserve both.',
120104:'Continuous long depot hall with narrow connected extension is visible. This supports investigating whole-depot footprint context but grants no metadata restoration, foundation or runtime approval. Separate automatic-review hold remains pending.',
264206:'The source labelled China Merchants Tower is a low long podium deck. Shun Tak/China Merchants tall shafts are absent. Retain all three upper/current group components.',
227942:'Apex original is a highly faceted source spanning a sloping site, with two current ancillary footprints beside its main body. Image alone cannot classify the lower-envelope contacts as structural walls versus ground/terrace details; strict rim failure remains.',
265848:'HSBC podium has landscaped roof and larger low masses at its ends. The two tall HSBC tower shafts are absent; original source interfaces still have unresolved samples. Preserve both towers and other current form.',
227099:'WEST9ZONE is an elongated lower podium with roof features. Florient Rise tall shafts are absent; retain both. Its raised end masses are not complete tower coverage.',
228219:'Fu Tor Loy Shopping Centre is a long low slab with small roof structures. Fu Wong/Fu Sun/Fu Lai/Fu Tong tall shafts are absent; preserve all four.',
134332:'Citywalk is a curved courtyard podium with stepped mall volumes and roof landscape. Vision City tall shafts are absent; preserve tall towers and ancillary upper forms.',
233227:'Harbourfront Horizon original is a low U-shaped podium, including rounded ends and internal connectors. Tall hotel body is absent; the image cannot justify suppressing the other hotel component.',
265851:'Olympian City Two original is an L-shaped mall/podium. The tall Central Park tower is absent; retain it. Nearby blue footprints are not original-mesh geometry.',
229881:'Hoi Tai original contains low podium volumes and roof structures, not a demonstrated accepted complete tower assembly. The previous bounded Hoi Tai source/support review remains valid; no unchanged retry or suppression approval.',
280084:'Kwai Chung Shopping Centre is a broad low podium/landscape roof. The estate residential shafts are absent and numerous ancillary forms remain uncertain. Preserve all 23 other group forms.',
235076:'Block Z original contains lower connected wings and raised end volumes. It is below the separate recorded upper academic block; preserve that upper component and require complete source support evidence.',
258470:'Broad lower podium with repeated raised short roof volumes is visible. Imperial six tall residential shafts are absent; preserve them. Rooftop massing does not establish full towers.',
285642:'China Ferry Terminal original contains the low terminal roof and a narrow connected waterfront walkway. China Hong Kong City/Royal Pacific tall shafts are absent; preserve all upper/unknown-height forms. Its waterfront span still requires terrain/foundation/component checks.'}
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists();prior=read(SOURCE/'result.json');context=read(SOURCE/'context.json.gz');assert len(context['rows'])==len(OBSERVATIONS)==22
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('complete',prior)
 for item in prior['evidenceRefs']:assert ref(ROOT/item['path'])==item
 refs=[ref(p) for p in [Path(__file__),SOURCE/'result.json',SOURCE/'context.json.gz',SOURCE/'official-context.json']];rows=[]
 for r in context['rows']:
  number=int(r['uid'].split('/')[1].split(':')[0]);capture=SOURCE/(str(number)+'-0.png');refs.append(ref(capture))
  rows.append({'uid':r['uid'],'sourceSHA256':r['sourceSHA256'],'capture':ref(capture),'reviewer':'Codex','sourceEvidenceInterpretationUsedAI':True,'observation':OBSERVATIONS[number],'retainOtherCurrentGroupUids':[b['uid'] for b in r['groupForms'] if b['uid']!=r['uid']],'suppressionApproved':False,'identityAccepted':False,'installationApproved':False,'geometryEdits':0,'humanStatus':'held-unknown','permanentRejection':False,'qualification':'Bounded visual interpretation of the exact original top/oblique capture with fresh component heights. No external imagery, whole-building geometry, hidden underside or structural support completeness is inferred.'})
 save(DOC/'reviews.json',{'rows':rows,'qualification':'Original component captures only; no architectural remodelling. No automatic rejection, skip or installation credit.'});refs.append(ref(DOC/'reviews.json'))
 claim=reservations.claim('codex-component-capture-review-'+str(uuid.uuid4()),['source-context:'+BATCH],batch=BATCH);assert claim['ok'],claim;lease=claim['reservation'];job=None
 try:
  payload={'uids':[r['uid'] for r in rows],'evidenceRefs':refs,'captureJobId':prior['jobId']};stage='original-component-capture-interpretation-v1';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  result={**payload,'jobId':jid,'batch':BATCH,'rows':rows,'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,'sourceEvidenceInterpretationUsedAI':True,'aiGeometryModelling':False,'qualification':'22 captures actually inspected. Source silhouettes distinguish low/lower/partial assets from absent tall component shafts; this is not full identity/support approval. Existing source-specific physical/runtime failures and Siu Ho Wan automatic-review hold remain.'}
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for item in refs:assert ref(ROOT/item['path'])==item
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'jobId':jid,'reviews':len(rows),'neonVerified':True}),flush=True)
 except Exception as e:
  if job:assert jobs.finish(job,error=str(e))
  raise
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()

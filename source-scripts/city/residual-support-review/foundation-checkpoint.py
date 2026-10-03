"""Retain the bounded two-approved/one-held foundation review checkpoint."""
import pathlib,json,hashlib
R=pathlib.Path(__file__).resolve().parents[3];H=pathlib.Path(__file__).resolve().parent/'foundation';D=R/'docs/astra-city/residual-support-review/foundation';read=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,x:p.write_text(json.dumps(x,indent=2)+'\n');snapshot=read(R/'docs/astra-city/model-integration-20260909/current-source-review.json')['snapshotId'];a=read(H/'approval.json');a['ledgerSnapshot']=snapshot
for row in a['rows']:
 for old,new in [('places79/486','places 79/486'),('to3.374m','to 3.374 m'),('all9','all 9')]:row['observation']=row['observation'].replace(old,new)
a['limits']=[s.replace('retains10','retains 10').replace('source230686','source 230686')for s in a['limits']];write(H/'approval.json',a);write(D/'decisions.json',a)
held={'uid':'landsd/230686:0','sourceName':'B337351515902063C0','sourceSHA256':'8f46865b65669c9aca6a9fa6e925dc26a1687c636935a4dc88e95f87f1dcee0b','state':'held','reason':'Exact native hillside terrain improves low-rim contact from 4/26 to 21/26, but five source boundary points remain below grade (maximum 31.51 m) and one complete upward native triangle remains buried. The normal/isolated native views are inspectable; retaining-bank and buried source-face interpretation, road/terrain seams and final guarded nested patch publication remain unresolved. Retain the existing fallback; do not shift the source model.','identity':'Exact source component; no claim that it is The Merton.','evidence':[{'path':str(p.relative_to(R)),'sha256':sha(p)}for p in [D/'hillside/exact-tin.json',D/'hillside/current-versus-exact.json',D/'hillside/framing/report.json']],'neighbourCheck':'Eight affected footprints; no newly introduced sampled roof/base flags. Finite sampling is not a complete intersection proof.','nextActions':['Inspect the actual native triangle 160 and the five lowest boundary points against native terrain facets and visible retaining walls. Determine expected below-grade geometry versus genuine occlusion.','Review roads and terrain boundaries in the current-versus-exact browser views; camera framing is already clear.','If accepted, package the exact child in an area.terrain bundle under its parent city/data/terrain-central.json with the current verified parent SHA. Run the existing publisher dry-run and installed checks; never publish the diagnostic candidate automatically.']};write(D/'hillside/decision.json',held)
write(D/'checkpoint.json',{'issue':'HKS-214','status':'paused-after-current-three','snapshotId':snapshot,'approvedForIntegration':a['approvedNewUids'],'held':['landsd/230686:0'],'publishedByThisPass':False,'plan':'source-scripts/city/residual-support-review/foundation/publication-plan.json','approval':'source-scripts/city/residual-support-review/foundation/approval.json','heldDecision':'docs/astra-city/residual-support-review/foundation/hillside/decision.json','constraints':['No further acquisition or integration while paused.','Source assets and exact candidate terrain remain versioned; shared cache continuity is the parent R2 checkpoint.','Acquire canonical source reservations on the restored machine before resuming.']})
(D/'README.md').write_text('''# Foundation review pause checkpoint — HKS-214

Two components are approved for integration: **255200 Dynasty Club / Convention Plaza podium** and **255386 Convention Plaza Office Tower**. The plan passes the existing publisher dry-run: two native models, no terrain changes, no estimated-base changes. Both source assets retain their original checksums and elevations. The Office Tower requires the native podium.

Normal and isolated views were inspected. The podium's wider normal view has 16/21 source rays; ten unrelated model groups retain their fallbacks under the existing rendering budget. The reviewed parts remain active without errors. The podium has 755 upward faces and 483 sampled roofs, with no fully buried upward face or roof. The tower has 721 upward faces and 371 sampled roofs, also clear; all nine low-rim points contact its native podium. Some podium foundation vertices are below both the native terrain and existing terrain; this was not corrected by moving geometry.

**230686 is held separately.** Its exact source name is B337351515902063C0; it must not be labelled The Merton. The original and exact-terrain browser views are retained. Exact TIN improves rim contact from 4/26 to 21/26, and all eight neighbouring footprint checks show no new flags. Five source rim points remain below grade and one upward source triangle remains buried, requiring explicit retaining-bank/source-face judgement. No terrain candidate is approved for publication.

## Resume on another machine

Restore the parent Git/R2 checkpoint and use the pinned Neon branch. Read checkpoint.json, approval.json and hillside/decision.json first. Claim the two approved source keys before running any integration. The exact next validation command for their existing plan is:

```sh
python source-scripts/city/island-detail-integration/publish.py source-scripts/city/residual-support-review/foundation/publication-plan.json
```

This is a dry-run. Publication and installed browser checks remain a separate, reserved operation. Do not run foundation.py to resume: it is the original claim/staging command. The shared snapshot may have advanced; resolve the current pointer before writing the ledger.

For the held source, claim building:landsd/230686:0 first. Existing diagnostic commands (no acquisition, no publication):

```sh
node source-scripts/city/residual-support-review/foundation-hillside-check.mjs
node source-scripts/city/residual-support-review/foundation-hillside-browser.generated.mjs
```

The native exact patch is under foundation/hillside/exact-tin/. Its parent was terrain-central.json SHA2207e6d0e933daf100ea5240b974d7346da96ec169d5c199346fdee1a3a276d7 when generated. Reconcile any changed parent before publication; preserve other reviewed child patches. The Python terrain generator uses cached official TIN sources; no new downloads are necessary for this checkpoint. Native geometry, native elevations and vertical scale1 remain unchanged.

A source component approval is not a complete landmark or region. No source was published by this review pass. The parent task records the final cloud checkpoint and issue status.
''')

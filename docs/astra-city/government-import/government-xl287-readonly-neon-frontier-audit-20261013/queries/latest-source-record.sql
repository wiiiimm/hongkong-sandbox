WITH sources AS (
 SELECT * FROM jsonb_to_recordset('{{EXACT_SOURCE_ROWS_JSON}}'::jsonb) AS s("sourceKey" text, uid text, "indexedSourceSHA256" text, "runtimeSourceSHA256" text, "installedVerified" boolean)
), expanded AS MATERIALIZED (
 SELECT j.id,j.batch,j.stage,j.status,j.updated_at,'job-top-level' AS record_scope,j.result AS record
 FROM astra_modelling.jobs j WHERE j.status='complete' AND j.batch LIKE 'government-xl%' AND j.result ? 'sourceSHA256'
 UNION ALL
 SELECT j.id,j.batch,j.stage,j.status,j.updated_at,'per-source-row',r
 FROM astra_modelling.jobs j CROSS JOIN LATERAL jsonb_array_elements(CASE WHEN jsonb_typeof(j.result->'rows')='array' THEN j.result->'rows' ELSE '[]'::jsonb END)r
 WHERE j.status='complete' AND j.batch LIKE 'government-xl%' AND r ? 'sourceSHA256'
), matched AS (
 SELECT s."sourceKey",s.uid AS expected_uid,s."indexedSourceSHA256" AS expected_source_sha256,e.*,
 row_number() OVER(PARTITION BY s."sourceKey" ORDER BY e.updated_at DESC,e.id DESC,e.record_scope) AS recency
 FROM sources s JOIN expanded e ON e.record->>'sourceSHA256'=s."indexedSourceSHA256" OR e.record->>'sourceSHA256'=s."runtimeSourceSHA256"
)
SELECT "sourceKey",expected_uid,expected_source_sha256,id,batch,stage,status,updated_at,record_scope,
 jsonb_build_object('uid',record->'uid','uids',record->'uids','sourceSHA256',record->'sourceSHA256','installed',record->'installed','humanStatus',record->'humanStatus','currentHeldReason',record->'currentHeldReason','remainingReason',record->'remainingReason','reasons',record->'reasons','nextStep',record->'nextStep','identityAccepted',record->'identityAccepted','physicalAccepted',record->'physicalAccepted','scriptFullAcceptancePassed',record->'scriptFullAcceptancePassed','currentAcceptance',record->'currentAcceptance','installationApproved',record->'installationApproved','publication',record->'publication','permanentRejection',record->'permanentRejection','sourceCorrupt',record->'sourceCorrupt','requiresAI',record->'requiresAI','requiresHumanDecision',record->'requiresHumanDecision','qualification',record->'qualification') AS latest_source_record
FROM matched WHERE recency=1 ORDER BY "sourceKey"

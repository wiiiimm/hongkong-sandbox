WITH sources AS (
 SELECT * FROM jsonb_to_recordset('{{EXACT_SOURCE_ROWS_JSON}}'::jsonb) AS s("sourceKey" text, uid text, "indexedSourceSHA256" text, "runtimeSourceSHA256" text, "installedVerified" boolean)
), positive_jobs AS MATERIALIZED (
 SELECT id,batch,stage,status,result,updated_at FROM astra_modelling.jobs
 WHERE status='complete' AND (
 result->'physicalAccepted'='true'::jsonb OR result->'scriptFullAcceptancePassed'='true'::jsonb OR
 result->'currentAcceptance'='true'::jsonb OR result->'installationApproved'='true'::jsonb OR
 result->'publication'='true'::jsonb OR result->'passed'='true'::jsonb OR result->'checksPassed'='true'::jsonb)
)
SELECT s."sourceKey",s.uid AS expected_uid,s."indexedSourceSHA256" AS expected_source_sha256,j.id,j.batch,j.stage,j.updated_at,
 jsonb_build_object('physicalAccepted',j.result->'physicalAccepted','scriptFullAcceptancePassed',j.result->'scriptFullAcceptancePassed','currentAcceptance',j.result->'currentAcceptance','installationApproved',j.result->'installationApproved','publication',j.result->'publication','passed',j.result->'passed','checksPassed',j.result->'checksPassed','sourceSHA256',j.result->'sourceSHA256','sourceSHA256s',j.result->'sourceSHA256s','uids',j.result->'uids','installedUids',j.result->'installedUids','manifestSHA256',j.result->'manifestSHA256','snapshotId',j.result->'snapshotId','qualification',j.result->'qualification','interpretation',j.result->'interpretation','nextStep',j.result->'nextStep') AS selected_result
FROM sources s JOIN positive_jobs j ON (
 j.result->>'sourceSHA256'=s."indexedSourceSHA256" OR j.result->>'sourceSHA256'=s."runtimeSourceSHA256" OR
 j.result->'sourceSHA256s'->>s.uid=s."indexedSourceSHA256" OR
 EXISTS(SELECT 1 FROM jsonb_array_elements(CASE WHEN jsonb_typeof(j.result->'rows')='array' THEN j.result->'rows' ELSE '[]'::jsonb END)r
 WHERE r->>'sourceSHA256'=s."indexedSourceSHA256" OR r->'sourceSHA256s'->>s.uid=s."indexedSourceSHA256"))
ORDER BY s."sourceKey",j.updated_at DESC

WITH sources AS (
 SELECT * FROM jsonb_to_recordset('{{EXACT_SOURCE_ROWS_JSON}}'::jsonb) AS s("sourceKey" text, uid text, "indexedSourceSHA256" text, "runtimeSourceSHA256" text, "installedVerified" boolean)
)
SELECT s."sourceKey",s.uid AS expected_uid,s."indexedSourceSHA256" AS expected_source_sha256,j.id,j.batch,j.stage,j.updated_at,
 jsonb_build_object('uid',r->'uid','sourceSHA256',r->'sourceSHA256','installed',r->'installed','humanStatus',r->'humanStatus','physicalAccepted',r->'physicalAccepted','currentAcceptance',r->'currentAcceptance','installationApproved',r->'installationApproved','scriptFullAcceptancePassed',r->'scriptFullAcceptancePassed','publication',r->'publication','reasons',r->'reasons','blockerGroup',r->'blockerGroup','nextStep',r->'nextStep','requiresAI',r->'requiresAI','requiresHumanDecision',r->'requiresHumanDecision') AS per_source_result
FROM sources s JOIN astra_modelling.jobs j ON j.id IN ('e286ee62bea12ba508365c4c0f4b2a6d4993af16473d6ebb6a594dd0a6c6d107','9963d69f1a4c5c150cb119ba7409204fc9beca9c0ddb49ba2b4e85d9d7334585')
CROSS JOIN LATERAL jsonb_array_elements(j.result->'rows') r
WHERE r->>'sourceSHA256'=s."indexedSourceSHA256" OR r->>'sourceSHA256'=s."runtimeSourceSHA256"
ORDER BY s."sourceKey",j.updated_at DESC

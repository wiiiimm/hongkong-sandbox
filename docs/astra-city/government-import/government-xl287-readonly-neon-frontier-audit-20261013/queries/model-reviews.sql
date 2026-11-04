WITH sources AS (
 SELECT * FROM jsonb_to_recordset('{{EXACT_SOURCE_ROWS_JSON}}'::jsonb) AS s("sourceKey" text, uid text, "indexedSourceSHA256" text, "runtimeSourceSHA256" text, "installedVerified" boolean)
), matches AS (
 SELECT s."sourceKey", r.snapshot_id, r.uid, r.source_sha256, r.source_state, r.review_state, r.updated_at,
 jsonb_build_object('publicationApproved',r.result->'publicationApproved','placementReviewed',r.result->'placementReviewed','identityReviewApproved',r.result->'identityReviewApproved','identityAccepted',r.result->'identityAccepted','physicalAccepted',r.result->'physicalAccepted','scriptFullAcceptancePassed',r.result->'scriptFullAcceptancePassed','currentAcceptance',r.result->'currentAcceptance','installationApproved',r.result->'installationApproved','productionPublished',r.result->'productionPublished','wholeLandmarkComplete',r.result->'wholeLandmarkComplete','evidence',r.result->'evidence','sha256',r.result->'sha256','observation',r.result->'observation','reasons',r.result->'reasons','humanStatus',r.result->'humanStatus','needsHumanDecision',r.result->'needsHumanDecision','needsAIProcessing',r.result->'needsAIProcessing') AS selected_result,
 row_number() OVER (PARTITION BY s."sourceKey" ORDER BY r.updated_at DESC, r.snapshot_id DESC) AS recency
 FROM sources s JOIN astra_modelling.model_reviews r ON r.source_sha256=s."indexedSourceSHA256" OR r.source_sha256=s."runtimeSourceSHA256"
)
SELECT s."sourceKey", s.uid AS expected_uid, s."indexedSourceSHA256" AS expected_source_sha256,
 count(m."sourceKey") AS matching_review_rows,
 count(m."sourceKey") FILTER (WHERE m.snapshot_id='5cb980a97466802b') AS current_snapshot_rows,
 coalesce(jsonb_agg(jsonb_build_object('snapshotId',m.snapshot_id,'uid',m.uid,'sourceSHA256',m.source_sha256,'sourceState',m.source_state,'reviewState',m.review_state,'updatedAt',m.updated_at,'selectedResult',m.selected_result) ORDER BY m.recency) FILTER (WHERE m.recency<=3), '[]'::jsonb) AS latest_exact_hash_reviews
FROM sources s LEFT JOIN matches m USING ("sourceKey")
GROUP BY s."sourceKey",s.uid,s."indexedSourceSHA256" ORDER BY s."sourceKey"

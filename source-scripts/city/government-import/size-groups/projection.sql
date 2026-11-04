-- Expand stored metadata inside Postgres; no model downloads/decoding/AI calls.
WITH entries AS (
    SELECT m.run_id, m.cache_key, i.sheet, r.result_sha, x
    FROM astra_modelling.native_stage_members m
    JOIN astra_modelling.native_stage_inputs i USING (cache_key)
    JOIN astra_modelling.native_stage_results r USING (cache_key)
    CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') x
    WHERE m.run_id = %s
)
SELECT run_id, cache_key, x->>'modelId' AS model_id,
    'government-size-v1'::text AS policy, result_sha AS source_result_sha, sheet,
    x->>'sourceEntry' AS source_entry, x->>'state' AS source_state,
    x->'candidate'->>'uid' AS viewer_uid,
    x->'candidate'->>'buildingCSUID' AS building_csuid,
    x->>'holdReason' AS source_hold_reason, x->>'error' AS source_error,
    (x->>'triangles')::bigint AS triangles,
    (x->>'vertices')::bigint AS source_vertices,
    (x->'asset'->>'indexedVertices')::bigint AS indexed_vertices,
    (x->'asset'->>'bytes')::bigint AS compressed_bytes,
    (x->'asset'->>'glbBytes')::bigint AS glb_bytes,
    (x->'asset'->>'decodedGeometryBytes')::bigint AS geometry_bytes,
    (x->'worldBounds'->1->>0)::double precision
        - (x->'worldBounds'->0->>0)::double precision AS width_m,
    (x->'worldBounds'->1->>1)::double precision
        - (x->'worldBounds'->0->>1)::double precision AS height_m,
    (x->'worldBounds'->1->>2)::double precision
        - (x->'worldBounds'->0->>2)::double precision AS depth_m
FROM entries

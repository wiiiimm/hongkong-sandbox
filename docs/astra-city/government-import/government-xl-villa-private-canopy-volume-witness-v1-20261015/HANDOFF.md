# Villa private canopy: production collision result

Completed both workers, pinned Neon verified: complete surface check 04e99528a6c587adb22dc696f2289f16d3876871877706ff335222badaa5acae; exact roof-interior witness check 7f2dc98a701e229dd0c76cdbdd71dd193c02f07c04e79ace80677ea771a0d93d.

Unchanged production building-geometry.js generated the exact current canopy and both private candidate pieces, including illustrative posts. All five complete original sources tested against all generated triangles. Four towers have zero surface contacts in either version. Podium surface contacts: current74, candidate84. These counts do not distinguish valid boundary contact from penetration.

Exact rational mid-roof test resolves that distinction: current29 strict interior witnesses; candidate first piece0, second piece8. All source and cap barycentric coordinates are strictly positive for recorded witnesses. Candidate remains failed, not approved. Both candidate pieces produce nondegenerate triangles. The source-projection subtraction in double precision alone is insufficient after production Float32 extrusion; investigate exact eight witness locations and representable boundary positions. Do not increase collision tolerances, drop tiny pieces, change original model geometry, or label source geometry corrupt. No full placed-world/containment proof is claimed.

Next: map remaining witnesses to exact source boundary segments and actual Float32 generated roof faces. Derive a conservative source-backed procedural boundary correction that survives production packing, retaining all actor components, then repeat complete strict collision checks and current five-source acceptance/neighbours/browser. Current live geometry was never changed.

XL unchanged243installed/278remaining/521.

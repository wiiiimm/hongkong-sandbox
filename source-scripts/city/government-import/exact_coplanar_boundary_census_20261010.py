"""Conservative full-edge coplanar region census; never changes geometry.

Only full-edge manifold, same-winding components with one simple boundary can
receive a theoretical triangulation count. T-junctions, holes, duplicate faces,
branched boundaries and degenerate triangles retain their entire original count.
All collinearity is integer exact on the actual Float32 coordinate stream.
"""
from collections import defaultdict
import numpy as np
from exact_runtime_coplanar_groups_20261010 import groups

def census(triangles):
    t=np.asarray(triangles,dtype=np.float32).astype(np.float64);plane=groups(t)
    denominator=plane['coordinateIntegerDenominator']
    vertices={tuple(map(float,p)):tuple(int(float(v).as_integer_ratio()[0]*(denominator//float(v).as_integer_ratio()[1])) for v in p) for p in t.reshape(-1,3)}
    records=[];saving=0
    for group in plane['rows']:
        ids=group['faceIds'];edges=defaultdict(list);adjacency={i:set() for i in ids}
        for i in ids:
            points=[vertices[tuple(p)] for p in t[i]]
            for a,b in zip(points,points[1:]+points[:1]):edges[tuple(sorted((a,b)))].append((i,a,b))
        invalid=any(len(e)>2 or (len(e)==2 and not (e[0][1]==e[1][2] and e[0][2]==e[1][1])) for e in edges.values())
        if invalid:
            records.append({'faceIds':ids,'originalFaces':len(ids),'state':'nonmanifold-or-overlapping-exact-edge','theoreticalFaces':len(ids),'saving':0});continue
        for entries in edges.values():
            if len(entries)==2:
                a,b=entries[0][0],entries[1][0];adjacency[a].add(b);adjacency[b].add(a)
        unseen=set(ids)
        while unseen:
            todo=[min(unseen)];part=set()
            while todo:
                i=todo.pop()
                if i in part:continue
                part.add(i);todo.extend(adjacency[i]-part)
            unseen-=part;boundary=[e[0][1:] for e in edges.values() if len(e)==1 and e[0][0] in part]
            outgoing=defaultdict(list);incoming=defaultdict(list)
            for a,b in boundary:outgoing[a].append(b);incoming[b].append(a)
            loops=[];state='single-simple-boundary'
            if not boundary or any(len(outgoing[p])!=1 or len(incoming[p])!=1 for p in set(outgoing)|set(incoming)):state='branched-or-empty-boundary'
            else:
                left=set(outgoing)
                while left:
                    start=min(left);p=start;loop=[]
                    while p in left:
                        loop.append(p);left.remove(p);p=outgoing[p][0]
                    if p!=start:state='non-simple-boundary';break
                    loops.append(loop)
                if len(loops)!=1:state='multiple-boundaries-hole-or-disjoint'
            simplified=[]
            if state=='single-simple-boundary':
                loop=loops[0]
                for a,b,c in zip(loop[-1:]+loop[:-1],loop,loop[1:]+loop[:1]):
                    u=tuple(b[k]-a[k] for k in range(3));v=tuple(c[k]-b[k] for k in range(3))
                    cross=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
                    if any(cross) or sum(u[k]*v[k] for k in range(3))<=0:simplified.append(b)
                if len(simplified)<3:state='zero-area-boundary'
            theoretical=len(simplified)-2 if state=='single-simple-boundary' else len(part)
            gain=max(0,len(part)-theoretical);saving+=gain
            records.append({'faceIds':sorted(part),'originalFaces':len(part),'state':state,
                'boundaryEdges':len(boundary),'boundaryVerticesAfterExactCollinearRemoval':len(simplified),
                'theoreticalFaces':theoretical,'saving':gain,'vertical':group['vertical'],
                'exactPlaneIntegerCoefficients':group['exactPlaneIntegerCoefficients']})
    return {'originalFaces':len(t),'degenerateFaceIds':plane['degenerateFaceIds'],
        'components':records,'theoreticalFaceSaving':saving,'theoreticalRemainingFaces':len(t)-saving,
        'geometryChanges':0,'equivalenceAccepted':False,
        'qualification':'Full-edge exact integer topology census only. Minimum polygon triangulation is theoretical; complete finite coverage, vertical surface, winding/multiplicity, Float32 result and actor/runtime proofs remain mandatory.'}

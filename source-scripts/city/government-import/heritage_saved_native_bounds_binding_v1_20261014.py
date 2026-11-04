"""Authenticate cached full source bounds; exact closed projection relation only."""
import json,math
def encoded(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def bind_record(entry,declaration,row):
    assert entry['uid']==declaration['uid']==row['uid'] and encoded(entry)==encoded(declaration['rawCurrentEntry'])
    assert declaration['source']['sha256']==row['sourceSHA256']==entry['sha256']
    p=row['completeOriginalPOSITIONProof'];assert p['sourceSHA256']==entry['sha256'] and p['allOriginalPositionVerticesAccounted'] is True
    assert row['completeFaces']==p['completeOriginalTriangles']==entry['triangles'] and row['completePositionVertices']==p['completeOriginalPositionVertices']
    meshes=row['actualRenderMeshes'];assert meshes and all(m['wholePositionVerticesIncludingUnused'] is True for m in meshes)
    assert sum(m['completePositionVertices']for m in meshes)==row['completePositionVertices'] and sum(m['completeIndexedFaces']for m in meshes)==row['completeFaces']
    if 'completeFourWorldBounds'in row:
        boxes=row['completeFourWorldBounds'];assert encoded(boxes[0])==encoded(p['originalWholeSourceBounds'])
    else:
        assert row['wholeUnusedPositionVerticesIncluded'] is True and row['sourceFacesOmitted']==0
        boxes=[p['originalWholeSourceBounds'],row['completeLiteralBounds'],row['completeLeftAssociatedF32Bounds'],row['completeBalancedF32Bounds']]
    assert len(boxes)==4
    for b in boxes:
        assert len(b)==2 and all(len(v)==3 for v in b)
        assert all(type(n)in(int,float)and math.isfinite(n)for v in b for n in v) and all(b[0][k]<=b[1][k]for k in range(3))
    return boxes
def closed_disjoint(boxes,domain):
    assert len(domain)==4 and all(type(x)in(int,float)and math.isfinite(x)for x in domain) and domain[0]<=domain[2] and domain[1]<=domain[3]
    return all(b[1][0]<domain[0]or b[0][0]>domain[2]or b[1][2]<domain[1]or b[0][2]>domain[3]for b in boxes)

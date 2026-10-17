"""Diagnose exact government mesh ownership, independently of roof area ratios.

This is provenance evidence, never import, placement or architectural approval.
The caller must separately verify original provider/native hashes and live inputs.
"""
import gzip
import hashlib
import json
import math
import struct


def document(raw):
    data=gzip.decompress(raw)
    assert len(data)>=20 and struct.unpack_from('<III',data)==(0x46546c67,2,len(data)), 'Invalid original GLB'
    length,kind=struct.unpack_from('<II',data,12)
    assert kind==0x4e4f534a and 20+length<=len(data)
    return json.loads(data[20:20+length])


def graph_reasons(gltf,model_id,triangles):
    """Require all original geometry to belong to one exact named FME root."""
    reasons=[]
    if gltf.get('asset',{}).get('version')!='2.0':reasons.append('gltf-version')
    if gltf.get('extensionsUsed') or gltf.get('extensionsRequired'):reasons.append('unhandled-source-extensions')
    if len(gltf.get('buffers',[]))!=1 or any('uri' in b for b in gltf.get('buffers',[])):reasons.append('external-or-multiple-source-buffers')
    scenes=gltf.get('scenes',[]);nodes=gltf.get('nodes',[]);meshes=gltf.get('meshes',[])
    if len(scenes)!=1 or len(scenes[0].get('nodes',[]))!=1:return reasons+['single-exact-source-root-required']
    root=scenes[0]['nodes'][0]
    if not isinstance(root,int) or not 0<=root<len(nodes):return reasons+['invalid-source-root']
    if nodes[root].get('name')!=model_id:reasons.append('source-root-name')
    matrix=nodes[root].get('matrix',[])
    pattern=[1,0,0,0,0,0,-1,0,0,1,0,0,None,None,None,1]
    if len(matrix)!=16 or any(v!=wanted for v,wanted in zip(matrix,pattern) if wanted is not None) or not all(isinstance(v,(int,float)) and math.isfinite(v) for v in matrix):reasons.append('original-unit-hkpd-root-pose')
    if any(k in nodes[root] for k in ['translation','rotation','scale']):reasons.append('ambiguous-root-pose')
    pending=[root];seen=set();owned=[];faces=0
    while pending:
        index=pending.pop()
        if not isinstance(index,int) or not 0<=index<len(nodes):reasons.append('invalid-child-node');continue
        if index in seen:reasons.append('cycle-or-repeated-node');continue
        seen.add(index);node=nodes[index]
        if index!=root:
            if node.get('name') not in [None,'',model_id]:reasons.append('foreign-named-child')
            if any(k in node for k in ['matrix','translation','rotation','scale']):reasons.append('additional-child-pose')
        if any(k in node for k in ['skin','weights','camera','extensions']):reasons.append('additional-source-actor')
        pending.extend(node.get('children',[]))
        if 'mesh' not in node:continue
        mesh=node['mesh']
        if not isinstance(mesh,int) or not 0<=mesh<len(meshes):reasons.append('invalid-mesh');continue
        owned.append(mesh)
        for primitive in meshes[mesh].get('primitives',[]):
            if primitive.get('mode',4)!=4 or primitive.get('targets') or primitive.get('extensions'):reasons.append('unhandled-primitive');continue
            if 'POSITION' not in primitive.get('attributes',{}) or 'indices' not in primitive:reasons.append('unhandled-geometry-accessor');continue
            accessors=gltf.get('accessors',[])
            for accessor in [primitive['indices'],*primitive['attributes'].values()]:
                if not isinstance(accessor,int) or not 0<=accessor<len(accessors):reasons.append('invalid-accessor');continue
                a=accessors[accessor]
                if 'sparse' in a or not isinstance(a.get('bufferView'),int):reasons.append('unhandled-accessor');continue
                views=gltf.get('bufferViews',[]);view=a['bufferView']
                if not 0<=view<len(views) or views[view].get('buffer',0)!=0:reasons.append('foreign-buffer-view')
            if isinstance(primitive['indices'],int) and 0<=primitive['indices']<len(accessors):
                count=accessors[primitive['indices']].get('count',0)
                if not isinstance(count,int) or count%3:reasons.append('invalid-index-count')
                else:faces+=count//3
    if seen!=set(range(len(nodes))):reasons.append('unowned-source-nodes')
    if len(owned)!=len(set(owned)) or set(owned)!=set(range(len(meshes))):reasons.append('unowned-or-repeated-source-meshes')
    if not meshes or faces!=triangles:reasons.append('original-face-accounting')
    return sorted(set(reasons))


def evidence(raw,row,context):
    model=row['native']['model'];form=row['source']['building'];uid=row['uid']
    matching=model['matching'];reasons=[]
    if hashlib.sha256(raw).hexdigest()!=row['sourceSHA256'] or model['asset']['sha256']!=row['sourceSHA256']:reasons.append('original-byte-integrity')
    if row['modelId']!=model['modelId'] or row['modelId'][1:11]!=form['buildingCSUID'][:10]:reasons.append('exact-source-georef')
    for key in ['officialCandidates','officialMatches','viewerMatches']:
        matches=matching.get(key,[])
        if len(matches)!=1:reasons.append('unique-'+key);continue
        match=matches[0]
        if match.get('objectId')!=form['objectId'] or match.get('buildingCSUID')!=form['buildingCSUID'] or (key=='viewerMatches' and match.get('uid')!=uid):reasons.append('exact-'+key)
        overlap=match.get('overlapOfSmallerFootprint');centroid=match.get('footprintCentroidDistanceMetres')
        if not all(isinstance(v,(int,float)) and math.isfinite(v) for v in [overlap,centroid]) or overlap<.98 or centroid>1:reasons.append('cached-spatial-'+key)
    if context['sourceSHA256']!=row['sourceSHA256']:reasons.append('context-source-integrity')
    projection=context['identity']
    if not projection.get('exactObjectAndCSUID'):reasons.append('exact-current-object-csuid')
    for key,minimum,maximum,reason in [
        ('targetCoveredBySourceProjection',.95,1.000000001,'full-source-target-coverage'),
        ('sourceExcessMaximumDistanceFromTargetM',0,10,'full-source-maximum-extent'),
        ('sourceExcessCoveredByUnrelatedFormsM2',0,1,'full-source-unrelated-overlap')]:
        value=projection.get(key)
        if not isinstance(value,(int,float)) or not math.isfinite(value) or not minimum<=value<=maximum:reasons.append(reason)
    graph=graph_reasons(document(raw),row['modelId'],row['triangles']);reasons.extend(graph)
    return {'uid':uid,'sourceSHA256':row['sourceSHA256'],'originalRootName':row['modelId'],
        'sourceGraphVerified':not graph,'provenanceAndSpatialDiagnosticPassed':not reasons,
        'reasons':sorted(set(reasons)),'fullProjection':projection,'installationApproved':False,
        'qualification':'Exact original graph ownership and cached/current spatial evidence only. An owned roof extension is not an architectural judgement; this diagnostic does not replace current full-projection, support, terrain, foundation, browser or publication gates.'}

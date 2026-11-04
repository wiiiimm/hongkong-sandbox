"""Normalize the two existing single-replacement descriptor schemas only.

Does not validate geometry or grant approval. Callers still verify exact current
bytes, ownership, envelope, target set and complete retained actor evidence.
"""
def replacement(entry):
    values=[]
    if 'replaces' in entry:
        row=entry['replaces'];assert set(row)=={'url','sha256','retainedUids'}
        values.append(dict(url=row['url'],sha256=row['sha256'],retainedUids=list(row['retainedUids'])))
    if 'replacesMany' in entry:
        rows=entry['replacesMany'];assert len(rows)==1,'Only one exact old terrain is supported'
        row=rows[0];assert row['path']=='3d-viewer/'+row['url']
        values.append(dict(url=row['url'],sha256=row['sha256'],retainedUids=list(row['targetUids'])))
    assert values and all(v==values[0]for v in values),'Conflicting or absent replacement descriptors'
    value=values[0];assert value['url'].startswith('city/data/')and '..'not in value['url']
    assert len(value['sha256'])==64 and all(c in '0123456789abcdef'for c in value['sha256'])
    assert value['retainedUids']and len(value['retainedUids'])==len(set(value['retainedUids']))
    return value

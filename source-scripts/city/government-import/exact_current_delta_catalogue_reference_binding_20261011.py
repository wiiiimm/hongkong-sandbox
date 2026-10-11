"""Compare two declared catalogue-ref schemas without dropping path semantics."""
def verify_delta_catalogue_refs(delta_refs,regional_refs,manifest):
 expected=['3d-viewer/'+p for p in manifest['officialModelCatalogues']]
 assert len(expected)==len(set(expected))==len(delta_refs)==len(regional_refs)
 assert [r['path'] for r in delta_refs]==[r['path'] for r in regional_refs]==expected
 for d,r,p in zip(delta_refs,regional_refs,expected):
  assert set(d)=={'path','sha256','originalPath'} and set(r)=={'path','sha256'}
  assert d['originalPath']==d['path']==r['path']==p
  assert d['sha256']==r['sha256'] and isinstance(d['sha256'],str) and len(d['sha256'])==64
  assert all(c in 'abcdef0123456789' for c in d['sha256'])
 return True

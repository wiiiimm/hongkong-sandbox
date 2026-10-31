"""Reject changed/missing/additional siblings; original overlap policy stays active."""
from pool_reviewed_sibling_publisher_v1_20261017 import checked_overlap
from primrose_compound_foundation_v2_20261015 import module
from run import HERE
pub=module('pool_overlap_test',HERE.parent/'island-detail-integration/publish.py')
a={'coarseCells':[481,376,488,382],'nativeMesh':'candidate'}
b={'coarseCells':[476,380,482,384],'nativeMesh':'retained'}
checked_overlap(pub.check_patch_overlap,a,b,a,[b])
for actual,others in [(dict(a,nativeMesh='changed'),[b]),(a,[]),(a,[b,b]),(a,[dict(b,nativeMesh='changed')]),(a,[b,{'coarseCells':[483,377,484,378]}])]:
 try:checked_overlap(pub.check_patch_overlap,a,b,actual,others)
 except AssertionError:pass
 else:raise AssertionError('Adverse case accepted')
print('Positive case and five adverse overlap cases pass')

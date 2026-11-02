"""Bind already inspected image bytes for the SAME named source/view capture.

Content-inspection coverage only. No software, visual or installation approval.
Different UID, viewport, time, capture role or bytes always require own review.
"""
import hashlib,json,re
from pathlib import Path

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def capture_key(path):return re.sub(r'^(staged|live)-','',Path(path).name)
def checked_path(root,value):
    path=(root/value).resolve();assert path.is_relative_to(root.resolve()),'Image/review outside root';return path

def bind_inspected_bytes(targets,review_paths,root):
    root=Path(root).resolve();known={};reviews=[]
    for name in review_paths:
        path=checked_path(root,name);review=json.loads(path.read_text())
        assert review['reviewer']=='ROOT'and review['allListedExportsActuallyInspected']is True,'Actual ROOT image inspection required'
        for key in ['unresolvedVisualFailures','unresolvedVisibleFailuresInListedExports','unresolvedAtomicVisualFailures']:
            assert not review.get(key,[]),'Unresolved review context cannot be inherited'
        review_ref=dict(path=str(path.relative_to(root)),sha256=sha(path));reviews.append(review_ref)
        declared={}
        for item in review['images']:
            assert set(item)>={'path','sha256'}
            assert item['path']not in declared,'Duplicate image path in inspection'
            declared[item['path']]=item['sha256'];image=checked_path(root,item['path'])
            assert sha(image)==item['sha256'],'Previously inspected image bytes changed'
            known.setdefault((capture_key(image),item['sha256']),[]).append(dict(image=dict(path=item['path'],sha256=item['sha256']),inspection=review_ref))
    matched=[];unseen=[];paths=set()
    for name in targets:
        path=checked_path(root,name);relative=str(path.relative_to(root));assert relative not in paths,'Duplicate target image';paths.add(relative)
        item=dict(path=relative,sha256=sha(path));prior=known.get((capture_key(path),item['sha256']))
        if prior:matched.append(dict(**item,captureKey=capture_key(path),priorActualInspections=prior))
        else:unseen.append(item)
    return dict(reviewCoverageOnly=True,softwareAcceptance=False,visualAcceptance=False,publication=False,
                matched=matched,unseen=unseen,reviewRefs=reviews,exactCaptureAndByteIdentityRequired=True)

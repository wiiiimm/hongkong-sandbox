"""Read back every saved publication destination after an uncredited rollback."""
import hashlib

def verify(root,failure,history):
    root=root.resolve()
    assert failure['allPublicDestinationsRestored']and failure['currentPointerRestoredNotDerivedCredit']and not failure['derivedInstalledReviewHistoryRetained']and not failure['rollbackErrors']
    destinations=history['allMutableDestinations'];assert destinations and len(destinations)==len(set(destinations))
    old=history['mutableCurrentByteSnapshots'];expected={r['originalPath']:r['originalSHA256']for r in old};assert len(expected)==len(old)and set(expected)<=set(destinations)
    def path(relative):
        p=(root/relative).resolve();assert p.is_relative_to(root);return p
    for row in old:
        saved=row['savedHistoricalBytes'];assert saved['sha256']==row['originalSHA256']and hashlib.sha256(path(saved['path']).read_bytes()).hexdigest()==row['originalSHA256']
    rows=[]
    for name in sorted(destinations):
        p=path(name);actual=hashlib.sha256(p.read_bytes()).hexdigest()if p.exists()else None;assert actual==expected.get(name),name
        rows.append(dict(path=name,restoredSHA256=actual))
    return rows

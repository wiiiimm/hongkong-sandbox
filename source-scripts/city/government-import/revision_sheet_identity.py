"""Resolve source sheet from verified member hashes, independent of cache layout."""
from run import ROOT,read


def source_sheet(model,revisions,*,reader=None):
    reader=reader or (lambda path:read(ROOT/path))
    hashes=model['sourceHashes']
    assert hashes and model['sourceEntry'] in hashes
    found=[]
    for revision in revisions:
        download=reader(revision['download'])
        assert download['sheet']==revision['sheet']
        assert download['sha256']==revision['archiveSHA256']
        assert download['directorySHA256']==revision['directorySHA256']
        entries={entry['name']:entry['sha256'] for entry in download['entries']}
        assert len(entries)==len(download['entries'])
        if all(entries.get(name)==sha for name,sha in hashes.items()):found.append(revision['sheet'])
    assert len(found)==1,'Original members lack one exact verified sheet receipt'
    return found[0]

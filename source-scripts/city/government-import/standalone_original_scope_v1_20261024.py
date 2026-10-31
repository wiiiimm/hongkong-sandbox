"""Narrow standalone entry admission; existing global dependency guards still apply."""
SOURCES={'landsd/93417:0':'debfebe52c8a04231cd20bdbfeaa9057f28af6e9df054769f9c57118f4d5aa60'}


def verify_entry(entry, sources):
    assert sources==SOURCES, 'Standalone approval is limited to the exact University Hall source'
    assert entry['uid'] in SOURCES and entry['sha256']==SOURCES[entry['uid']], 'Different original source'
    for key in ['supportDependencies','retainedBasicSupportDependencies','suppressesBuildingUids']:
        assert key not in entry or entry[key]==[], 'Standalone source cannot require or suppress another actor'
    assert not entry.get('footprintScope'), 'No partial-source footprint routing'
    assert not entry.get('embeddedGeometry'), 'No embedded replacement geometry'

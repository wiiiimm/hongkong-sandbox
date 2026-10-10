"""Fresh Man Hei dependency replay of the unchanged reviewed Man Fuk adapter.

Only isolated module input-directory globals change. No frozen producer/proof
is edited; the complete existing raw/provider/source/installed-ManOi guards
are replayed. Additional unique native source and exact caller-input checks
protect this fresh dependency capture. This grants identity only, no physics.
"""
import importlib.util
from run import ROOT,HERE,read,connect
from man_hei_named_mandatory_original_platform_identity_20261010 import PLATFORM,PLATFORM_SHA,RELATED
DOC=ROOT/'docs/astra-city/government-import/government-xl-man-hei-dependent-platform-current-inputs-v1-20261010'
INSTALLED=DOC.parent/'government-xl-man-hei-dependent-platform-installed-man-oi-v1-20261010'
RAW=DOC.parent/'government-xl-man-hei-dependent-platform-current-raw-v1-20261010'
MODEL='B364461960802063C0';RELATED_MODEL='B364721945401063C0'

def adapter():
    spec=importlib.util.spec_from_file_location('manhei_fresh_independent_platform',HERE/'man_fuk_current_bound_envelope_identity_v3_20261010.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.DOC=DOC;m.INSTALLED=INSTALLED
    return m

def verify_native_rows(rows,related_sha):
    assert len(rows)==2 and len({r['sourceKey'] for r in rows})==2
    expected={MODEL:PLATFORM_SHA,RELATED_MODEL:related_sha}
    assert {r['model']['modelId'] for r in rows}==set(expected)
    for r in rows:
        assert r['sourceKey'].endswith('/'+r['model']['modelId']) and len(r['sourceKey'].split('/'))==2
        assert r['model']['asset']['sha256']==expected[r['model']['modelId']]
    return True

def verify_files(row,context,local):
    assert row['uid']==PLATFORM
    assert row==read(DOC/'selection.json.gz')['rows'][0] and context==read(DOC/'context.json.gz')['rows'][0]
    m=adapter();source=read(DOC/'original-source-lookup.json.gz');verify_native_rows(source['rows'],m.RELATED_SHA)
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY');actual=m.native_rows(c);verify_native_rows(actual,m.RELATED_SHA);assert actual==source['rows']
    return m.verify_files(row,context,local)

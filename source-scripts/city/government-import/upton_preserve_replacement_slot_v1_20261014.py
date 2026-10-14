"""Metadata ordering only: preserve exact captured renderer patch sequence."""
def preserve_slot(original,proposed,old_url,new_url):
    before=original['terrainPatches'];after=proposed['terrainPatches'];old=[r for r in before if r['url']==old_url];new=[r for r in after if r['url']==new_url]
    assert len(old)==len(new)==1 and len({r['url']for r in before})==len(before)and len({r['url']for r in after})==len(after)
    assert old_url not in {r['url']for r in after}and new_url not in {r['url']for r in before}
    assert len(before)==len(after)
    expected={r['url']:r for r in before if r['url']!=old_url};actual={r['url']:r for r in after if r['url']!=new_url};assert actual==expected
    proposed['terrainPatches']=[new[0]if r['url']==old_url else r for r in before]
    return dict(oldIndex=next(i for i,r in enumerate(before)if r['url']==old_url),replacementIndex=next(i for i,r in enumerate(proposed['terrainPatches'])if r['url']==new_url),allOtherPatchMetadataAndOrderPreserved=True,terrainGeometryChanged=False)

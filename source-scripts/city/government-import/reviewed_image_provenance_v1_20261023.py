"""Verify reviewed pixels, including explicit byte-identical desktop aliases."""
def verify_image(image, check):
    keys = set(image)
    assert keys in ({'path', 'sha256'}, {'path', 'sha256', 'viewedOriginalPath', 'copiedByteIdentically'})
    check(dict(path=image['path'], sha256=image['sha256']))
    if 'viewedOriginalPath' in image:
        assert image['copiedByteIdentically'] is True
        check(dict(path=image['viewedOriginalPath'], sha256=image['sha256']))

"""Decode the acquired original dated tile and preserve an unfitted source crop."""
import json
import shutil
import sys
import uuid
import zipfile
from pathlib import Path
import numpy as np
from PIL import Image
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v2_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from bounded_response_file_v1_20261103 import receive
from hk1980_geotiff_window_v1_20261103 import window
from exact_packed_world_geometry_v2_20261103 import decode_original_world_triangles

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-source43101-dated-orthophoto-pixels-v1-20261103'
ARCHIVE = 'government-xl-source43101-dated-orthophoto-archive-v1-20261103'
SELECT = 'government-xl-source43101-current-selection-v1-20261029'
PROVIDER = 'government-xl-after-sha-tin-43101-provider-roots-v1-20261029'
AERIAL = 'government-xl-source43101-unfitted-official-aerial-v1-20261103'


def owned():
    local, out = HERE / 'local' / BATCH, BASE / BATCH
    lease = read(local / 'reservation.json')
    assert reservations.owns(lease)
    refs = [Path(__file__), HERE / 'bounded_response_file_v1_20261103.py', HERE / 'hk1980_geotiff_window_v1_20261103.py', HERE / 'exact_packed_world_geometry_v2_20261103.py']
    def take(batch, name, structured=True):
        _, pins = authenticate(BASE / batch)
        p = BASE / batch / name
        assert digest(p.read_bytes()) == pins[str(p.relative_to(ROOT))]
        refs.extend([BASE / batch / 'result.json', p])
        return read(p) if structured else p
    prior = take(ARCHIVE, 'summary.json')
    original = prior['originalArchive']
    archive = ROOT / original['archive']
    assert original['status'] == 'complete' and archive.stat().st_size == original['receivedBytes'] and digest(archive.read_bytes()) == original['sha256']
    assert shutil.disk_usage(local.parent).free > 2 * sum(m['rawBytes'] for m in prior['archiveMembers']) + 1_000_000_000
    extracted = []
    with zipfile.ZipFile(archive) as z:
        assert len(z.infolist()) == len(prior['archiveMembers'])
        for entry, expected in zip(z.infolist(), prior['archiveMembers']):
            assert (entry.filename, entry.CRC, entry.file_size, entry.compress_size, entry.compress_type) == (expected['name'], expected['crc32'], expected['rawBytes'], expected['compressedBytes'], expected['compression'])
            if entry.is_dir():
                continue
            dest = local / Path(entry.filename).name
            with z.open(entry) as source:
                received = receive(source, dest, entry.file_size)
            assert received['receivedBytes'] == entry.file_size
            extracted.append(dict(path=str(dest.relative_to(ROOT)), archiveMember=entry.filename, crcVerifiedByZipReader=True, **received))
            print(json.dumps(dict(extracted=entry.filename, bytes=entry.file_size)), flush=True)
    assert reservations.owns(lease)
    tif = next(ROOT / e['path'] for e in extracted if e['path'].lower().endswith('.tif'))
    tfw = next(ROOT / e['path'] for e in extracted if e['path'].lower().endswith('.tfw'))
    tfw_bytes = tfw.read_bytes()
    out.mkdir(exist_ok=True)
    (out / 'official-world-file.tfw').write_bytes(tfw_bytes)
    source = take(SELECT, 'selection.json.gz')['rows'][0]
    proof = take(PROVIDER, 'summary.json')
    asset = ROOT / source['candidate']['path']
    assert source['uid'] == 'landsd/43101:0' and digest(asset.read_bytes()) == source['sourceSHA256'] == proof['sourceSHA256'] == prior['sourceSHA256']
    refs.append(asset)
    roots = proof['roots']
    assert len(roots) == 2 and sum(r['completeFaces'] for r in roots) == 24308
    bounds = [min(r['sourceWorldBounds'][0][0] for r in roots) + 834500 - 15,
              816500 - max(r['sourceWorldBounds'][1][2] for r in roots) - 15,
              max(r['sourceWorldBounds'][1][0] for r in roots) + 834500 + 15,
              816500 - min(r['sourceWorldBounds'][0][2] for r in roots) + 15]
    Image.MAX_IMAGE_PIXELS = 400_000_000
    with Image.open(tif) as im:
        tags = {key: list(im.tag_v2[key]) if isinstance(im.tag_v2[key], tuple) else im.tag_v2[key] for key in [33550, 33922, 34264, 34735, 34737] if key in im.tag_v2}
        metadata = dict(size=list(im.size), mode=im.mode, georeferenceTags=tags, officialWorldFile=tfw_bytes.decode('ascii'), sourceBoundsHK1980=bounds, extractedMembers=extracted)
        save(out / 'raster-metadata.json', metadata)
        try:
            crop = window(im.tag_v2, im.size, bounds)
        except (KeyError, AssertionError) as error:
            result = dict(rasterMetadata=metadata, pixelCropPending=True, pendingReason=type(error).__name__ + ': ' + str(error), sourceGeometryChanges=0, sourcePoseChanges=0, identityAccepted=False, installationApproved=False, publication=False)
        else:
            sx, sy = crop['pixelSizeM']; l, r, bottom, top = crop['hk1980Extent']
            world = [float(v) for v in tfw_bytes.decode('ascii').split()]
            assert len(world) == 6 and abs(world[0] - sx) <= 1e-9 and world[1:3] == [0, 0] and abs(world[3] + sy) <= 1e-9
            tie = list(im.tag_v2[33922])
            assert abs(world[4] - tie[3] - sx / 2) <= 1e-7 and abs(world[5] - tie[4] + sy / 2) <= 1e-7
            pixels = im.crop(tuple(crop['pixelWindow'])).convert('RGB')
            raw = out / 'original-dated-raster-crop.png'; pixels.save(raw); refs.append(raw)
            tri = decode_original_world_triangles(asset.read_bytes())
            pieces = np.split(tri, [roots[0]['completeFaces']])
            assert len(tri) == 24308 and all(digest(p.astype('<f8').tobytes()) == root['providerWorldSHA256'] for p, root in zip(pieces, roots))
            logo = Image.open(take(AERIAL, 'lands-department-logo.jpg', False)).convert('RGB')
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import shapely
            from matplotlib.offsetbox import OffsetImage, AnnotationBbox
            fig, axes = plt.subplots(1, 2, figsize=(14, 9), dpi=160)
            for ax in axes:
                ax.imshow(pixels, extent=crop['hk1980Extent'], interpolation='nearest')
                ax.set_aspect('equal'); ax.ticklabel_format(useOffset=False, style='plain'); ax.tick_params(labelsize=6)
                ax.add_artist(AnnotationBbox(OffsetImage(np.asarray(logo), zoom=24 / logo.height), (.04, .04), xycoords='axes fraction', frameon=True, box_alignment=(0, 0)))
            for piece, color in zip(pieces, ['#ff5544', '#00eeff']):
                projection = shapely.union_all(shapely.polygons(piece[:, :, [0, 2]]))
                for poly in shapely.get_parts(projection):
                    if hasattr(poly, 'exterior'):
                        q = np.asarray(poly.exterior.coords)
                        axes[1].plot(q[:, 0] + 834500, 816500 - q[:, 1], color=color, linewidth=.7)
            axes[0].set_title('Official TDOP2025 pixels; 3 & 11 January 2025')
            axes[1].set_title('Both original roots; native EPSG2326, no fitting')
            fig.suptitle('43101 complete original source against the dated official orthophoto')
            fig.text(.02, .015, 'Aerial Photograph from Lands Department / HKSAR Government / CSDI. T8-SW-C, TDOP2025.', fontsize=8)
            fig.tight_layout(rect=[0, .04, 1, .96])
            image = out / 'unfitted-dated-official-aerial-two-roots.png'; fig.savefig(image); plt.close(fig); refs.append(image)
            result = dict(rasterMetadata=metadata, pixelCropPending=False, crop=crop, images=[dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes())) for p in [raw, image]], allOriginalRoots=2, allOriginalFaces=24308, sourceGeometryChanges=0, sourcePoseChanges=0, identityAccepted=False, installationApproved=False, publication=False)
    result.update(uids=prior['uids'], sourceSHA256=source['sourceSHA256'], archive=original, officialIndexAttributes=prior['officialIndexAttributes'], allArchiveMemberCRCsVerified=True, sourceEvidenceInterpretationUsedAI=False, aiGeometryModelling=False, visualReviewPending=True)
    save(out / 'summary.json', result)
    assert reservations.owns(lease)
    refs.extend(p for p in out.iterdir() if p.is_file())
    module('source43101_dated_pixels_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'unfitted-dated-primary-raster-context-for-both-original-roots', list(dict.fromkeys(refs)), result)
    print(json.dumps(dict(cropPending=result['pixelCropPending'], metadata=metadata, images=result.get('images', []))), flush=True)


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not (BASE / BATCH).exists() and not (HERE / 'local' / BATCH).exists()
        claim = reservations.claim('source43101-dated-pixels-' + str(uuid.uuid4()), ['building:landsd/43101:0', 'immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
        assert claim['ok'], 'Source reservation unavailable'
        execute_reserved(claim['reservation'], HERE / 'local' / BATCH / 'reservation.json', [sys.executable, __file__, '--owned'])

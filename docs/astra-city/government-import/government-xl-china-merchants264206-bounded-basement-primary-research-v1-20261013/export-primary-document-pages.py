"""Render only retrieved primary document pages; no project/model imports."""
import hashlib
import json
from pathlib import Path
import fitz

HERE = Path(__file__).resolve().parent
SELECTION = {
    'shun-tak-owner-circular-20200826.pdf': (0, 84, 85),
    'mtr-sheung-wan-layout.pdf': (0,),
}

def main():
    out = HERE / 'document-page-exports'
    out.mkdir(exist_ok=False)
    rows = []
    retrieval = json.loads((HERE / 'retrieval.json').read_text())
    for filename, indices in SELECTION.items():
        raw = HERE / 'primary-documents' / filename
        sha = hashlib.sha256(raw.read_bytes()).hexdigest()
        receipt = next(x for x in retrieval['sources'] if x['filename'] == filename)
        assert receipt['saved'] and receipt['sha256'] == sha
        doc = fitz.open(raw)
        for i in indices:
            page = doc[i]
            pix = page.get_pixmap(matrix=fitz.Matrix(2400 / max(page.rect.width, page.rect.height), 2400 / max(page.rect.width, page.rect.height)), alpha=False)
            png = out / (raw.stem + f'-physical-page-{i + 1:03d}-2400px.png')
            pix.save(png)
            text = out / (raw.stem + f'-physical-page-{i + 1:03d}-text.txt')
            with text.open('x', encoding='utf-8') as stream:
                stream.write(page.get_text())
            rows.append({'sourceFile': filename, 'sourceSHA256': sha, 'totalSourcePages': len(doc), 'physicalPageOneBased': i + 1, 'png': str(png.relative_to(HERE)), 'width': pix.width, 'height': pix.height, 'pngSHA256': hashlib.sha256(png.read_bytes()).hexdigest(), 'text': str(text.relative_to(HERE)), 'textSHA256': hashlib.sha256(text.read_bytes()).hexdigest()})
        doc.close()
    with (HERE / 'document-page-exports.json').open('x', encoding='utf-8') as stream:
        json.dump({'renderer': 'PyMuPDF', 'rendererVersion': fitz.VersionBind, 'documentOnlyNoModelGeometry': True, 'pages': rows}, stream, indent=2)
        stream.write('\n')
    print(json.dumps(rows, indent=2))

if __name__ == '__main__':
    main()

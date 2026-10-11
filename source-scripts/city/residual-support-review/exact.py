"""Reuse the native-facet builder for this isolated reserved patch set."""
import sys,pathlib,json
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/residual-support-review';sys.path.insert(0,str(ROOT/'source-scripts/city/assembly-support-review'));import exact_tin as e
bundle=json.loads((DOC/'terrain-patches.json').read_bytes());ids=[pathlib.Path(p['path']).stem.replace('support-native-','')for b in bundle['bundles']for p in b['patches']];e.HERE=HERE;e.OUT=DOC;sys.argv=['exact.py','--ids',*ids];e.main()

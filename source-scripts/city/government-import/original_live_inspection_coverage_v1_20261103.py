"""Prepare exact inspection coverage for a completed live-browser report.

Authenticates frozen reviews and committed partial ROOT reviews. Never records
visual, physical, software or publication acceptance, even with complete coverage.
"""
import argparse,hashlib,json,subprocess
from pathlib import Path
from run import ROOT,read,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from inspected_export_byte_binding_v1_20261103 import bind_inspected_bytes,checked_path


def report_targets(source,report,expected_count,root):
    assert report['passed']is True and not report['errors'],'Completed passing browser report required'
    targets=[]
    for item in [*report['views'],*report['retainedNativeOwnViews']]:
        if 'time'not in item:continue
        path=(source/item['file']).resolve();assert path.is_relative_to(root.resolve()),'Capture outside root'
        targets.append(str(path.relative_to(root)))
    assert len(targets)==len(set(targets))==expected_count,'Complete unique report image set required'
    return targets


def committed_review(path,root,git_read=None):
    path=checked_path(root,path);relative=str(path.relative_to(root))
    if git_read is None:git_read=lambda value:subprocess.check_output(['git','show','HEAD:'+value],cwd=root)
    committed=git_read(relative);assert committed==path.read_bytes(),'ROOT review differs from committed bytes'
    value=json.loads(committed);assert value['reviewer']=='ROOT'and value['allListedExportsActuallyInspected']is True
    return dict(path=relative,sha256=digest(committed),binding='exact-committed-HEAD-bytes')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=Path,required=True);ap.add_argument('--report-name',default='live-browser.json');ap.add_argument('--expected-count',type=int,required=True);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--frozen-review',type=Path,action='append',default=[]);ap.add_argument('--committed-review',type=Path,action='append',default=[])
    a=ap.parse_args();source=checked_path(ROOT,a.source);output=checked_path(ROOT,a.out);assert source.is_relative_to(ROOT/'docs/astra-city/government-import')and output.is_relative_to(ROOT/'docs/astra-city/government-import')and not output.exists()
    report_path=(source/a.report_name).resolve();assert report_path.parent==source and 1<=a.expected_count<=1000
    before=digest(report_path.read_bytes());report=read(report_path);targets=report_targets(source,report,a.expected_count,ROOT);reviews=[];bindings=[]
    for name in a.frozen_review:
        p=checked_path(ROOT,name);receipt,pins=authenticate(p.parent);assert pins[str(p.relative_to(ROOT))]==digest(p.read_bytes());reviews.append(p);bindings.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()),binding='pinned-Neon-completed-frozen-evidence',receipt=dict(path=str((p.parent/'result.json').relative_to(ROOT)),sha256=digest((p.parent/'result.json').read_bytes()))))
    for name in a.committed_review:
        p=checked_path(ROOT,name);bindings.append(committed_review(p,ROOT));reviews.append(p)
    assert reviews,'Actual prior ROOT reviews required'
    coverage=bind_inspected_bytes(targets,reviews,ROOT);assert digest(report_path.read_bytes())==before
    result=dict(**coverage,report=dict(path=str(report_path.relative_to(ROOT)),sha256=before),expectedReportImages=a.expected_count,matchedImages=len(coverage['matched']),unseenImages=len(coverage['unseen']),reviewBindings=bindings,installationApproved=False,qualification='Image-content coverage only. Each match is the same capture key and exact already-inspected image bytes, with authenticated frozen or exact committed prior ROOT review. Complete passing live software still requires independent scope/runtime/source review. Any unseen or changed image needs actual inspection; complete image coverage alone never records acceptance.')
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k]for k in ['expectedReportImages','matchedImages','unseenImages','visualAcceptance','softwareAcceptance','installationApproved']}))

if __name__=='__main__':main()

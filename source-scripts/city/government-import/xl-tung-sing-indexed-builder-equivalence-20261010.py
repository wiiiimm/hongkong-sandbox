"""Full in-memory builder output equality using actual immutable source fixtures."""
import importlib.util,json,time,numpy as np
from run import ROOT,HERE,read,save,digest
from indexed_original_parent_clip_builder_20261010 import indexed_builder
DOC=ROOT/'docs/astra-city/government-import/government-xl-tung-sing-indexed-builder-equivalence-20261010'
SOURCE=ROOT/'docs/astra-city/government-import/government-xl-tung-sing-original-pair-source-tin-context-20261010/complete-original-source-tin.json.gz'
PARENT=ROOT/'3d-viewer/city/data/government-native-163705-0.json'
def main():
    assert not DOC.exists();spec=importlib.util.spec_from_file_location('indexed_original_resolve_pass',HERE/'resolve-pass.py');original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original);fast,binding=indexed_builder(original);source=read(SOURCE);alltri=np.asarray(source['position'],float).reshape(-1,3)[np.asarray(source['index'],int).reshape(-1,3)];parent=read(PARENT);rows=[]
    for cells in [[55,4,61,10],[63,20,69,26]]:
        group={'cells':cells,'uids':['landsd/53800:0','landsd/126434:0']};bb=original.extent(cells,parent);native=alltri[(alltri[:,:,0].max(axis=1)>=bb[0])&(alltri[:,:,0].min(axis=1)<=bb[2])&(alltri[:,:,2].max(axis=1)>=bb[1])&(alltri[:,:,2].min(axis=1)<=bb[3])];assert len(native)
        outputs=[];times=[];guards=[]
        for builder in [original.make_patch,fast]:
            real=builder.__globals__['validate_patch'];captured=[]
            def capture_and_validate(patch,before):
                captured.append(json.dumps(patch,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
                return real(patch,before)
            builder.__globals__['validate_patch']=capture_and_validate;start=time.monotonic()
            try:
                builder(group,parent,native,[],parent_url='city/data/government-native-163705-0.json',parent_sha256=digest(PARENT.read_bytes()),terrain_triangle_budget=100000);guard=None
            except Exception as e:guard=[type(e).__name__,str(e)]
            finally:builder.__globals__['validate_patch']=real
            assert len(captured)==1;times.append(time.monotonic()-start);outputs.append(captured[0]);guards.append(guard)
        assert outputs[0]==outputs[1] and guards[0]==guards[1];row={'cells':cells,'originalSourceFacets':len(native),'wholeOutputBytesIdentical':True,'wholeOutputSHA256':digest(outputs[0]),'unchangedRealValidatorOutcome':guards[0],'candidateAccepted':guards[0] is None,'originalSeconds':times[0],'indexedSeconds':times[1]};rows.append(row);print(row,flush=True)
    errors=[]
    for name,tri,budget in [('existing-water-clamp-negative',np.asarray([[[0,0,0],[1,0,0],[0,0,1]]],float),100000),('existing-budget-negative',native,0)]:
        observed=[]
        for builder in [original.make_patch,fast]:
            try:builder(group,parent,tri,[],parent_url='city/data/government-native-163705-0.json',parent_sha256=digest(PARENT.read_bytes()),terrain_triangle_budget=budget)
            except Exception as e:observed.append([type(e).__name__,str(e)])
            else:observed.append(None)
        assert observed[0] is not None and observed[0]==observed[1];errors.append({'fixture':name,'identicalOriginalGuardFailure':observed[0]})
    save(DOC/'result.json',{'actualFixtures':rows,'guardNegatives':errors,'builderBinding':binding,'inputHashes':{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in [SOURCE,PARENT,HERE/'resolve-pass.py',HERE/'parent_cell_clip_broad_phase_20261010.py',HERE/'indexed_original_parent_clip_builder_20261010.py']},'wholeOutputBytesIdentical':True,'newGeometryWritten':False,'productionUsed':False,'physicalAccepted':False,'qualification':'Actual source/current-parent bounded full make_patch replay. Complete generated output captured at validator entry, then the unchanged real validator invoked for both implementations. Identical serialized output and existing guard failures. Rejected source-only rectangles do not receive acceptance credit. No output candidate written and no source, live surface, numeric clipping threshold or acceptance contract changed.'})
if __name__=='__main__':main()

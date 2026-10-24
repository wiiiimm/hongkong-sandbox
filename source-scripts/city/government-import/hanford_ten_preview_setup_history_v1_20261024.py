"""Archive corrected preview failures as setup history, never model holds."""
from run import ROOT,HERE,save
from primrose_compound_foundation_v2_20261015 import module
P='government-xl-next-repairs-hanford-ten-original-'

def main():
    base=ROOT/'docs/astra-city/government-import';out=base/(P+'preview-setup-history-v1-20261024');assert not out.exists();refs=[__file__]
    rows=[]
    for version,reason in [(1,'Required sourceTile metadata absent from two historical prepared entries; V2binds exact native input sheet/result.'),(2,'Desktop all20exports pass. Mobile authored-yaw tower194725fails complete framing after12exports; V3widens capture box only, retains full framing gate.')]:
        name=P+'unapproved-preview-v'+str(version)+'-20261024';doc=base/name;assert not(doc/'result.json').exists()
        refs.append(HERE/('hanford_ten_unapproved_original_preview_v'+str(version)+'_20261024.py'))
        refs.extend(p for p in doc.rglob('*')if p.is_file());refs.extend(p for p in(HERE/'local'/name).rglob('*')if p.is_file()and p.name!='reservation.json')
        rows.append(dict(batch=name,outcome='preview-setup-failure-corrected-in-successor',reason=reason,modelCorruption=False,permanentHold=False,installationApproved=False))
    result=dict(rows=rows,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publication=False)
    save(out/'setup-history.json',result)
    module('hanford_setup_history_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(out.name,'hanford-corrected-private-preview-setup-history',[ROOT/p if isinstance(p,str)else p for p in refs],result)

if __name__=='__main__':main()

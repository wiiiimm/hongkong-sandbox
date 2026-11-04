"""Freeze the subset passing original-source, patched terrain and neighbour checks."""
import importlib.util,shutil
from run import ROOT,HERE,read,save,digest,reservations
DOC=ROOT/'docs/astra-city/government-import/government-200-20260911/resolution';LOCAL=HERE/'local/government-198-resolution-20260911';STAGE=HERE/'accepted/government-198-resolution-20260911'
s=importlib.util.spec_from_file_location('policy',HERE/'acceptance-policy.py');policy=importlib.util.module_from_spec(s);s.loader.exec_module(policy)
receipt=read(LOCAL/'reservation.json');assert reservations.owns(receipt)
source=read(DOC/'selection.json.gz');metrics=read(DOC/'staged-metrics.json');neighbours=read(DOC/'neighbour-checks.json');validation=read(DOC/'staged-validation.json');resolution=read(DOC/'source-resolution.json')
for rel,h in metrics['inputHashes'].items():assert digest((ROOT/rel).read_bytes())==h,'Metrics input changed: '+rel
for rel,h in neighbours['sourceInputHashes'].items():assert digest((ROOT/rel).read_bytes())==h,'Neighbour source changed'
by_source={r['uid']:r for r in source['rows']};by_metric={r['uid']:r for r in metrics['rows']};by_validation={r['uid']:r for r in validation['results']}
accepted=[];selected_patches=[]
for patch in neighbours['patches']:
    if patch['blockedBy']:continue
    for uid in patch['uids']:
        v=by_validation[uid];assert v['outcome']!='validation-exception' and not v['concerns']
        reasons=policy.reasons({'state':'runtime-validated-awaiting-acceptance','sourceSHA256':by_source[uid]['candidate']['entry']['sha256']},by_metric[uid],metrics['profiles']['mobile']);assert not reasons,(uid,reasons)
    accepted.extend(patch['uids']);selected_patches.append(patch)
assert len(accepted)==9
cat=read(LOCAL/'candidates/catalogue.json');cat['models']=[];cat['area']='Verified original government models with native terrain · September 2026';STAGE.mkdir(parents=True,exist_ok=True)
for uid in accepted:
    entry=dict(by_source[uid]['candidate']['entry']);entry.update(placementReviewed=True,sourceIdentityReviewed=True,identityReviewApproved=True,priority='detail',placementReview='Original-government-import-v1; exact original source, native terrain correction, unchanged source heights, all-vertex/triangle-centre/low-edge contact, neighbour regression and runtime checks. No architectural reconstruction.')
    src=LOCAL/'candidates'/entry['asset'];assert digest(src.read_bytes())==entry['sha256'];dst=STAGE/entry['asset'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);cat['models'].append(entry)
cat['counts']['packedModels']=len(accepted);save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',{'models':len(accepted),'catalogues':['catalogue.json']})
forms=[]
for uid in accepted:
    b=dict(by_source[uid]['source']['building']);b['tile']=(ROOT/by_source[uid]['source']['tile']).stem;forms.append(b)
save(STAGE/'source-forms.json',forms)
plan={'areas':[{'area':cat['area'],'catalogue':str((STAGE/'catalogue.json').relative_to(ROOT)),'destination':'city/data/official-models/government-resolution-20260911/catalogue.json'}],'topLevelTerrainPatches':[]}
for patch in selected_patches:
    src=ROOT/patch['path'];dst=STAGE/'terrain'/src.name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
    plan['topLevelTerrainPatches'].append({'source':str(dst.relative_to(ROOT)),'sha256':digest(dst.read_bytes()),'destination':'city/data/'+src.name,'resolution':read(src)['cell'],'area':'Original government terrain · model integration'})
save(STAGE/'plan.json',plan)
config={'stage':str(STAGE.relative_to(ROOT))+'/','catalogueURL':plan['areas'][0]['destination'],'doc':str(DOC.relative_to(ROOT))+'/','terrain':plan['topLevelTerrainPatches']};save(STAGE/'browser-config.json',config)
proof={'policy':policy.POLICY,'policySHA256':digest((HERE/'acceptance-policy.py').read_bytes()),'selectedUids':sorted(accepted),'models':len(accepted),'patches':len(selected_patches),'catalogueSHA256':digest((STAGE/'catalogue.json').read_bytes()),'planSHA256':digest((STAGE/'plan.json').read_bytes()),'inputHashes':{**metrics['inputHashes'],**neighbours['sourceInputHashes']},'evidenceHashes':{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in [DOC/'staged-metrics.json',DOC/'staged-validation.json',DOC/'neighbour-checks.json',DOC/'source-resolution.json']},'aiCalls':0,'publication':False}
save(DOC/'decision.json',proof)
print({'selected':len(accepted),'terrainPatches':len(selected_patches),'modelBytes':sum(m['bytes'] for m in cat['models']),'terrainBytes':sum((ROOT/p['source']).stat().st_size for p in plan['topLevelTerrainPatches'])})

"""Disambiguate only a complete, exact Tower/Podium native candidate family.

This is metadata identity routing, not a geometry/placement/support exemption.
"""
from copy import deepcopy

REPLACE={'exact-current-object-csuid','fresh-current-exact-object-csuid','fresh-exact-component-route-not-unique-or-differs','unique-officialCandidates','unique-officialMatches','unique-viewerMatches'}
KINDS={'01':('Tower','T'),'02':('Podium','P')}


def qualify(raw,row,primary_records,current_forms):
    model=row['native']['model'];modelid=row['modelId'];uid=row['uid'];form=row['source']['building']
    assert len(modelid)==18 and modelid[0]=='B'and modelid[1:11].isdigit()and modelid[11:13]in KINDS
    kind,letter=KINDS[modelid[11:13]];geo=modelid[1:11]
    assert model['modelId']==modelid and model['asset']['sha256']==row['sourceSHA256']==raw['sourceSHA256']
    assert raw['originalOwnership']['sourceGraphVerified']and raw['originalOwnership']['originalRootName']==modelid
    assert form['uid']==uid==raw['uid']and form['structureType']==kind and form['buildingCSUID'][10]==letter and form['buildingCSUID'][:10]==geo
    forms=[f for f in current_forms if str(f.get('buildingCSUID',''))[:10]==geo]
    assert len(forms)==len({f['uid']for f in forms})==len({f['buildingCSUID']for f in forms})==2
    assert {f['structureType']for f in forms}=={'Tower','Podium'}and [f for f in forms if f['uid']==uid]==[form]
    records={p['BuildingCSUID']:p for p in primary_records if str(p.get('GeoRefNo'))==geo}
    assert set(records)=={f['buildingCSUID']for f in forms}
    by_csuid={f['buildingCSUID']:f for f in forms}
    for csuid,p in records.items():
        f=by_csuid[csuid]
        assert p['Status']=='Active'and p['BuildingBlockType']==f['structureType']and p['BuildingID']==f['buildingId']
        assert p['BaseHeight']==f['baseHeightHKPD']and p['TopHeight']==f['topHeightHKPD']
    matching=model['matching'];selected={}
    for key in ['officialCandidates','officialMatches','viewerMatches']:
        values=matching[key];assert values and len(values)==len({v['buildingCSUID']for v in values})
        assert all(v['buildingCSUID']in records and v['objectId']==by_csuid[v['buildingCSUID']]['objectId']for v in values)
        candidates=[v for v in values if by_csuid[v['buildingCSUID']]['structureType']==kind]
        assert len(candidates)==1 and candidates[0]['buildingCSUID']==form['buildingCSUID']and candidates[0]['objectId']==form['objectId']
        if key=='viewerMatches':assert candidates[0]['uid']==uid
        selected[key]=deepcopy(candidates[0])
    route=raw['exactCurrentComponentRoute'];assert route['qualified']and route['uid']==uid and route['source']['building']==form
    assert route['official']['buildingCSUID']==form['buildingCSUID']and route['official']['objectId']==form['objectId']
    reasons=[r for r in raw['reasons']if r not in REPLACE];replaced=sorted(set(raw['reasons'])&REPLACE)
    return dict(uid=uid,sourceSHA256=row['sourceSHA256'],typedRoutingQualified=True,modelId=modelid,kind=kind,exactBuildingCSUID=form['buildingCSUID'],exactObjectId=form['objectId'],selectedTypedMatches=selected,onlyTypedMetadataReasonsReplaced=replaced,rawReasonsRetained=deepcopy(raw['reasons']),reasons=reasons,passed=not reasons,identityAccepted=not reasons,spatialPhysicalOrCellExemption=False,installationApproved=False,sourceGeometryChanges=0,qualification='The official model subtype selects the sole active same-GeoRef Tower or Podium across all current records and each complete cached candidate/match list. Every candidate remains recorded; only these exact metadata ambiguity reasons are replaced. All coverage, extent, geographic-cell, unrelated-form, support, terrain and publication reasons remain unchanged.')

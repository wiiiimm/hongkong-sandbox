"""Bounded infrastructure/stilt evidence; no building or terrain changes."""
import collections,gzip,hashlib,json,pathlib,xml.etree.ElementTree as ET,zipfile
from shapely.geometry import Polygon
from shapely.ops import unary_union
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/tai-o-completion'

def main():
    selection=json.load(gzip.open(ROOT/'source-scripts/city/tai-o-models/building-selection.json.gz'))['buildings'];uids={b['uid'] for b in selection};buildings=[]
    for tid in sorted({b['tile'] for b in selection}):
        data=json.loads((ROOT/'3d-viewer/city/data/tiles'/(tid+'.json')).read_text());buildings.extend(b for b in data['buildings'] if b['uid'] in uids)
    assert len(buildings)==len(uids)==1030
    hydro_path=HERE/'hydro-tai-o.json';hydro=json.loads(hydro_path.read_text());water=unary_union([Polygon(p['rings'][0],p['rings'][1:]) for p in hydro['water']]);candidates=[]
    for b in buildings:
        shape=Polygon(b['rings'][0],b['rings'][1:]);area=shape.intersection(water).area
        if area<=1:continue
        model=b.get('modelGeometry');minimum=model['worldBounds'][0][1] if model else b['base']+(b.get('minimum') or 0)
        source_base=b.get('baseHeightHKPD');source_top=b.get('topHeightHKPD');foundation=b.get('foundationBase')
        rendered_min=min(minimum,foundation) if isinstance(foundation,(int,float)) else minimum
        candidates.append({'uid':b['uid'],'buildingCSUID':b['buildingCSUID'],'structureType':b['structureType'],'area':shape.area,'mappedWaterIntersectionArea':area,'mappedWaterFraction':area/shape.area,'baseHeightHKPD':source_base,'topHeightHKPD':source_top,'renderBase':b['base'],'renderHeight':b['height'],'heightSource':b['heightSource'],'sourceModelId':model.get('modelId') if model else None,'sourceGeometryMinimumHKPD':minimum if model else None,'sourceGeometryBelowRecordedBaseMetres':max(0,source_base-minimum) if model and source_base is not None else None,'renderedGeometryMinimumEstimateHKPD':rendered_min,'displayBedGapMetres':max(0,rendered_min-hydro['illustrativeBed']),'aboveReferenceWater0_3m':rendered_min>.3,'note':'Mapped-water overlap establishes waterfront context, not a surveyed stilt-house classification or private access. Model minimum is a whole-model diagnostic, not a per-pile measurement; any retained foundation is illustrative.'})
    archive=HERE/'hydro-sources/9-SW-23B.zip';entry='9-SW-23B/Layers/Buildings/Building.gml';canopies=[]
    with zipfile.ZipFile(archive) as z:
        raw=z.read(entry);root=ET.fromstring(raw)
        for member in root:
            if not member.tag.endswith('featureMember'):continue
            f=list(member)[0];attrs={e.tag.split('}')[-1]:e.text for e in list(f) if len(e)==0}
            if attrs.get('BUILDINGID') not in ['1109182593','1109176709']:continue
            uid='landsd/182398:0' if attrs['BUILDINGID']=='1109182593' else 'landsd/169618:0';b=next(b for b in buildings if b['uid']==uid)
            # These two checked source records each have one simple exterior ring.
            lists=[n for n in f.iter() if n.tag.endswith('posList')];assert len(lists)==1
            v=list(map(float,lists[0].text.split()));coords=[(v[i+1]-834500,816500-v[i]) for i in range(0,len(v),3)];p=Polygon(coords);target=Polygon(b['rings'][0]);ratio=p.intersection(target).area/min(p.area,target.area)
            assert ratio>.9999 and attrs['TYPEOFBUILDINGBLOCK']=='OS' and attrs['BUILDINGSTATUS']=='E' and attrs['BASELEVEL'] is None and attrs['ROOFLEVEL'] is None
            canopies.append({'uid':uid,'sourceEntry':entry,'sourceEntrySha256':hashlib.sha256(raw).hexdigest(),'attributes':attrs,'sourceRings':[coords],'matchedFootprintFraction':ratio,'policy':'Retain roof footprint and raw NULL elevations. Shared descriptor uses source-deck anchored 3 m illustrative clearance; no duplicate suppression or surveyed roof-height claim.'})
    assert len(canopies)==2
    stats={'selectedBuildings':len(buildings),'selectedSourceModels':sum(bool(b.get('modelGeometry')) for b in buildings),'structureTypes':dict(collections.Counter(b['structureType'] for b in buildings)),'waterOverlapCandidates':len(candidates),'waterOverlapStructureTypes':dict(collections.Counter(b['structureType'] for b in candidates)),'waterOverlapSourceModels':sum(bool(b['sourceModelId']) for b in candidates),'waterOverlapFullyCoveredOver99Percent':sum(b['mappedWaterFraction']>.99 for b in candidates),'candidateGeometryAboveReferenceWater0_3m':sum(b['aboveReferenceWater0_3m'] for b in candidates),'candidateGeometryAboveIllustrativeBed':sum(b['displayBedGapMetres']>.01 for b in candidates),'candidateModelsWithGeometryMoreThan0_25mBelowRecordedBase':sum(b['sourceGeometryBelowRecordedBaseMetres'] is not None and b['sourceGeometryBelowRecordedBaseMetres']>.25 for b in candidates),'surveyedHousePileLocationsEstablished':0,'newIllustrativeHouseSupportsAdded':0}
    out={'schemaVersion':1,'scope':'The retained 1,030-building central Tai O source selection; not all Tai O households.','counts':stats,'waterSource':{'path':str(hydro_path.relative_to(ROOT)),'sha256':hashlib.sha256(hydro_path.read_bytes()).hexdigest(),'illustrativeBedHKPD':hydro['illustrativeBed']},'canopies':canopies,'waterOverlappedBuildingCandidates':candidates,'conclusions':['Five original infrastructure meshes preserve their source supports, including the eastern bridge piers extending to −5.509 m HKPD.','No individual house pile coordinates or vertical dimensions have been verified. A positive display-bed gap flags missing rendered support/clearance; it does not prove the exact stilt construction or bathymetry.','Mapped-water overlap alone does not justify adding timber piles to every building, including canopies and possible overhangs. No such blanket geometry is added.','The reference 0.3 m water plane is a visual diagnostic only; actual city tide is controlled separately.','Source placement and channel opening improve the waterfront, but surveyed per-house pile geometry remains an explicit limitation.']}
    access=json.loads((HERE/'infrastructure-access.json').read_text())
    out['publicApproaches']=[{k:r[k] for k in ['id','name','kind','estimatedElevation','elevationBasis','width','widthBasis','deckPath','sourcePath','sourceNodes','anchors']} for r in access['records']]
    out['counts']['illustrativePublicApproaches']=len(access['records'])
    out['counts']['additionalSurveyedApproachGeometry']=0
    (DOC/'infrastructure-evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(stats,indent=2))
if __name__=='__main__':main()

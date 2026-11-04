"""Compare cached official metadata to a current target; never approve a model."""
import re


def compare_target(source,form,records):
    model=source['originalModelId'];reasons=[];kind=None;geo=None
    if re.fullmatch(r'B\d{10}(01|02)[A-Za-z0-9]{5}',model):
        geo=model[1:11];kind={'01':'Tower','02':'Podium'}[model[11:13]]
    else:reasons.append('unsupported-original-model-id-subtype')
    typed=[r for r in records if str(r.get('GeoRefNo'))==geo and r.get('BuildingBlockType')==kind]if kind else []
    if not form:reasons.append('current-viewer-target-missing')
    else:
        csuid=str(form.get('buildingCSUID',''))
        if form.get('uid')!=source['uid']:reasons.append('current-viewer-uid-differs')
        if geo is not None and csuid[:10]!=geo:reasons.append('current-target-georef-differs')
        if kind and (form.get('structureType')!=kind or len(csuid)<11 or csuid[10]!={'Tower':'T','Podium':'P'}[kind]):reasons.append('current-target-subtype-differs')
    if len(typed)!=1:reasons.append('typed-official-record-missing'if not typed else'typed-official-record-ambiguous')
    official=typed[0]if len(typed)==1 else None;differences={}
    if official and form:
        fields={'BuildingCSUID':'buildingCSUID','BuildingID':'buildingId','BuildingBlockType':'structureType','BaseHeight':'baseHeightHKPD','TopHeight':'topHeightHKPD'}
        for officialkey,viewerkey in fields.items():
            if officialkey not in official or viewerkey not in form:reasons.append('required-field-missing:'+officialkey)
            elif official[officialkey]!=form[viewerkey]:
                reasons.append('official-current-field-differs:'+officialkey);differences[officialkey]=dict(official=official[officialkey],viewer=form[viewerkey])
        if official.get('Status')!='Active':reasons.append('official-record-not-active')
    return dict(uid=source['uid'],originalModelId=model,sourceKey=source['sourceKey'],indexedSourceSHA256=source['indexedSourceSHA256'],sourceKind=kind,geoRefNo=geo,typedPrimaryMatches=len(typed),exactTargetMetadataQualified=not reasons,reasons=reasons,fieldDifferences=differences,officialFootprint=official,currentTarget=form,officialObjectIdChanged=bool(official and form and official.get('OBJECTID')!=form.get('objectId')),sourceIdentityAccepted=False,sourceGraphOrAssetBytesChecked=False,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,permanentRejection=False)

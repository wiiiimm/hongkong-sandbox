"""Compare original official model bounds and dated outline heights without moving either."""
import json,pathlib
HERE=pathlib.Path(__file__).resolve().parent
models=json.loads((HERE/'model-sample/model-geometries.json').read_text())['byBuildingUid'];rows=[]
for uid,model in models.items():
    match=model['officialMatches'][0];low,high=model['worldBounds'][0][1],model['worldBounds'][1][1]
    rows.append({'uid':uid,'modelId':model['modelId'],'modelBase':low,'modelTop':high,
        'outlineBase':match['sourceBaseHeight'],'outlineTop':match['sourceTopHeight'],
        'baseDifference':low-match['sourceBaseHeight'] if match['sourceBaseHeight'] is not None else None,
        'topDifference':high-match['sourceTopHeight'] if match['sourceTopHeight'] is not None else None})
result={'method':'Source model vertical bounds minus independently recorded 2D outline heights; neither source is moved. Different revisions and vertical definitions can differ. This is a discrepancy screen, not a decision that either source is wrong.',
    'models':len(rows),'baseDifferenceOver2m':sum(r['baseDifference'] is not None and abs(r['baseDifference'])>2 for r in rows),
    'topDifferenceOver2m':sum(r['topDifference'] is not None and abs(r['topDifference'])>2 for r in rows),
    'topDifferenceOver5m':sum(r['topDifference'] is not None and abs(r['topDifference'])>5 for r in rows),'records':rows}
(HERE/'model-outline-height-comparison.json').write_text(json.dumps(result,indent=2)+'\n')

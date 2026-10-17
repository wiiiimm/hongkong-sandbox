"""Join both source audits and split source-valid assets by current terrain flags."""
import collections,json,pathlib,hashlib
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/pui-o-detail-completion'
def main():
 audit=json.loads((DOC/'audit.json').read_text());individual=json.loads((DOC/'individual-audit.json').read_text());prepared=json.loads((DOC/'prepared.json').read_text());runtime=json.loads((DOC/'runtime-verification.json').read_text());cat=json.loads((HERE/'compact/catalogue.json').read_text());byuid={r['uid']:r for r in individual['ledger']};models={r['uid']:r for r in cat['models']};terrain={r['uid']:r for r in runtime['results']};ledger=[]
 for r in audit['ledger']:
  row={**r,'individualisedCandidates':byuid[r['uid']]['candidates']}
  if r['uid'] in models:row['status']='staged-model-current-terrain-conflict' if terrain[r['uid']]['roofBelowSomeCurrentTerrain'] else 'staged-model-awaiting-browser-review'
  elif r['candidates']:row['status']='existing-source-model-fails-unchanged-geometric-match'
  elif row['individualisedCandidates']:row['status']='individualised-candidate-needs-source-geometry-audit'
  else:row['status']='no-exact-reference-model-in-either-current-local-source'
  ledger.append(row)
 safe=[r for r in cat['models'] if not terrain[r['uid']]['roofBelowSomeCurrentTerrain']];safe_cat={**cat,'models':safe,'counts':{'catalogueModels':len(safe),'packedModels':len(safe),'packedTriangles':sum(r['triangles'] for r in safe),'compressedBytes':sum(r['bytes'] for r in safe),'glbBytes':sum(r['glbBytes'] for r in safe),'decodedGeometryBytes':sum(r['decodedGeometryBytes'] for r in safe)}}
 (HERE/'compact/catalogue-integration-candidate.json').write_text(json.dumps(safe_cat,separators=(',',':'))+'\n')
 report={'scope':audit['scope'],'selectedForms':919,'liveDetailed':681,'stagedIdentityVerified':len(models),'browserReviewCandidates':len(safe),'stagedTerrainConflicts':len(models)-len(safe),'potentialDetailedAfterAllFourReviewed':681+len(models),'potentialPercentageAfterAllFourReviewed':100*(681+len(models))/919,'statuses':dict(collections.Counter(r['status'] for r in ledger)),'ledger':ledger,'directoryTransferredBytes':audit['counts']['directoryTransferredBytes']+individual['counts']['directoryTransferredBytes'],'modelTransferredBytes':prepared['sourceTransferredBytes'],'compactBytes':prepared['counts']['compressedBytes'],'limits':['No shared/live data changed. No assertion of 100% attainable detailed source coverage.','Both complete current local sheet sets were inspected, including neighbouring source sheets. This does not prove a model cannot exist in a different dataset or be published later.','Footprints remain retained for every unavailable/conflicting record; no procedural roof counts as an official detailed model.']}
 (DOC/'completion.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='ledger'},indent=2))
if __name__=='__main__':main()

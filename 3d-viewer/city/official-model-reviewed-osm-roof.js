/** One reviewed unchanged original entrance-roof correspondence.
 * Source association: government-xl-peninsula-exact-source-association-review-v1-20261029.
 * Feature review: government-xl-peninsula-private-group-roof-review-v1-20261029.
 * This admits no other OSM source, geometry revision or roof form. Publication
 * still requires the separate current source/physical/lifecycle approval gates.
 */
const OWNER='landsd/270876:0',ROOF='way/709674357:0';
const SOURCE='3a40860e5302240d814f907d2f1edabc4b3c7becab1c90d37f406d2a4ce631f2';
const FORM_SHA='e5145c99ffb447b87fb0a0de40bcca50dd3b36cd84be401765cd2631c8d4f67e';
const POLICY='exact-original-peninsula-entrance-roof-v1';
const FORM={"base":5.0,"centre":[1244.1,-847.3],"height":3.2,"heightSource":"levels","id":"way/709674357","kind":"yes","levels":1.0,"material":"","minimum":0.0,"name":"","part":true,"rings":[[[1237.8,-850.1],[1238.3,-843.5],[1250.5,-844.4],[1249.9,-851.1],[1237.8,-850.1]]],"tile":"0_-1","uid":"way/709674357:0","zh":""};
function canonical(value){
 if(Array.isArray(value))return '['+value.map(canonical).join(',')+']';
 if(value&&typeof value==='object')return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+canonical(value[k])).join(',')+'}';
 return JSON.stringify(value);
}
export function reviewedOsmRoofSuppression(entry,uid){
 const review=entry?.reviewedOsmRoofReplacement;
 return uid===ROOF&&entry?.uid===OWNER&&entry.sha256===SOURCE&&entry.modelId==='B357421737102063C0'&&entry.buildingCSUID==='3574217371T20050430'&&(entry.verticalPlacementOffsetHKPD??0)===0&&
  !!review&&Object.keys(review).sort().join('|')==='policy|roofFormSHA256|sourceSHA256'&&review.policy===POLICY&&review.sourceSHA256===SOURCE&&review.roofFormSHA256===FORM_SHA;
}
export function validateReviewedOsmRoofDeclaration(entry){
 if(entry.reviewedOsmRoofReplacement===undefined)return;
 if(!reviewedOsmRoofSuppression(entry,ROOF)||!Array.isArray(entry.suppressesBuildingUids)||entry.suppressesBuildingUids.length!==1||entry.suppressesBuildingUids[0]!==ROOF)throw new Error('Invalid reviewed original OSM roof declaration '+entry.uid);
}
export function reviewedOsmRoofFormMatches(entry,building){
 if(!reviewedOsmRoofSuppression(entry,building?.uid))return false;
 // Runtime activity annotations may be additional fields. Every original
 // source field, including the complete rings, must still match exactly.
 return Object.keys(FORM).every(k=>canonical(building[k])===canonical(FORM[k]));
}

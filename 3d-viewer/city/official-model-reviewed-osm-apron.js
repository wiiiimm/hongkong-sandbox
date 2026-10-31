/** Exact original pier/apron display correspondence; not a generic OSM rule.
 * Decision: government-xl-disneyland-eastern75643-osm-apron-decision-v1-20261030.
 * No source/BASIC geometry is changed. Installation still requires current
 * physical, visual and lifecycle approval. Changed source/form data fails closed.
 */
const OWNER='landsd/75643:0',BASIC='way/334029318:0';
const SOURCE="4c8e577256875f9ecc67fe5728e262113d852748ac743798b804f9b090f0dbc2",FORM_SHA="d08fe7d950c6efa8ef8afc7d2251770f7d6a5508995004d77b2a25c0ed45cda1",REVIEW_SHA="d9c2a503febf90dee0d67a14ac19520965c5faf793cf417bd19209091f643c48";
const POLICY='exact-original-disneyland-pier-apron-v1';
const BOUNDS=[[-11757.5625,0.042799949645996094,-2224.8125],[-11738.625,10.90429973602295,-2162.9375]];
const FORM={"base":4.41,"centre":[-11752.1,-2174.1],"height":24,"heightSource":"estimated","id":"way/334029318","kind":"yes","levels":null,"material":"","minimum":0.0,"name":"","part":false,"rings":[[[-11756.0,-2177.0],[-11756.0,-2171.1],[-11748.2,-2171.1],[-11748.1,-2177.0],[-11756.0,-2177.0]]],"tile":"-6_-2","uid":"way/334029318:0","zh":""};
function canonical(value){
 if(Array.isArray(value))return '['+value.map(canonical).join(',')+']';
 if(value&&typeof value==='object')return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+canonical(value[k])).join(',')+'}';
 return JSON.stringify(value);
}
export function reviewedOsmApronSuppression(entry,uid){
 const review=entry?.reviewedOsmApronGraphic;
 return uid===BASIC&&entry?.uid===OWNER&&entry.sha256===SOURCE&&entry.objectId===75643&&entry.modelId==='B227511866801062G0'&&entry.buildingCSUID==='2275118668T20050725'&&
  entry.footprintScope==='reviewed-original-feature:'+OWNER&&entry.variantId==null&&(entry.verticalPlacementOffsetHKPD??0)===0&&entry.sourceWorldBounds===undefined&&entry.verticalPlacementBasis===undefined&&
  canonical(entry.worldBounds)===canonical(BOUNDS)&&!!review&&Object.keys(review).sort().join('|')==='basicFormSHA256|policy|reviewSHA256|sourceSHA256'&&
  review.policy===POLICY&&review.sourceSHA256===SOURCE&&review.basicFormSHA256===FORM_SHA&&review.reviewSHA256===REVIEW_SHA;
}
export function validateReviewedOsmApronDeclaration(entry){
 if(entry.reviewedOsmApronGraphic===undefined)return;
 if(!reviewedOsmApronSuppression(entry,BASIC)||!Array.isArray(entry.suppressesBuildingUids)||entry.suppressesBuildingUids.length!==1||entry.suppressesBuildingUids[0]!==BASIC)throw new Error('Invalid reviewed original OSM apron declaration '+entry.uid);
}
export function reviewedOsmApronFormMatches(entry,building){
 if(!reviewedOsmApronSuppression(entry,building?.uid))return false;
 // Source fields cannot be added or altered under an old review. Activity is
 // the only annotation added by CityStreaming.fetchTile, not source metadata.
 return Object.keys(building).every(k=>Object.hasOwn(FORM,k)||k==='activity')&&Object.keys(FORM).every(k=>canonical(building[k])===canonical(FORM[k]));
}

// Generated source-bound fallback correction; official footprints and government assets stay unchanged.
const villa = {"required":{"uid":"landsd/325786:0","buildingCSUID":"2162233384T20211022","base":6.014,"height":3.0,"minimum":0,"structureType":"Open-sided Structure","heightSource":"estimated","baseSource":"terrain-estimated","baseHeightHKPD":null,"topHeightHKPD":null,"rings":[[[-12869.62,-16876.55],[-12870.057,-16883.573],[-12872.492,-16883.203],[-12873.445,-16888.39],[-12856.295,-16889.713],[-12856.61,-16894.015],[-12883.44,-16891.47],[-12881.31,-16884.66],[-12887.48,-16877.36],[-12886.38,-16873.89],[-12869.62,-16876.55]]]},"footprints":[[[[-12869.62132046913,-16876.57122117779],[-12869.622857972749,-16876.549546407667],[-12869.62,-16876.55],[-12869.62132046913,-16876.57122117779]]],[[[-12870.057,-16883.573],[-12872.492,-16883.203],[-12873.445,-16888.39],[-12856.295,-16889.713],[-12856.61,-16894.015],[-12883.41268010117,-16891.47259147009],[-12881.306151254412,-16884.745601092356],[-12881.32850056486,-16884.719149693283],[-12881.31,-16884.66],[-12887.459907705346,-16877.383772082816],[-12886.379345668958,-16873.975107470695],[-12869.625230374158,-16876.634057019928],[-12870.057,-16883.573]]]],"sourceUID":"landsd/89917:0","sourceSHA256":"4407cbd52574f50e6b6bdddc6e581c96bbd0653426f89df0e490ae0b2096935d","precisionClearanceM":0.0021836601342771385,"provenance":"docs/astra-city/government-import/government-xl-villa-private-canopy-quantised-boundary-v2-20261015/proposal.json"};
const requiredKeys=Object.keys(villa.required);
export function proceduralFootprintCorrection(building){
 if(building.uid!==villa.required.uid||building.modelGeometry)return null;
 for(const key of requiredKeys){
  const actual=building[key]??null,expected=villa.required[key];
  if(key==='rings'?JSON.stringify(actual)!==JSON.stringify(expected):actual!==expected)return null;
 }
 return villa;
}

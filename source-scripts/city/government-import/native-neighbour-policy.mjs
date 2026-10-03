/** Conservative acceptance for an installed native neighbour under a new terrain patch. */
export function nativeNeighbourAccepted({newlyBuried,newlyUpward,terrainRelevant,supportFraction}){
 return newlyBuried===0&&newlyUpward===0&&(terrainRelevant||supportFraction>=.5);
}

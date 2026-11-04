/** Private catalogue envelope only; model/source entries are returned unchanged. */
export function makePrivateInterfaceCatalogue(sources,scenario){
 if(!['current-BASIC','original-Star'].includes(scenario))throw Error('Unknown private source scenario');
 if(sources.length!==2||sources[0].uid!=='landsd/165054:0'||sources[1].uid!=='landsd/57455:0')throw Error('Exact Museum/independent Star source pair required');
 const models=sources.filter(s=>scenario==='original-Star'||s.uid==='landsd/165054:0').map(s=>s.entry);
 return{schemaVersion:1,kind:'staged-official-model-catalogue',crs:'EPSG:2326',verticalDatum:'Hong Kong Principal Datum',rootTranslation:[-834500,0,816500],counts:{packedModels:models.length},coordinatePolicy:'Unchanged original source nodes and one city translation; PRIVATE unapproved source interface review',models};
}

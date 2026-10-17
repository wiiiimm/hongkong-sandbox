import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {read,routeContext} from '../../../source-scripts/city/tai-o-completion/route_context.mjs';
import {loadRouteSurfaces,makeRouteNavigation,replayRoute} from '../../../source-scripts/city/tai-o-completion/route_navigation.mjs';
import {InfrastructureSurfaces} from '../infrastructure-data.js';
const route=read('3d-viewer/city/data/tai-o-route.json'),context=routeContext(route),surfaces=await loadRouteSurfaces({sampler:context.sampler});

test('published Tai O route preserves mapped geometry and discloses its separate public-entry estimate',()=>{
 assert.deepEqual(route,read('docs/astra-city/tai-o-completion/route.json'));
 assert.equal(route.continuousWalkVerified,true);assert.equal(route.stops.length,6);assert.ok(route.lengthMetres>600);
 assert.deepEqual(route.centreline[0],[-30779,3820.8]);assert.equal(route.walkCentreline.length,route.walkSampleSources.length);
 assert.equal(createHash('sha256').update(JSON.stringify(route.walkCentreline)).digest('hex'),route.runtimeVerification.walkCentrelineSha256);
 assert.ok(route.publicConnectors[0].estimatedHorizontalAlignment);assert.match(route.publicConnectors[0].sourceDiscrepancy,/side railing/);
 for(let i=0;i<route.walkCentreline.length;i++){
  const source=route.walkSampleSources[i],line=source.connectorId?route.publicConnectors.find(c=>c.id===source.connectorId).centreline:route.centreline,edge=source.connectorId?source.connectorEdge:source.sourceEdge;
  const point=line[edge].map((v,j)=>v+(line[edge+1][j]-v)*source.fraction),actual=route.walkCentreline[i];
  assert.ok(Math.hypot(actual[0]-point[0],actual[1]-point[1])<=.750001,'each adjustment remains bounded relative to its disclosed source or connector');
 }
});

test('actual Navigation walks the whole public Tai O route in both directions without resets',{timeout:30000},()=>{
 for(const reverse of [false,true]){
  const result=replayRoute(makeRouteNavigation({...context,surfaces}),route.walkCentreline,{reverse});
  assert.equal(result.passed,true,JSON.stringify(result));assert.ok(result.distanceMetres>600);assert.equal(result.initialisations,1);assert.equal(result.positionResetsAlongRoute,0);assert.ok(result.maxFrameMovementMetres<.35);
 }
});

test('removing the public floor or raising the tide blocks the route rather than crossing water',{timeout:30000},()=>{
 const dry=makeRouteNavigation({...context,surfaces:new InfrastructureSurfaces()}),probe=route.walkCentreline.find(([x,z])=>context.sampler.mappedWater(x,z));
 assert.deepEqual(dry.groundHeights(...probe),[]);const missing=replayRoute(dry,route.walkCentreline);assert.equal(missing.passed,false);assert.equal(missing.reason,'blocked');
 const high=makeRouteNavigation({...context,surfaces,waterLevel:context.sampler.height(...route.walkCentreline[0])+.195}),result=replayRoute(high,route.walkCentreline);
 assert.equal(result.passed,false);assert.equal(result.reason,'blocked');assert.ok(result.distanceMetres<2);
});

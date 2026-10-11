import assert from 'node:assert/strict';
import test from 'node:test';
import {nativeNeighbourAccepted} from './native-neighbour-policy.mjs';

test('terrain-contacting native neighbour passes when the patch buries no new triangle',()=>{
 assert.equal(nativeNeighbourAccepted({newlyBuried:0,newlyUpward:0,terrainRelevant:true,supportFraction:0}),true);
});
test('elevated native neighbour requires at least half its low rim inside a same-parent source support',()=>{
 assert.equal(nativeNeighbourAccepted({newlyBuried:0,newlyUpward:0,terrainRelevant:false,supportFraction:.5}),true);
 assert.equal(nativeNeighbourAccepted({newlyBuried:0,newlyUpward:0,terrainRelevant:false,supportFraction:.49}),false);
});
test('newly buried triangles always hold the terrain change',()=>{
 assert.equal(nativeNeighbourAccepted({newlyBuried:1,newlyUpward:0,terrainRelevant:true,supportFraction:1}),false);
 assert.equal(nativeNeighbourAccepted({newlyBuried:0,newlyUpward:1,terrainRelevant:true,supportFraction:1}),false);
});

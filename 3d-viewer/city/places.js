// Neighbourhood camera centres are approximate WGS84 public-place coordinates,
// projected through the importer's EPSG:2326 transform; buildings use OSM geometry.
export const REGIONS={island:{title:'Hong Kong Island',zh:'香港島'},kowloon:{title:'Kowloon',zh:'九龍'},lantau:{title:'Lantau',zh:'大嶼山'}};
const preset=(region,title,zh,x,z,{height=80,offset=[1500,1250,-1600],description='A different corner of Hong Kong.',spawn}={})=>({region,title,zh,target:[x,height,z],spawn:spawn||[x,z],offset,description});
export const PLACES={
 central:preset('island','Central','中環',0,420,{height:110,offset:[1900,1560,-2050],description:'Where the mountains meet the metropolis.',spawn:[0,575]}),
 wanchai:preset('island','Wan Chai','灣仔',1390,680,{height:90,offset:[1500,1150,-1500],description:'A thousand stories between the streets.',spawn:[1390,920]}),
 northpoint:preset('island','North Point','北角',4151,-399,{description:'Follow the shoreline further east.'}),
 chaiwan:preset('island','Chai Wan','柴灣',8068,2479,{description:'A city tucked beneath the eastern hills.'}),
 aberdeen:preset('island','Aberdeen','香港仔',-487,4252,{offset:[1400,1150,1500],description:'The other harbour, beyond the ridge.'}),
 stanley:preset('island','Stanley','赤柱',5390,7684,{offset:[1000,900,1200],description:'Village streets beside the southern sea.'}),
 kowloon:preset('kowloon','Kowloon waterfront','尖沙咀',750,-1020,{height:90,offset:[-1600,1300,2000],description:'Across the water, another world awaits.',spawn:[998,-853]}),
 mongkok:preset('kowloon','Mong Kok','旺角',957,-3511,{offset:[1700,1550,1650],description:'Street upon street, story upon story.'}),
 shamshuipo:preset('kowloon','Sham Shui Po','深水埗',236,-4718,{offset:[1500,1350,1800],description:'Old neighbourhoods and everyday discoveries.'}),
 kowloonbay:preset('kowloon','Kowloon Bay','九龍灣',4975,-3943,{offset:[-1600,1400,1800],description:'Industrial roots, a changing waterfront.'}),
 lantau:preset('lantau','Tung Chung','東涌',-22436,-197,{height:70,offset:[1700,1300,-1800],description:'A new town at the foot of Lantau’s mountains.'}),
 discoverybay:preset('lantau','Discovery Bay','愉景灣',-14706,-1183,{offset:[1400,1100,-1300],description:'A hillside neighbourhood opening onto the water.'}),
 muiwo:preset('lantau','Mui Wo','梅窩',-16462,2469,{height:40,offset:[1000,900,1100],description:'Silvermine Bay, villages and a slower pace.'}),
 taio:preset('lantau','Tai O','大澳',-30585,3554,{height:30,offset:[-950,850,900],description:'A fishing village between mountains and tidal creeks.'}),
 lantaupeaks:preset('lantau','Lantau mountains','大嶼山山巒',-22440,2273,{height:300,offset:[7400,5700,7200],description:'The high country between the settlements.'}),
};
export function closestPlace(x,z){return Object.entries(PLACES).filter(([id])=>id!=='lantaupeaks').sort((a,b)=>Math.hypot(a[1].target[0]-x,a[1].target[2]-z)-Math.hypot(b[1].target[0]-x,b[1].target[2]-z))[0][0];}

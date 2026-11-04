/** Read-only normal browser access; no imagery tile scraping or remote asset extraction. */
import {chromium} from '../../../../3d-viewer/city/node_modules/playwright/index.mjs';
import {readFile,writeFile} from 'node:fs/promises';
import path from 'node:path';import {fileURLToPath} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url));
const clusters=JSON.parse(await readFile(path.join(here,'official-comparison.json'))).clusters;
const targets=[{id:'waterfront',name:'Mui Wo waterfront',lat:22.266553,lon:113.999241},...['Wang Tong','Pak Ngan Heung','Tai Tei Tong Village','Luk Tei Tong'].map(name=>{const p=clusters.find(c=>c.name===name)||clusters.find(c=>c.name.startsWith(name));return {id:name.toLowerCase().replaceAll(' ','-'),name,lat:p.lat,lon:p.lon};})];
const selected=process.env.REF_ALL==='1'?targets:targets.slice(0,1),results=[];
const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--enable-webgl','--ignore-gpu-blocklist']});
try{
 for(const provider of (process.env.REF_PROVIDER?[process.env.REF_PROVIDER]:['google','open3dhk'])){
  const page=await browser.newPage({viewport:{width:1600,height:1000},deviceScaleFactor:1});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  for(const target of selected){
   const url=provider==='google'?`https://www.google.com/maps/@${target.lat},${target.lon},18z/data=!3m1!1e3`:`https://3d.map.gov.hk/mapviewer/app/map?flyto=${encodeURIComponent([target.lat,target.lon,650,0,90,0].join(','))}&l=en-US`;
   let navigationError=null;try{await page.goto(url,{waitUntil:'domcontentloaded',timeout:45000});await page.waitForTimeout(Number(process.env.REF_WAIT_MS||12000));}catch(e){navigationError=e.message;}
   const text=await page.locator('body').innerText().catch(()=>''),screenshot=`reference-${provider}-${target.id}-1600x1000.png`;
   await page.screenshot({path:path.join(here,screenshot),timeout:20000}).catch(()=>{});
   const result={provider,...target,requestedUrl:url,actualUrl:page.url(),title:await page.title().catch(()=>''),screenshot,navigationError,visibleText:text.slice(0,12000),pageErrors:[...errors]};results.push(result);console.log(JSON.stringify(result));
  }
  await page.close();
 }
 await writeFile(path.join(here,process.env.REF_ALL==='1'?(process.env.REF_PROVIDER?'online-reference-'+process.env.REF_PROVIDER+'.json':'online-reference-check.json'):process.env.REF_WAIT_MS?'online-reference-long-access.json':'online-reference-access.json'),JSON.stringify({checkedAt:new Date().toISOString(),method:'Normal headless Chrome navigation and viewport captures only. No downloaded imagery tiles, account access, or access-block workarounds.',results},null,2)+'\n');
}finally{await browser.close();}

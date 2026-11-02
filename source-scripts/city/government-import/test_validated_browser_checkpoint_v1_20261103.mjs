import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,writeFile,readFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
import {createCheckpoint} from './validated_browser_checkpoint_v1_20261103.mjs';
const hash=b=>createHash('sha256').update(b).digest('hex');
async function fixture(run){const root=await mkdtemp(join(tmpdir(),'xl-checkpoint-'));try{await writeFile(join(root,'input'),'original');await writeFile(join(root,'config'),'{}');const params={root,out:join(root,'out'),inputRefs:[{path:'input',sha256:hash('original')}],configPath:join(root,'config'),harnessPath:join(root,'config')};await run(params);}finally{await rm(root,{recursive:true,force:true});}}
const row=()=>({uid:'landsd/1:0',time:'15:00',file:'live-source.png',active:true,visible:true,fullyFramed:true,fallbackFaces:0,sourceSHA256:'a'.repeat(64),sourcePixelVisibility:{visiblePixels:64}});
test('complete-looking input remains partial; exact image/input bindings saved',()=>fixture(async p=>{const checkpoint=await createCheckpoint(p);await writeFile(join(p.out,'live-source.png'),'image');await checkpoint({passed:true,errors:[],views:[row()],retainedNativeOwnViews:[]});const result=JSON.parse(await readFile(join(p.out,'validated-browser-checkpoint.json')));assert.equal(result.softwareReportComplete,false);assert.equal(result.installationApproved,false);assert.equal(result.report.passed,undefined);assert.equal(result.images[0].sha256,hash('image'));}));
test('changed source input fails before checkpoint creation',()=>fixture(async p=>{await writeFile(join(p.root,'input'),'changed');await assert.rejects(createCheckpoint(p));}));
test('missing visibility, fallback faces and no target pixels fail',()=>fixture(async p=>{const checkpoint=await createCheckpoint(p);await writeFile(join(p.out,'live-source.png'),'image');for(const patch of [{visible:false},{fullyFramed:false},{fallbackFaces:1},{sourcePixelVisibility:{visiblePixels:0}}])await assert.rejects(checkpoint({errors:[],views:[{...row(),...patch}]}));}));
test('page errors and duplicate captures fail',()=>fixture(async p=>{const checkpoint=await createCheckpoint(p);await writeFile(join(p.out,'live-source.png'),'image');await assert.rejects(checkpoint({errors:['shader error'],views:[row()]}));await assert.rejects(checkpoint({errors:[],views:[row(),row()]}));}));
test('input/output and image traversal fail',()=>fixture(async p=>{await assert.rejects(createCheckpoint({...p,out:join(p.root,'../outside')}));const checkpoint=await createCheckpoint(p);await assert.rejects(checkpoint({errors:[],views:[{...row(),file:'../input'}]}));}));

import {readFileSync} from 'node:fs';import {gunzipSync} from 'node:zlib';import {verifySupportInterface} from './support-interface.mjs';
const x=JSON.parse(gunzipSync(readFileSync(process.argv[2])));console.log(JSON.stringify(verifySupportInterface(x.part,x.part.bottomHKPD,x.terrain)));

import fs from 'node:fs/promises';
import {FileBlob,PresentationFile} from 'file:///C:/Users/Z1234/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
const source='D:/Desktop/7215/project/deliverables/member04_baseline/member04_baseline_slides.pptx';
const p=await PresentationFile.importPptx(await FileBlob.load(source));
if(p.slides.items.length!==2)throw new Error('Expected exactly two slides');
for(let i=0;i<p.slides.items.length;i++){const png=await p.export({slide:p.slides.items[i],format:'png',scale:1});await fs.writeFile(`D:/Desktop/7215/project/diagnostics/presentation_build/final-v5/verified-slide-${i+1}.png`,new Uint8Array(await png.arrayBuffer()));}
console.log('Rendered both slides from the validated final PPTX');



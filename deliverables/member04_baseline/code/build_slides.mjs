import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from 'file:///C:/Users/Z1234/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
import {applyPresentationChartFont,finalizePresentation} from 'file:///C:/Users/Z1234/.codex/plugins/cache/openai-primary-runtime/presentations/26.1030.10813/skills/presentations/container_tools/artifact_tool_utils.mjs';
const root='D:/Desktop/7215/project';
const skill='C:/Users/Z1234/.codex/plugins/cache/openai-primary-runtime/presentations/26.1030.10813/skills/presentations';
const build=path.join(root,'diagnostics/presentation_build');
const read=async p=>JSON.parse((await fs.readFile(p,'utf8')).replace(/^\uFEFF/,''));
const preview=process.argv.includes('--preview');
const status=await read(path.join(root,'baseline/current_training_status.json'));
const run=status.run_directory;
const metrics=preview?{overall:status.metrics,per_class:null}:await read(path.join(run,'independent_validation/validation_metrics.json'));
const verified=preview?null:await read(path.join(run,'training_verified.json'));
if(!preview && verified.csv_rows!==100)throw new Error('Full 100 epochs must be verified');
const output=preview?path.join(build,'preview'):path.join(build,'final-v5');await fs.mkdir(output,{recursive:true});
const presentation=Presentation.create({slideSize:{width:1280,height:720}});
presentation.theme.defaultFont='Arial';
const navy='#123044',teal='#007D84',gray='#475569';
function text(slide,value,x,y,w,h,size=28,bold=false,color=navy){const s=slide.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});s.text=value;s.text.style={typeface:'Arial',fontSize:size,bold,color};return s;}
async function photo(slide,p,x,y,w,h){const b=await fs.readFile(p);slide.images.add({blob:b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),contentType:'image/jpeg',alt:'FDM printing defect photograph from the current dataset',fit:'contain',position:{left:x,top:y,width:w,height:h}});}
const s1=presentation.slides.add();s1.background.fill='#FFFFFF';
text(s1,'Original YOLOv8n baseline',64,46,1140,68,46,true);
text(s1,'Five FDM defect classes with official COCO initialization',64,122,1140,48,28,false,gray);
text(s1,'Frozen dataset',64,210,530,46,30,true);
text(s1,'1371 train / 171 validation / 171 test',64,267,560,74,30,true,teal);
text(s1,'Revised JSON annotations\n48 conflicting or related images excluded',64,344,535,92,27,false,gray);
text(s1,'100 epochs, 640-pixel inputs, SGD\nBatch 16, AMP, seed 42, workers 0',64,461,540,92,27);
let imagePath,caption;
if(preview){const samples=await read(path.join(root,'reports/new_json_20261105/visual_review_samples.json'));const sample=samples.find(x=>x.split==='val');imagePath=path.join(root,'datasets/current/images/val',sample.stem+'.jpg');caption='Current validation photograph used for layout review';}
else{const a=await read(path.join(run,'validation_predictions/error_analysis.json'));const ex=a.examples.find(x=>x.kind==='class_representative'&&x.class_id===0);imagePath=path.join(run,'validation_predictions',ex.file);caption='Saved validation prediction, confidence threshold 0.25';}
await photo(s1,imagePath,660,208,552,368);
text(s1,caption,660,587,552,66,22,false,gray);
text(s1,preview?`Layout preview during epoch ${status.completed_epochs}`:`Completed 100 epochs in ${(verified.training_seconds/60).toFixed(1)} minutes on RTX 3080 Laptop GPU`,64,657,1152,40,21,false,gray);
s1.speakerNotes.text=`Member 04, Tianyao Zhang. Data and settings sources: ${run}/protocol.json and ${root}/reports/new_json_20261105/current_data_audit.json. Every original JSON is preserved. The frozen test set is withheld. This image is a real dataset photograph, not a generated illustration. Framework sources: https://github.com/ultralytics/ultralytics/tree/v8.2.103 and https://docs.ultralytics.com/models/yolov8/. The original YOLOv8n architecture is unchanged except for its class output. Training wrappers, JSON conversion, audit and delivery used AI assistance. About 40 seconds: describe the revised JSON, fixed split and exact baseline configuration.`;
const s2=presentation.slides.add();s2.background.fill='#FFFFFF';
text(s2,preview?`Training snapshot after ${status.completed_epochs} epochs`:'Independent reload validation',64,46,1152,68,46,true);
const m=metrics.overall,pct=x=>(100*x).toFixed(2)+'%';
text(s2,`Precision ${pct(m['metrics/precision(B)'])}     Recall ${pct(m['metrics/recall(B)'])}`,64,127,1152,46,30,false,navy);
text(s2,`mAP50 ${pct(m['metrics/mAP50(B)'])}     mAP50–95 ${pct(m['metrics/mAP50-95(B)'])}`,64,174,1152,46,30,true,teal);
const categories=preview?['Precision','Recall','mAP50','mAP50–95']:metrics.per_class.map(r=>r.name.replaceAll('_',' '));
const series=preview?[{name:'Current validation',values:[m['metrics/precision(B)'],m['metrics/recall(B)'],m['metrics/mAP50(B)'],m['metrics/mAP50-95(B)']],fill:teal}]:[{name:'AP50',values:metrics.per_class.map(r=>Number(r.mAP50.toFixed(8))),fill:teal},{name:'AP50–95',values:metrics.per_class.map(r=>Number(r.mAP50_95.toFixed(8))),fill:'#45667E'}];
const chart=s2.charts.add('bar',{position:{left:64,top:235,width:1152,height:355},categories,series,barOptions:{direction:'bar',grouping:'clustered',gapWidth:65},hasLegend:!preview,legend:{position:'top',overlay:false,textStyle:{fontSize:23}},xAxis:{min:0,max:1,majorUnit:.25,numberFormatCode:'0%',textStyle:{fontSize:21,fill:gray},majorGridlines:{fill:'#E1E8ED',width:1,style:'solid'}},yAxis:{min:0,max:1,majorUnit:.25,numberFormatCode:'0%',textStyle:{fontSize:23,fill:navy},line:{fill:'none',width:0}},dataLabels:{showValue:true,position:'inEnd',numberFormatCode:'0.0%',textStyle:{fontSize:20,fill:'#FFFFFF',bold:true}},chartFill:'#FFFFFF',plotAreaFill:'#FFFFFF',chartLine:{fill:'none',width:0},plotAreaLine:{fill:'none',width:0}});
applyPresentationChartFont(chart,{fontFamily:'Arial'});
text(s2,'171 validation images. Off platform has 9 validation objects.',64,612,1152,34,23,false,gray);
text(s2,'Test remains withheld. Verified print-process IDs are still unavailable.',64,650,1152,40,23,false,gray);
s2.speakerNotes.text=`Source: ${run}/independent_validation/validation_metrics.json. The final slide uses a saved best.pt reloaded from disk on 171 validation images. Validation also selected the best checkpoint, so the numbers are not untouched test performance. P/R use the Ultralytics F1-curve operating point, while AP integrates confidence. Default AP collection conf=0.001, NMS IoU=0.7, imgsz=640, batch=16, device=0, FP32 validation. Per-class chart data use validation_metrics.json, rounded to eight decimal places for Excel workbook compatibility, and remain editable. The original JSON retains full precision. Off_platform has nine validation objects. Filename family grouping is inferred, and adjacent real-process frames can remain dependent. About 45 seconds: state the measured metrics, discuss the sparse class and withhold claims of independent-print generalization or unified FPS.`;
for(let i=0;i<presentation.slides.items.length;i++){const slide=presentation.slides.items[i];const png=await presentation.export({slide,format:'png',scale:1});await fs.writeFile(path.join(output,`slide-${i+1}.png`),new Uint8Array(await png.arrayBuffer()));const layout=await slide.export({format:'layout'});await fs.writeFile(path.join(output,`slide-${i+1}.layout.json`),await layout.text());}
const candidate=path.join(output,'candidate.pptx');await(await PresentationFile.exportPptx(presentation)).save(candidate);
if(!preview){const finalPath=path.join(build,'validated-output-v5/member04_baseline_slides.pptx');await fs.mkdir(path.dirname(finalPath),{recursive:true});const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath,pythonExecutable:'C:/Users/Z1234/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),explicitTotalSlideCount:2,requiredNativeChartOwnerSlides:[2],materializeLiteralChartWorkbooks:true,layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,receiptPath:path.join(build,'validation_receipt_v5.json')});await fs.copyFile(finalPath,path.join(root,'deliverables/member04_baseline/member04_baseline_slides.pptx'));console.log(JSON.stringify({finalPath,validation:'passed',slides:2}));}
else console.log(JSON.stringify({previewSlides:2,observedEpoch:status.completed_epochs,output}));






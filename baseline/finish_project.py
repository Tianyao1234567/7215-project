"""Final artifact integrity, archive creation, current documentation and size accounting."""
import new_json_common as c
import csv,json,os,shutil,zipfile
from pathlib import Path
from collections import Counter

def inventory():
    by=Counter();files=Counter();links=[]
    for parent,dirs,names in os.walk(c.ROOT,followlinks=False):
        for d in list(dirs):
            p=Path(parent)/d
            if p.is_symlink() or (p.stat().st_file_attributes&0x400):links.append(str(p));dirs.remove(d)
        for name in names:
            p=Path(parent)/name;rel=p.relative_to(c.ROOT);top=rel.parts[0] if len(rel.parts)>1 else '[root]'
            by[top]+=p.stat().st_size;files[top]+=1
    return {'logical_bytes':sum(by.values()),'bytes_by_top_directory':dict(by),'files_by_top_directory':dict(files),'reparse_paths_skipped':links,'disk_free_bytes':shutil.disk_usage(c.ROOT).free,'note':'Logical directory entries can count hardlinked bytes more than once; physical disk savings use the observed free-space delta in cleanup_record.json.'}

def main():
    pointer=c.current_model();run=Path(pointer['run_directory']);out=c.ROOT/'deliverables/member04_baseline'
    assert c.load(run/'post_training_verified.json')['status']=='passed'
    required=['README.md','best.pt','last.pt','config.yaml','config.json','requirements.txt','split_manifest.csv','validation_metrics.json','baseline_report.md','personal_contribution.md','presentation_notes.md','member04_baseline_slides.pptx','predictions/error_analysis.json']
    for name in required:assert (out/name).is_file(),name
    model=c.load(out/'model_handoff.json');assert model['epochs']==100 and not model['test_used']
    for name in ['best','last']:assert c.sha(out/(name+'.pt'))==model[name+'_sha256']
    c.assert_dataset()
    checked=c.load(c.REPORT/'verified_files.json')
    for record in checked:
        p=c.ROOT/record['image'];s=p.stat()
        if s.st_size!=record['bytes'] or s.st_mtime_ns!=record['image_mtime_ns']:assert c.sha(p)==record['image_sha256'],str(p)
    assert len(checked)==1761
    assert len(list((c.ROOT/'datasets/annotation_source/json').glob('*.json')))==1761
    assert len(list((c.ROOT/'datasets/quarantine/images').glob('*.jpg')))==48
    with (out/'results.csv').open(newline='') as f:rows=list(csv.DictReader(f))
    assert len(rows)==100
    with zipfile.ZipFile(out/'member04_baseline_slides.pptx') as ppt:
        assert len([n for n in ppt.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml')])==2
    shutil.copy2(c.ROOT/'run_project.py',out/'code/run_project.py')
    shutil.copy2(c.ROOT/'diagnostics/presentation_build/build_slides.mjs',out/'code/build_slides.mjs')
    c.save(out/'code/presentation_runtime.json',{'authoring_library':'@oai/artifact-tool','source':'Codex bundled runtime','recreation':'The PPTX itself is editable in PowerPoint. build_slides.mjs uses the bundled Codex runtime paths; adapt its root/runtime paths before regenerating outside this computer.'})
    metrics=c.load(out/'validation_metrics.json');v=metrics['overall'];cleanup=c.load(c.REPORT/'cleanup_record.json');train=c.load(run/'training_verified.json')
    manifest=[]
    for p in sorted(out.rglob('*')):
        if p.is_file() and p.name!='package_manifest.json':manifest.append({'path':p.relative_to(out).as_posix(),'bytes':p.stat().st_size,'sha256':c.sha(p)})
    c.save(out/'package_manifest.json',{'run_id':run.name,'created_China':c.now(),'files':manifest,'test_used':False})
    archive=c.ROOT/'deliverables/IDAT7215_Member04_Baseline_20261105.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(out.rglob('*')):
            if p.is_file():z.write(p,'member04_baseline/'+p.relative_to(out).as_posix())
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None;archive_entries=len(z.infolist())
    summary={'status':'complete','completed_China':c.now(),'run_id':run.name,'run_directory':str(run),'package':str(out),'archive':str(archive),'archive_bytes':archive.stat().st_size,'archive_sha256':c.sha(archive),'archive_entries':archive_entries,'epochs':100,'training_seconds':train['training_seconds'],'validation_metrics':metrics,'test_used':False,'split_counts':{'train':1371,'val':171,'test':171},'quarantined_images':48,'original_json':1761,'cleanup_observed_free_bytes_increase':cleanup['observed_free_bytes_increase'],'checks':['100 consecutive epochs verified','all numeric results finite','saved best reloaded for actual independent validation','171 validation predictions and error matching exported','five-class examples saved','package best/last hashes match run checkpoints','current labels and unchanged image identities verified','all JSON and quarantine retained','two editable slides checked and rendered','ZIP CRC passed'],'limits':['No verified print-process IDs','Only nine Off_platform validation objects','Annotation semantics checked by samples, not exhaustive manual review','Test withheld for member06','No unified deployment speed benchmark or measured GPU power']}
    c.save(c.REPORT/'FINAL_RESULT.json',summary)
    pct=lambda key:f'{100*v[key]:.2f}%'
    readme=f'''# IDAT7215 Topic 3 当前工程

工程根目录：{c.ROOT}。以下相对路径均从工程根目录起算。

已完成四号原始YOLOv8n基线。本次从官方COCO权重开始，完整训练100轮，耗时{train['training_seconds']/60:.2f}分钟，已重载best.pt进行validation验证和预测。

验证集171张：Precision {pct('metrics/precision(B)')}，Recall {pct('metrics/recall(B)')}，mAP50 {pct('metrics/mAP50(B)')}，mAP50–95 {pct('metrics/mAP50-95(B)')}。完整逐类结果见deliverables/member04_baseline/validation_metrics.json。test保持未使用。

## 交付入口

交付目录：deliverables/member04_baseline。总说明和六／七号可直接执行的命令：该目录README.md。完整小包：deliverables/IDAT7215_Member04_Baseline_20261105.zip。内含代码、配置、best/last权重、日志、训练曲线、验证图、五类预测与错误示例、方法和个人贡献草稿，以及两页可编辑PPT。多GB图片不重复装包。

当前run：baseline/runs/{run.name}。实时终端和training.log均保留，terminal_exit.json记录退出码，status.json和baseline/current_training_status.json记录完成状态。

## 唯一正式数据

数据入口datasets/current/data.yaml；1371 train / 171 val / 171 test，seed42。全部1761份原始JSON在datasets/annotation_source/json；48张争议和关联图片及对应JSON在datasets/quarantine。旧validation不用。当前YOLO标签由新版JSON生成，五类映射和冻结清单均已复核。

## 目录整理

原项目逻辑文件长度约31.71GB。清理10项旧副本／冗余ZIP后，可用磁盘空间实增{cleanup['observed_free_bytes_increase']/1e9:.2f}GB。详细删除和保留记录在reports/new_json_20261105/cleanup_record.json，最终目录占用在disk_after.json。参考模型、可用GPU环境、正式run、必要历史证据保留。C盘历史来源未修改。

## 运行

使用environment/.venv_gpu/Scripts/python.exe -B run_project.py status或verify-labels查看状态和复核JSON标签。train启动新的完整100轮实验；validate和predict默认加载当前正式best.pt。具体参数见交付README。baseline/start_training.ps1提供可见PowerShell入口。

## 解释边界与待补项

当前划分无完全相同解码图片或推断的原图／增强家族跨集合，但真实工件／打印过程ID未核实，相邻帧仍可能相关。只完成全量机器检查和10张画框抽查，不承诺所有语义标注绝对正确。Off_platform验证仅9个框。三号需确认16组标注分歧并提供过程分组ID，清单见交付member03_pending.md。

五号负责轻量检测头；六号负责统一评价／测速及冻结test评价；七号负责演示；八号负责统稿。已提供所需接口和材料，未替用户向成员发送消息。没有宣称同机测速、功耗测量或未经测试的部署导出。

reports/history与baseline/runs/history_35epochs_20261105为历史记录。本次没有恢复旧35轮，也没有把历史或smoke指标冒充正式结论。
'''
    (c.ROOT/'README.md').write_text(readme,encoding='utf-8')
    (c.ROOT/'PROGRESS_CURRENT.md').write_text(f'# 当前进度\n\n四号交接范围已完成。run_id：{run.name}。100轮训练、独立重载验证、validation预测、目录清理和交付材料均已完成。\n\n数据1371/171/171，48张隔离，1761份JSON保留，test未使用。交付入口：deliverables/member04_baseline/README.md。最终可核对记录：reports/new_json_20261105/FINAL_RESULT.json。\n\n待三号补充16组标注最终决定和真实打印过程ID；这些隔离项未参训。六号的统一测速、五号轻量模型和全组最终报告不由本次四号成果代替。\n',encoding='utf-8')
    (c.BASE/'README.md').write_text(readme,encoding='utf-8');(c.BASE/'PROGRESS.md').write_text(f'Current completed baseline: {run.name}\nSee {out}/README.md and {c.REPORT}/FINAL_RESULT.json.\n',encoding='utf-8')
    (c.ROOT/'datasets/README.md').write_text('Current dataset: current/data.yaml with frozen 1371/171/171 split. All 1761 original JSON are in annotation_source/json, and all 48 excluded images and JSON are in quarantine. Previous delivered validation and superseded dataset copies are not the current experiment input.\n',encoding='utf-8')
    (c.ROOT/'new/README.md').write_text('The four source ZIPs were removed only after verified current data, all original train JSON, quarantine and source/CRC inventories were retained. See reports/new_json_20261105/cleanup_record.json. Small received scripts/manifests here are historical delivery metadata, not current training entries.\n',encoding='utf-8')
    state=c.load(run/'status.json');state.update({'status':'complete','updated_China':c.now(),'completed_epochs':100,'package':str(out),'archive':str(archive),'validation_metrics':v,'test_used':False})
    c.save(run/'status.json',state);c.save(c.BASE/'current_training_status.json',state)
    original_source=c.INITIAL.with_suffix('.source.json')
    backup=c.ROOT/'reports/history/before_new_json_20261105/yolov8n.source.json'
    if original_source.exists() and not backup.exists():shutil.copy2(original_source,backup)
    c.save(original_source,{'source_url':'https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt','path':str(c.INITIAL),'bytes':c.INITIAL.stat().st_size,'sha256':c.INITIAL_SHA,'purpose':'Official COCO initialization; distinct from the trained current best/last weights.'})
    refs=c.ROOT/'sources/member_02/reference_models'
    c.save(c.ROOT/'sources/SOURCE_CATALOG_CURRENT.json',{'updated_China':c.now(),'current_data':str(c.DATA),'all_original_train_json':str(c.ROOT/'datasets/annotation_source/json'),'quarantine':str(c.ROOT/'datasets/quarantine'),'historical_catalog':'SOURCE_CATALOG.json is a preserved pre-cleanup inventory, not the current data entry.','reference_models':[{'path':str(p.relative_to(c.ROOT)),'bytes':p.stat().st_size} for p in refs.rglob('*') if p.is_file()],'course_documents':str(c.ROOT/'sources/shared/course'),'cleanup':str(c.REPORT/'cleanup_record.json')})
    disk=inventory();c.save(c.REPORT/'disk_after.json',disk)
    summary['final_project_logical_bytes']=disk['logical_bytes'];c.save(c.REPORT/'FINAL_RESULT.json',summary)
    print(json.dumps({k:summary[k] for k in ['status','run_id','archive','archive_bytes','archive_sha256','epochs','training_seconds','cleanup_observed_free_bytes_increase','final_project_logical_bytes']},ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':main()


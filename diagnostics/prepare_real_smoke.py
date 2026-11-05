"""Prepare a small real-image fixture solely to validate member 4's training."""
import json,random,shutil,sys
from pathlib import Path
from PIL import Image,ImageDraw
import yaml
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"baseline"))
from data_tools.dataset_audit import check_label_file,sha256,write_json
received=ROOT/"datasets/received_20261102/dataset"
original=yaml.safe_load((received/"data.yaml").read_text(encoding="utf-8-sig"))
names=original["names"]
full={"path":str(received),"train":"images/train","val":"images/val","nc":len(names),"names":names}
(ROOT/"baseline/configs/data.received_20261102.yaml").write_text(yaml.safe_dump(full,sort_keys=False),encoding="utf8")
out=ROOT/"datasets/real_smoke_20261102";out.mkdir(parents=True,exist_ok=False)
rng=random.Random(42);selected=[];seen_hashes=set()
for split,per_class in (("train",4),("val",2)):
    (out/"images"/split).mkdir(parents=True);(out/"labels"/split).mkdir(parents=True)
    for cls,name in enumerate(names):
        candidates=sorted((received/"images"/split).glob(name+"_*.jpg"))
        rng.shuffle(candidates);count=0
        for image in candidates:
            label=received/"labels"/split/(image.stem+".txt")
            boxes,errors=check_label_file(label,len(names))
            if errors or cls not in {b[0] for b in boxes}:continue
            digest=sha256(image)
            if digest in seen_hashes:continue
            with Image.open(image) as im:im.verify()
            shutil.copy2(image,out/"images"/split/image.name)
            shutil.copy2(label,out/"labels"/split/label.name)
            selected.append({"split":split,"image":str(image),"class_selection":name,"sha256":digest})
            seen_hashes.add(digest);count+=1
            if count==per_class:break
        if count<per_class:raise RuntimeError("Not enough valid examples for "+name)
data={"path":str(out),"train":"images/train","val":"images/val","names":names}
(out/"data.yaml").write_text(yaml.safe_dump(data,sort_keys=False),encoding="utf8")
write_json(out/"selection.json",{"purpose":"Real FDM smoke only; not the formal experimental split","original_splits_preserved":True,"selected":selected})
# Draw received ground-truth boxes for visual review, one validation image per class.
canvas=Image.new("RGB",(1280,5*390),"white");draw=ImageDraw.Draw(canvas)
palette=["red","lime","cyan","yellow","magenta"]
for row,name in enumerate(names):
    sample=next(r for r in selected if r["split"]=="val" and r["class_selection"]==name)
    image=Path(sample["image"]);label=received/"labels/val"/(image.stem+".txt")
    with Image.open(image) as original_image:
        pic=original_image.convert("RGB")
    width,height=pic.size
    pic.thumbnail((1250,340))
    small=ImageDraw.Draw(pic)
    boxes,_=check_label_file(label,len(names))
    for cls,x,y,w,h in boxes:
        bounds=((x-w/2)*pic.width,(y-h/2)*pic.height,(x+w/2)*pic.width,(y+h/2)*pic.height)
        small.rectangle(bounds,outline=palette[cls],width=3)
        small.text((bounds[0],max(0,bounds[1]-14)),names[cls],fill=palette[cls])
    canvas.paste(pic,(10,row*390+38))
    draw.text((10,row*390+8),name+" | "+image.name,fill="black")
canvas.save(ROOT/"diagnostics/received_ground_truth_contact_sheet.jpg",quality=90)
print(json.dumps({"root":str(out),"train_images":20,"val_images":10,"config":str(out/"data.yaml")},indent=2))

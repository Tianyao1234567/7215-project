"""Create synthetic rectangles solely for engineering tests; no FDM results."""
import argparse, random
from pathlib import Path
from PIL import Image, ImageDraw
import yaml

def create(root):
    root=Path(root).resolve()
    root.mkdir(parents=True,exist_ok=False)
    rng=random.Random(42)
    for split,count in (("train",4),("val",2),("test",2)):
        (root/"images"/split).mkdir(parents=True)
        (root/"labels"/split).mkdir(parents=True)
        for i in range(count):
            image=Image.new("RGB",(64,64),tuple(rng.randrange(20,80) for _ in range(3)))
            ImageDraw.Draw(image).rectangle((16,16,47,47),fill=tuple(rng.randrange(150,255) for _ in range(3)))
            image.save(root/"images"/split/f"synthetic_{i}.png")
            (root/"labels"/split/f"synthetic_{i}.txt").write_text("0 0.5 0.5 0.5 0.5\n",encoding="utf8")
    config={"path":".","train":"images/train","val":"images/val","test":"images/test","names":["synthetic_rectangle"]}
    (root/"data.yaml").write_text(yaml.safe_dump(config),encoding="utf8")
    (root/"SYNTHETIC_ONLY.txt").write_text("Engineering fixture. Not a 3D-printing dataset. Never report its metrics as project results.",encoding="utf8")
    return root/"data.yaml"

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--output",required=True)
    print(create(p.parse_args().output))

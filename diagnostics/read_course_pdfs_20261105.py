import os
from pathlib import Path
root=Path(r'D:\Desktop\7215\project')
os.environ['TEMP']=str(root/'.runtime/new_json_baseline/tmp');os.environ['TMP']=os.environ['TEMP']
import json,hashlib
from pypdf import PdfReader
courses=[]
for name in ['Group_Project_Guidelines.pdf','Topic3_Team_Handoff.pdf']:
    p=root/'sources/shared/course'/name
    courses.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'pages':[{'page':i+1,'text':page.extract_text()} for i,page in enumerate(PdfReader(p).pages)],'read_method':'Fresh extraction from current PDF using bundled runtime pypdf.'})
(root/'reports/new_json_20261105/course_requirements_verified.json').write_text(json.dumps(courses,ensure_ascii=False,indent=2),encoding='utf-8')
print('Fresh PDF extraction saved:',[(Path(r['path']).name,len(r['pages'])) for r in courses])

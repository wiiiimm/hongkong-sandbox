"""Contact sheets for actual captured browser evidence, with no screenshot edits."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw
p=argparse.ArgumentParser();p.add_argument('folder');a=p.parse_args();d=Path(a.folder);r=json.loads((d/'report.json').read_text())
for mobile in [False,True]:
 for time in [15,22]:
  views=[v for v in r['views'] if v['mobile']==mobile and v['time']==time]
  for start in range(0,len(views),8):
   subset=views[start:start+8];out=Image.new('RGB',(1400,420*((len(subset)+1)//2)),(20,24,28));draw=ImageDraw.Draw(out)
   for i,v in enumerate(subset):
    im=Image.open(d/v['file']);im.thumbnail((700,388));x=(i%2)*700;y=(i//2)*420;out.paste(im,(x,y));draw.text((x+5,y+392),v['id'],fill='white')
   out.save(d/f"{'mobile' if mobile else 'desktop'}-{time}-{start//8+1}-contact.jpg")

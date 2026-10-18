"""Render a reader-value map as PNG and editable SVG, with one shared scene.

Uses only Pillow from requirements-showcase.txt and the bundled Noto font.
This is an explanatory diagram of existing capabilities, not a product UI.
"""
from html import escape
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'examples/waypoint-opd/showcase'
FONT=ROOT/'assets/NotoSansCJKsc-Regular.otf'
INK,BLUE,MUTED,RULE,BG='#20282c','#3d6278','#606b70','#c6cdcf','#f6f5f1'


def scene(mobile=False):
    width,height=(780,1040) if mobile else (1440,860)
    ops=[]
    def line(points,color=RULE,weight=2):ops.append({'kind':'line','points':points,'fill':color,'width':weight})
    def text(x,y,value,size=24,color=INK,center=False):
        f=ImageFont.truetype(str(FONT),size)
        if center:x-=f.getlength(value)/2
        if x<10 or x+f.getlength(value)>width-10:raise ValueError('Diagram text outside canvas: '+value)
        ops.append({'kind':'text','x':x,'y':y,'value':value,'size':size,'fill':color})
    corners=[
        ('Reading Brief','阅读导览','先理清问题，再选阅读入口。',['问题 · 先修知识','路线 · 原文入口']),
        ('In-context Notes','原文旁注','把解释放在正在读的段落旁。',['术语 · 长句','公式 · 机制']),
        ('Evidence Trace','证据追溯','看清判断由什么支持、限于哪里。',['实测 · 推导','作者主张 · 导读解释']),
        ('Reproducible Output','可复现产物','留下能复查、保存和重建的阅读结果。',['JSON · 两种 PDF','Mobile HTML · SHA256']),
    ]
    if mobile:
        positions=[(38,58),(426,58),(38,712),(426,712)]
        lines=[[(330,300),(330,350),(355,375)],[(450,300),(450,350),(425,375)],
               [(330,702),(330,655),(355,630)],[(450,702),(450,655),(425,630)]]
        for points in lines:line(points)
        for index,((x,y),(en,cn,desc,keywords)) in enumerate(zip(positions,corners)):
            line([(x,y+29),(x,y+5),(x+28,y+5)],BLUE)
            text(x+13,y+15,en,19,BLUE)
            text(x+13,y+58,cn,32)
            short=['知道先读哪里','读原文，少些打断','回查依据与边界','保存、复查、重建'][index]
            text(x+13,y+115,short,26)
            for n,kw in enumerate(keywords):text(x+13,y+168+n*36,kw,23,MUTED)
        text(width/2,397,'Read the paper,',38,center=True)
        text(width/2,454,'not just the summary.',38,center=True)
        text(width/2,529,'摘要用于筛选，理解回到原文',26,BLUE,True)
        text(width/2,576,'帮助你亲自读进去',25,MUTED,True)
        line([(38,1002),(742,1002)])
        text(38,1013,'SOURCE ANNOTATIONS / 阅读价值框架',16,MUTED)
    else:
        positions=[(64,55),(824,55),(64,594),(824,594)]
        for points in [[(592,245),(640,290),(640,323)],[(848,245),(800,290),(800,323)],
                       [(592,590),(640,550),(640,520)],[(848,590),(800,550),(800,520)]]:line(points)
        for (x,y),(en,cn,desc,keywords) in zip(positions,corners):
            line([(x,y+42),(x,y+7),(x+34,y+7)],BLUE)
            text(x+18,y+13,en,22,BLUE)
            text(x+18,y+54,cn,34)
            text(x+18,y+111,desc,25)
            text(x+18,y+163,' · '.join(kw.replace(' · ',' / ') for kw in keywords),21,MUTED)
        text(width/2,332,'Read the paper,',44,center=True)
        text(width/2,397,'not just the summary.',44,center=True)
        text(width/2,473,'读摘要用于筛选，理解仍要回到原文',29,BLUE,True)
        line([(64,810),(1376,810)])
        text(64,827,'SOURCE ANNOTATIONS / 让理解辅助回到原文现场',18,MUTED)
    return width,height,ops


def render(name,mobile=False):
    w,h,ops=scene(mobile)
    im=Image.new('RGB',(w,h),BG);draw=ImageDraw.Draw(im)
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title">',
         '<title id="title">Source Annotations：围绕亲自阅读原论文的四项辅助</title>',f'<rect width="{w}" height="{h}" fill="{BG}"/>']
    for op in ops:
        if op['kind']=='line':
            draw.line(op['points'],fill=op['fill'],width=op['width'])
            points=' '.join(f'{x},{y}' for x,y in op['points'])
            svg.append(f'<polyline points="{points}" fill="none" stroke="{op["fill"]}" stroke-width="{op["width"]}"/>')
        else:
            f=ImageFont.truetype(str(FONT),op['size']);draw.text((op['x'],op['y']),op['value'],font=f,anchor='lt',fill=op['fill'])
            box=draw.textbbox((op['x'],op['y']),op['value'],font=f,anchor='lt')
            if box[3]>=h:raise ValueError('Diagram text exceeds bottom')
            # SVG baseline is derived from the same font, keeping editable text.
            asc,_=f.getmetrics();baseline=op['y']+asc-f.getbbox(op['value'])[1]
            svg.append(f'<text x="{op["x"]:.2f}" y="{baseline:.2f}" font-size="{op["size"]}" fill="{op["fill"]}" font-family="Noto Sans CJK SC, Microsoft YaHei, sans-serif">{escape(op["value"])}</text>')
    svg.append('</svg>');OUT.mkdir(parents=True,exist_ok=True)
    im.save(OUT/(name+'.png'),optimize=True)
    (OUT/(name+'.svg')).write_text('\n'.join(svg)+'\n',encoding='utf-8')
    return {'size':[w,h],'png_sha256':hashlib.sha256((OUT/(name+'.png')).read_bytes()).hexdigest()}


if __name__=='__main__':
    data={name:render(name,mobile) for name,mobile in [('framework-overview',False),('framework-mobile',True)]}
    (OUT/'framework-manifest.json').write_text(json.dumps({'type':'reader-value diagram; not a screenshot','source':'scripts/framework_overview.py',
        'font':'bundled Noto Sans CJK SC / SIL OFL 1.1','figures':data},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Generated desktop/mobile PNG + editable SVG from shared scene')

"""Self-contained page reader rendered directly from the final annotated PDF."""
import argparse
import base64
import hashlib
from html import escape as e
import json
from pathlib import Path
import pymupdf as fitz


def build_mobile(source,datafile,output,annotated=None):
    source,datafile,output=map(Path,(source,datafile,output))
    annotated=Path(annotated) if annotated else output.parent/'waypoint-opd-v1-annotated.pdf'
    data=json.loads(datafile.read_text(encoding='utf-8'))
    report=json.loads(annotated.with_suffix('.report.json').read_text(encoding='utf-8'))
    if hashlib.sha256(source.read_bytes()).hexdigest()!=data['paper']['sha256']:
        raise ValueError('Source SHA256 differs')
    if hashlib.sha256(datafile.read_bytes()).hexdigest()!=report['annotations_sha256']:
        raise ValueError('Regenerate the annotated PDF after changing annotation data')
    digest=hashlib.sha256(annotated.read_bytes()).hexdigest()
    if digest!=report['output_sha256']:
        raise ValueError('Annotated PDF differs from its report')
    doc=fitz.open(annotated)
    parts=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Waypoint-OPD · 原页阅读</title>',
    '<meta name="source-pdf-sha256" content="'+digest+'">', '''<style>
*{box-sizing:border-box}body{display:flex;flex-direction:column;height:100dvh;margin:0;background:#e6e8e8;color:#25343e;font:15px/1.5 "Noto Serif SC","Songti SC",serif}header{padding:10px 14px;background:#fff;border-bottom:1px solid #d1d6d8}header b{font-size:16px}nav{display:flex;gap:7px;align-items:center;margin-top:8px;flex-wrap:wrap}button,select{font:inherit;color:inherit;border:1px solid #ccd3d5;background:#fff;padding:5px 10px;border-radius:3px}button{cursor:pointer}a{color:#20526b}#viewport{flex:1;min-height:0;overflow:auto;padding:12px;--zoom:1;scroll-behavior:smooth}main{max-width:1100px;margin:auto}.sheet{position:relative;width:calc(100% * var(--zoom));margin:0 0 16px;background:white;box-shadow:0 1px 6px #0002}.sheet img{display:block;width:100%;height:auto}.sheet svg{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}.sheet svg a{pointer-events:all}.source-anchor{position:absolute;width:1px;height:1px;scroll-margin:90px 30px}.source-anchor:target{outline:2px solid #b58b28}small{color:#67747a}#zoom-label{min-width:40px;text-align:center}@media(max-width:500px){#viewport{padding:5px}header{padding:8px 10px}nav{gap:5px}button,select{padding:4px 7px}}
</style><body><header><b>Waypoint-OPD</b> <small>原页与批注一起读</small><nav><select id="pages" aria-label="跳转页面">''']
    by_output={p['output_page']:p['source_page'] for p in report['pages']}
    for i in range(len(doc)):
        label='阅读地图' if i+1 not in by_output else '原文第 '+str(by_output[i+1])+' 页'
        parts.append(f'<option value="page-{i+1}">{e(label)}</option>')
    parts.append('</select><button id="minus" aria-label="缩小">−</button><span id="zoom-label">100%</span><button id="plus" aria-label="放大">＋</button><button id="fit">适合屏宽</button><a href="'+e(annotated.name)+'">打开 PDF</a></nav></header><div id="viewport"><main>')
    jump_targets={}
    for n,page in enumerate(doc):
        for k,link in enumerate(page.get_links()):
            if link['kind']==fitz.LINK_GOTO:
                jump_targets.setdefault(link['page'],[]).append((f'jump-{n}-{k}',link['to']))
    for i,page in enumerate(doc):
        png=page.get_pixmap(matrix=fitz.Matrix(2.5,2.5),alpha=False).tobytes('png')
        label='阅读地图' if i+1 not in by_output else '原文第 '+str(by_output[i+1])+' 页'
        parts.append(f'<figure class="sheet" id="page-{i+1}" data-pdf-page="{i+1}" aria-label="{e(label)}"><img loading="lazy" decoding="async" width="{page.rect.width}" height="{page.rect.height}" alt="{e(label)}：与PDF相同的原文及批注" src="data:image/png;base64,{base64.b64encode(png).decode()}">')
        source_page=by_output.get(i+1)
        entries=[a for a in report['annotations'] if a['page']==source_page]
        for a in entries:
            r=fitz.Rect(a['source_boxes'][0])
            parts.append(f'<span class="source-anchor" id="source-{e(a["id"])}" style="left:{r.x0/page.rect.width*100}%;top:{r.y0/page.rect.height*100}%"></span>')
        for name,point in jump_targets.get(i,[]):
            parts.append(f'<span class="source-anchor" id="{name}" style="left:{point.x/page.rect.width*100}%;top:{point.y/page.rect.height*100}%"></span>')
        parts.append(f'<svg viewBox="0 0 {page.rect.width} {page.rect.height}" aria-label="页面链接">')
        for a in entries:
            r=fitz.Rect(a['note_box'])
            parts.append(f'<a href="#source-{e(a["id"])}" aria-label="原文第 {source_page} 页：定位对应原句"><rect x="{r.x0}" y="{r.y0}" width="{r.width}" height="{r.height}" fill="transparent"/></a>')
        for k,link in enumerate(page.get_links()):
            if link['kind']==fitz.LINK_URI:
                r=link['from'];parts.append(f'<a href="{e(link["uri"])}" aria-label="打开背景资料"><rect x="{r.x0}" y="{r.y0}" width="{r.width}" height="{r.height}" fill="transparent"/></a>')
            elif link['kind']==fitz.LINK_GOTO:
                r=link['from'];parts.append(f'<a href="#jump-{i}-{k}" aria-label="跳转原文第 {by_output.get(link["page"]+1,1)} 页具体位置"><rect x="{r.x0}" y="{r.y0}" width="{r.width}" height="{r.height}" fill="transparent"/></a>')
        parts.append('</svg></figure>')
    parts.append('''</main></div><script>
const viewport=document.getElementById('viewport');let zoom=1;
function setZoom(value){const old=zoom,x=viewport.scrollLeft+viewport.clientWidth/2,y=viewport.scrollTop+viewport.clientHeight/2;zoom=Math.max(1,Math.min(6,value));viewport.style.setProperty('--zoom',zoom);document.getElementById('zoom-label').textContent=Math.round(zoom*100)+'%';viewport.scrollLeft=x*zoom/old-viewport.clientWidth/2;viewport.scrollTop=y*zoom/old-viewport.clientHeight/2}
document.getElementById('plus').onclick=()=>setZoom(zoom+.5);
document.getElementById('minus').onclick=()=>setZoom(zoom-.5);
document.getElementById('fit').onclick=()=>setZoom(1);
document.getElementById('pages').onchange=e=>document.getElementById(e.target.value).scrollIntoView({block:'start'});
function followHash(){const target=document.getElementById(decodeURIComponent(location.hash.slice(1)));if(target)target.scrollIntoView({block:'center',inline:'center'})}
window.addEventListener('hashchange',followHash);window.addEventListener('load',followHash);
</script></body></html>''')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text('\n'.join(parts),encoding='utf-8')
    doc.close()
    return report['annotation_count']


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source');p.add_argument('annotations');p.add_argument('output');p.add_argument('--pdf')
    a=p.parse_args()
    print(f'Exported {build_mobile(a.source,a.annotations,a.output,a.pdf)} annotations in PDF page layout')

"""Compose README figures from pinned, existing PDF outputs. Never edits PDFs.

python scripts/showcase.py
Requires requirements.txt + requirements-showcase.txt. Crops stay in PDF
coordinates; English and Chinese inside the paper are never re-typeset.
"""
import hashlib
import io
import json
from pathlib import Path
import pymupdf as fitz
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'examples/waypoint-opd/showcase'
BG, INK, MUTED, RULE, BLUE = '#f4f3ef', '#20282c', '#606b70', '#cdd1d1', '#3d6278'
FONT = ROOT / 'assets/NotoSansCJKsc-Regular.otf'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font(size):
    return ImageFont.truetype(str(FONT), size)


def text(canvas, xy, value, size=24, fill=INK):
    draw = ImageDraw.Draw(canvas)
    for n, row in enumerate(value.split('\n')):
        point=(xy[0],xy[1]+n*(size+18))
        draw.text(point, row, font=font(size), fill=fill, anchor='lt')
        box = draw.textbbox(point, row, font=font(size), anchor='lt')
        if box[2] > canvas.width-16 or box[3] > canvas.height-8:
            raise ValueError('Showcase label overflow: '+value)


def line(canvas, xy, fill=RULE, width=1):
    ImageDraw.Draw(canvas).line(xy, fill=fill, width=width)


def crop(doc, page, rect, width, log, role):
    rect = fitz.Rect(rect)
    if not doc[page].rect.contains(rect):
        raise ValueError('Crop outside actual PDF page')
    png = doc[page].get_pixmap(matrix=fitz.Matrix(4,4), clip=rect, alpha=False).tobytes('png')
    im = Image.open(io.BytesIO(png)).convert('RGB')
    im = im.resize((width, round(im.height*width/im.width)), Image.Resampling.LANCZOS)
    log.append({'role':role, 'pdf_page':page+1, 'clip_pt':list(rect), 'display_width_px':width})
    return im


def paste(canvas, image, xy):
    if xy[0]+image.width>canvas.width or xy[1]+image.height>canvas.height:
        raise ValueError('Screenshot outside composition')
    canvas.paste(image, xy)
    ImageDraw.Draw(canvas).rectangle((xy[0],xy[1],xy[0]+image.width-1,xy[1]+image.height-1), outline=RULE)


def footer(canvas, label, y=None):
    y = canvas.height-58 if y is None else y
    line(canvas, (48,y-16,canvas.width-48,y-16))
    text(canvas,(48,y),label,19,MUTED)


def save(canvas, name, log, manifest):
    canvas.save(DEST/name, optimize=True)
    manifest['figures'][name]={'size':list(canvas.size),'crops':log,'sha256':digest(DEST/name)}


def main():
    datafile=ROOT/'examples/waypoint-opd/annotations.json'
    data=json.loads(datafile.read_text(encoding='utf-8'))
    source=ROOT/'local/waypoint-opd-v1.pdf'
    annotated=ROOT/'output/waypoint-opd-v1-annotated.pdf'
    report=json.loads(annotated.with_suffix('.report.json').read_text(encoding='utf-8'))
    if digest(source)!=data['paper']['sha256'] or digest(annotated)!=report['output_sha256']:
        raise ValueError('Stale or incorrect source/output; regenerate and verify first')
    if digest(datafile)!=report['annotations_sha256']:
        raise ValueError('Annotation data differs from the output report')
    DEST.mkdir(parents=True,exist_ok=True)
    manifest={'paper':data['paper']['url'],'paper_license':'CC BY 4.0',
              'source_sha256':digest(source),'annotated_sha256':digest(annotated),
              'meaning':'Static crops/compositions of actual PDFs, not UI screenshots or interaction recordings.',
              'coordinate_system':'PDF physical page is one-based; clip rectangles are PDF points.', 'figures':{}}
    original=fitz.open(source); doc=fitz.open(annotated)

    log=[]; im=Image.new('RGB',(1440,760),BG)
    text(im,(56,40),'SOURCE ANNOTATIONS',23,BLUE)
    text(im,(1030,43),'WAYPOINT-OPD / V1',19,MUTED)
    text(im,(56,96),'术语、长句、证据，都在原文旁',46)
    text(im,(56,164),'真实 PDF 局部 · 保留原段落、阅读顺序和对应位置',25,MUTED)
    line(im,(56,217,1384,217))
    shot=crop(doc,1,[0,322.4,612,487],1328,log,'Original source and its existing marginal notes in one spatial crop')
    paste(im,shot,(56,244))
    footer(im,'原论文第 1 页 / 中文解释与标记由本项目添加 · 点击图片查看大图')
    save(im,'hero.png',log,manifest)

    log=[]; im=Image.new('RGB',(780,1040),BG)
    text(im,(48,38),'SOURCE ANNOTATIONS',23,BLUE)
    text(im,(48,96),'原文旁的\nAI 学术精读助手',44)
    text(im,(48,238),'同一页的原句与旁注，分区放大',24,MUTED)
    text(im,(48,302),'原句 · 原论文第 1 页',22,BLUE)
    paste(im,crop(doc,1,[141,333.6,242,344.9],684,log,'Exact source term, magnified'),(48,347))
    text(im,(48,505),'同页旁注 · 完整术语与本文义',22,BLUE)
    paste(im,crop(doc,1,[6,410,96,485],490,log,'Existing a02 margin note, magnified'),(48,550))
    footer(im,'真实 PDF 裁图 / 辅助解释由 AI 生成，需审查',1000)
    save(im,'hero-mobile.png',log,manifest)

    log=[]; im=Image.new('RGB',(1440,680),BG)
    text(im,(48,36),'SEE THE DIFFERENCE',22,BLUE)
    text(im,(48,89),'同一篇论文，同一个位置',40)
    text(im,(48,166),'Original',25)
    text(im,(744,166),'With Source Annotations',25)
    rect=[105,126.5,278,138]
    paste(im,crop(original,2,rect,648,log,'Original same source rectangle'),(48,213))
    paste(im,crop(doc,3,rect,648,log,'Annotated identical source rectangle'),(744,213))
    text(im,(48,312),'阅读时的问题',22,BLUE)
    text(im,(48,362),'reverse-KL 在本文里是什么意思？\n这里的方向为什么重要？',27)
    text(im,(744,290),'同页旁注 / 分区放大',22,BLUE)
    paste(im,crop(doc,3,[6,126.5,96,204],300,log,'Existing a08 margin note, separately magnified'),(744,334))
    footer(im,'上方原句：同版本、同坐标、同缩放 · 右下：原有旁注放大 / 原文第 3 页')
    save(im,'before-after.png',log,manifest)

    # Use the actual PDF GoTo, not a manually invented source destination.
    link=[l for l in report['guide_links'] if l['label']=='第4页 · 正确性限制'][0]
    actual=[l for l in doc[0].get_links() if l['kind']==fitz.LINK_GOTO and l['page']+1==link['output_page']
            and abs(l['to'].y-link['point'][1])<.02][0]
    target_page=actual['page']
    annotation=next(a for a in report['annotations'] if a['id']=='a12')
    quote=fitz.Rect(annotation['source_boxes'][0])
    assert abs(quote.x0-actual['to'].x)<.02 and abs(quote.y0-actual['to'].y)<.02
    guide_clip=[105,520,375,572]
    manifest['navigation']={'label':link['label'],'from_pdf_page':1,'to_pdf_page':target_page+1,
                            'original_pdf_page':4,'point_pt':link['point'],'annotation':'a12'}
    log=[]; im=Image.new('RGB',(1440,880),BG)
    text(im,(48,38),'TRACE EVERY INSIGHT',22,BLUE)
    text(im,(48,90),'观点有入口，边界有原句',42)
    text(im,(48,171),'01  Reading Brief / 阅读导览中的真实入口',24,BLUE)
    paste(im,crop(doc,0,guide_clip,1050,log,'Actual brief fifth step and its GoTo link'),(48,218))
    text(im,(48,450),'↓  PDF 内部跳转 · 原论文第 4 页',24,BLUE)
    text(im,(48,516),'02  Source Evidence / 作者写下的限制',24,BLUE)
    paste(im,crop(doc,target_page,[144,595.8,427.5,608.2],930,log,'Actual highlighted source limitation'),(48,568))
    text(im,(1060,516),'同页旁注',24,BLUE)
    paste(im,crop(doc,target_page,annotation['note_box'],290,log,'Existing a12 note, no re-typesetting'),(1060,568))
    footer(im,'静态组合 · 目标由成品 GoTo 读取；不代表交互录屏或内容正确性保证')
    save(im,'evidence-navigation.png',log,manifest)

    log=[]; im=Image.new('RGB',(780,1130),BG)
    text(im,(48,38),'TRACE EVERY INSIGHT',23,BLUE)
    text(im,(48,95),'从观点，回到原句',38)
    text(im,(48,175),'01  阅读导览中的入口',24,BLUE)
    paste(im,crop(doc,0,guide_clip,684,log,'Actual reading route'),(48,224))
    text(im,(48,400),'↓  内部 GoTo · 原论文第 4 页',24,BLUE)
    paste(im,crop(doc,target_page,[144,595.8,427.5,608.2],684,log,'Actual highlighted evidence'),(48,451))
    text(im,(48,560),'02  同页旁注保留作者的限制',24,BLUE)
    paste(im,crop(doc,target_page,annotation['note_box'],450,log,'Existing limitation note'),(48,610))
    footer(im,'真实 PDF 裁图的静态组合 / 并非操作录屏',1090)
    save(im,'evidence-mobile.png',log,manifest)

    doc.close();original.close()
    (DEST/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Generated '+str(len(manifest['figures']))+' real-PDF showcase figures; PDFs unchanged.')


if __name__=='__main__':main()

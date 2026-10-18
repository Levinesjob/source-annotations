"""Create a small, attributed comparison and guide preview for the Transformer case.

Requires the locally generated PDFs described in examples/attention-is-all-you-need/README.md.
Does not copy full research pages into the public showcase.
"""
import json
from pathlib import Path
import pymupdf as fitz
from PIL import Image
import showcase as s

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'examples/attention-is-all-you-need/showcase'


def main():
    datafile=ROOT/'examples/attention-is-all-you-need/annotations.json'
    source=ROOT/'local/attention-is-all-you-need-v1.pdf'
    annotated=ROOT/'local/attention-preview/attention-is-all-you-need-v1-annotated.pdf'
    report=json.loads(annotated.with_suffix('.report.json').read_text(encoding='utf-8'))
    data=json.loads(datafile.read_text(encoding='utf-8'))
    if s.digest(source)!=data['paper']['sha256'] or s.digest(annotated)!=report['output_sha256'] or s.digest(datafile)!=report['annotations_sha256']:
        raise ValueError('Input version mismatch')
    DEST.mkdir(parents=True,exist_ok=True)
    s.DEST=DEST
    manifest={'paper':data['paper']['url'],'paper_license':data['paper']['license'],
              'source_sha256':s.digest(source),'annotated_sha256':s.digest(annotated),
              'meaning':'Attributed small source excerpts for comparison; not a full-paper redistribution license.',
              'figures':{}}
    with fitz.open(source) as original, fitz.open(annotated) as doc:
        doc[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(DEST/'preview-guide.png')
        a=next(a for a in report['annotations'] if a['id']=='t04')
        clip=fitz.Rect(a['source_boxes'][0])
        for box in a['source_boxes'][1:]:clip|=fitz.Rect(box)
        clip=clip+(-2,-1,2,1)
        im=Image.new('RGB',(1440,840),s.BG);log=[]
        s.text(im,(48,36),'READ IN CONTEXT',22,s.BLUE)
        s.text(im,(48,89),'训练更并行，为什么生成还要逐词进行？',37)
        s.text(im,(48,166),'Original / 原文第 2 页',25)
        s.text(im,(744,166),'With Source Annotations',25)
        s.paste(im,s.crop(original,1,clip,648,log,'Original exact source sentence'),(48,213))
        s.paste(im,s.crop(doc,2,clip,648,log,'Annotated identical source coordinates'),(744,213))
        s.text(im,(48,320),'auto-regressive 在这里是什么意思？',26,s.BLUE)
        s.text(im,(48,383),'不是把整篇论文换成中文，\n而是在卡住的原句旁接上解释。',27)
        s.text(im,(744,320),'同页译句 / 放大',24,s.BLUE)
        s.paste(im,s.crop(doc,2,a['note_box'],390,log,'Existing t04 marginal translation'),(744,367))
        s.footer(im,'Attention Is All You Need / arXiv:1706.03762v1 · 原句与旁注小范围节选')
        s.save(im,'before-after.png',log,manifest)
    (DEST/'comparison-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Generated guide preview and a small same-coordinate comparison; PDFs unchanged.')


if __name__=='__main__':main()

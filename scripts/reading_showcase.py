"""Static diagrams and short, attributed crops of the real Attention reading PDF.

Requires requirements-showcase.txt. No fake screenshots, animation or API calls.
"""
import hashlib,io,json
from pathlib import Path
import pymupdf as fitz
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'examples/attention-is-all-you-need/showcase'
FONT=ROOT/'assets/NotoSansCJKsc-Regular.otf';SERIF=ROOT/'assets/NotoSerifCJKsc-Regular.otf'
INK='#111c29';BLUE='#395b77';GRAY='#617080';RULE='#ccd2d8';BG='#faf9f5'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class Canvas:
    def __init__(self,w,h):self.im=Image.new('RGB',(w,h),BG);self.d=ImageDraw.Draw(self.im);self.log=[]
    def text(self,x,y,value,size=28,color=INK,serif=False):
        f=ImageFont.truetype(str(SERIF if serif else FONT),size)
        for i,row in enumerate(value.split('\n')):
            xy=(x,y+i*(size+14));box=self.d.textbbox(xy,row,font=f,anchor='lt')
            if box[0]<0 or box[2]>self.im.width-24 or box[3]>self.im.height-20:raise ValueError('Label overflow: '+row)
            self.d.text(xy,row,font=f,fill=color,anchor='lt')
    def line(self,y):self.d.line((48,y,self.im.width-48,y),fill=RULE,width=2)
    def crop(self,doc,page,rect,x,y,w,role):
        rect=fitz.Rect(rect)
        if not doc[page].rect.contains(rect):raise ValueError('Crop outside PDF')
        p=doc[page].get_pixmap(matrix=fitz.Matrix(4,4),clip=rect,alpha=False)
        im=Image.open(io.BytesIO(p.tobytes('png'))).convert('RGB');im=im.resize((w,round(im.height*w/im.width)),Image.Resampling.LANCZOS)
        if x+w>self.im.width or y+im.height>self.im.height:raise ValueError('Crop outside figure')
        self.im.paste(im,(x,y));self.log.append({'role':role,'pdf_page':page+1,'clip_pt':list(rect),'display_width_px':w})
    def save(self,name,m):
        self.im.save(OUT/name,optimize=True)
        m['figures'][name]={'size':list(self.im.size),'crops':self.log,'sha256':digest(OUT/name)}
def union(boxes):
    r=fitz.Rect(boxes[0])
    for b in boxes[1:]:r|=fitz.Rect(b)
    return r+(-2,-1,2,1)
def poster(doc,report,mobile,m):
    c=Canvas(880,1990) if mobile else Canvas(1600,1290)
    c.text(48,40,'Source Annotations',48 if mobile else 66,serif=True)
    c.text(48,118 if mobile else 140,'把阅读辅助，留在论文里',40 if mobile else 52,serif=True)
    c.text(48,182 if mobile else 216,'Read the paper, not just the summary.',25 if mobile else 30,BLUE,True)
    c.line(240 if mobile else 279)
    if mobile:
        c.text(48,275,'01 / 先有主线，再进入原文',31,BLUE)
        c.text(48,330,'任务 → 机制 → 证据 → 边界',28)
        c.text(48,385,'机器翻译：让每个词取用相关上下文',28)
        c.text(48,438,'阅读路线与前序资料，见一页导览。',24,GRAY)
        x,y,w=48,510,784
    else:
        c.text(48,320,'01 / 一页阅读导览',30,BLUE)
        c.crop(doc,0,doc[0].rect,48,379,430,'Actual project-authored reading brief')
        c.text(546,320,'02 / 读到机制，解释就在原句旁',30,BLUE)
        x,y,w=546,390,1006
    a=next(a for a in report['annotations'] if a['id']=='t35')
    c.text(x,y,'Attention 如何把上下文带进来？',28)
    c.crop(doc,a['output_page']-1,union(a['source_boxes']),x,y+60,w,'Exact highlighted weighted-sum definition, original page 3')
    c.text(x,y+186,'同页旁注 / 放大',24,BLUE)
    c.crop(doc,a['output_page']-1,a['note_box'],x,y+235,230,'Actual t35 marginal explanation, enlarged')
    c.text(x+(350 if mobile else 325),y+246,'Q / K：算匹配权重\nV：汇总的信息\n输出：带上下文的表示',24)
    c.text(x,y+635,'原文第 3 页 · §3.2 · 定义与解释分别保留',22,GRAY)
    start=1220 if mobile else 1090;c.line(start)
    features=[('01  阅读导览','问题与背景 → 阅读路线'),('02  原文旁注','术语 / 长句 / 公式 / 机制'),('03  证据追溯','入口 → 原句、图表或公式'),('04  可复现产物','JSON / PDF / HTML / SHA256')]
    for i,(title,desc) in enumerate(features):
        xx,yy=(48,start+36+i*135) if mobile else (48+(i%4)*390,start+28)
        c.text(xx,yy,title,28,INK,True);c.text(xx,yy+47,desc,21,GRAY)
    c.text(48,c.im.height-60,'Attention Is All You Need / arXiv:1706.03762v1 · 原文小范围节选',18,GRAY)
    c.save('reading-poster'+('-mobile' if mobile else '')+'.png',m)
def mechanism(mobile,m):
    c=Canvas(880,1610) if mobile else Canvas(1600,1070)
    c.text(48,40,'Attention 到底在算什么？',40 if mobile else 48,serif=True)
    c.text(48,112,'机器翻译中的信息流 / 导读示意，不是实验可视化',23,GRAY);c.line(166)
    stages=[('Q K^T / sqrt(d_k)','比对：当前查询与各个键','Q：要找什么\nK：供匹配的特征'),('softmax(分数)','归一化：每行权重和为 1','沿键的方向计算\n不把所有查询混在一起'),('权重 × V','汇总：加权求和，更新表示','V：取用的内容\n并非只挑得分最高的词')]
    for i,(formula,desc,note) in enumerate(stages):
        x,y=(48,210+i*190) if mobile else (48+i*515,210)
        c.text(x,y,f'{i+1:02}  '+formula,32 if mobile else 30,BLUE,True)
        c.text(x,y+63,desc,25 if mobile else 23);c.text(x,y+109,note.replace('\n','；') if mobile else note,21,GRAY)
        if i<2:c.text(x+(0 if mobile else 470),y+(153 if mobile else 28),'↓' if mobile else '→',25,BLUE)
    y=812 if mobile else 445;c.line(y);c.text(48,y+35,'同一个计算，在网络里有三种用法',30,INK,True)
    rows=[('编码器自注意力','Q / K / V 都来自输入侧','输入各位置相互取用上下文。'),('解码器遮罩自注意力','Q / K / V 来自输出侧','遮住未来词，只用已知输出。'),('编码器—解码器注意力','Q 来自解码器，K / V 来自编码器','生成译文时读取输入句子。')]
    for i,(name,origin,meaning) in enumerate(rows):
        yy=y+108+i*(137 if mobile else 112);c.text(48,yy,name,27,BLUE)
        if mobile:c.text(48,yy+44,origin,23);c.text(48,yy+82,meaning,22,GRAY)
        else:c.text(575,yy,origin,25);c.text(575,yy+43,meaning,23,GRAY)
    yy=y+(550 if mobile else 465);c.line(yy)
    c.text(48,yy+26,'多头 = 学习不同投影后分别计算，再拼接。',24)
    c.text(48,yy+70,'还需要前馈层、位置编码、残差与归一化。',24)
    c.text(48,c.im.height-55,'依据：原文第 2–5 页，§3.1–3.5；公式按固定 v1 核对。',19,GRAY)
    c.save('attention-explained'+('-mobile' if mobile else '')+'.png',m)
def evidence(doc,report,mobile,m):
    c=Canvas(880,1020) if mobile else Canvas(1600,750)
    c.text(48,40,'一句概括，怎样回到证据？',40 if mobile else 46,serif=True)
    link=next(l for l in report['guide_links'] if '表2翻译' in l['label'])
    actual=next(l for l in doc[0].get_links() if l['kind']==fitz.LINK_GOTO and l['page']+1==link['output_page'] and abs(l['to'].y-link['point'][1])<.02)
    c.text(48,125,'导览观点：v1 英德翻译达到 28.4 BLEU',29,BLUE)
    c.text(48,193,'↓  点击「原文第8页 · 表2翻译」',27)
    a=next(a for a in report['annotations'] if a['id']=='t23')
    if actual['page']+1!=a['output_page']:raise ValueError('Evidence destination differs')
    c.crop(doc,actual['page'],union(a['source_boxes']),48,260,784 if mobile else 1050,'Actual Table 2 selected result rows')
    y=480 if mobile else 465
    c.text(48,y,'【实测】这是什么设置下的结果？',27,BLUE)
    c.text(48,y+58,'WMT 2014 / newstest2014 / Transformer big',25)
    c.text(48,y+113,'英德 28.4；英法 41.0（v1）。',27)
    c.text(48,y+170,'英法超过此前单模型，不超过表中所有集成。',24)
    c.text(48,c.im.height-62,'静态路径图 · 真实 GoTo 已校验；请在本地生成的 PDF 中点击。',18,GRAY)
    c.save('evidence-trace'+('-mobile' if mobile else '')+'.png',m)
    m['navigation']={'label':link['label'],'output_page':actual['page']+1,'point':list(actual['to']),'annotation':'t23'}
def main():
    datafile=ROOT/'examples/attention-is-all-you-need/annotations.json';source=ROOT/'local/attention-is-all-you-need-v1.pdf'
    pdf=ROOT/'local/attention-preview/attention-is-all-you-need-v1-annotated.pdf'
    d=json.loads(datafile.read_text(encoding='utf-8'));r=json.loads(pdf.with_suffix('.report.json').read_text(encoding='utf-8'))
    for a in r['annotations']:
        a['output_page']=next(p['output_page'] for p in r['pages'] if p['source_page']==a['page'])
    if digest(source)!=d['paper']['sha256'] or digest(pdf)!=r['output_sha256'] or digest(datafile)!=r['annotations_sha256']:raise ValueError('Regenerate PDF: inputs differ')
    OUT.mkdir(parents=True,exist_ok=True)
    m={'paper':d['paper']['url'],'source_sha256':digest(source),'annotated_sha256':digest(pdf),'meaning':'Static diagrams and attributed short PDF excerpts; no full research pages or simulated interaction.','figures':{}}
    with fitz.open(pdf) as doc:
        doc[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(OUT/'preview-guide.png')
        for mobile in (False,True):poster(doc,r,mobile,m);mechanism(mobile,m);evidence(doc,r,mobile,m)
    (OUT/'static-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Generated 6 static figures + guide preview; source crops and GoTo recorded.')
if __name__=='__main__':main()

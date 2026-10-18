"""Real-paper layout/insertion regression; not a full-paper annotation review."""
import argparse,hashlib,json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import pymupdf as fitz
from prepend_guide import prepend

args=argparse.ArgumentParser(description=__doc__)
args.add_argument('--fetch',action='store_true',help='Download pinned official regression PDFs')
args=args.parse_args()
root=ROOT/'local/academic-regression';root.mkdir(parents=True,exist_ok=True)
sources={
 'resnet':('https://openaccess.thecvf.com/content_cvpr_2016/papers/He_Deep_Residual_Learning_CVPR_2016_paper.pdf','51b5de45eb0b558b19c3affe49503cff50cb170a32de602983d6e2ec286942a7'),
 'adam':('https://arxiv.org/pdf/1412.6980v9','eab9c73ae2ceda884b94830bda99312254bac4806f6c9f045cbab90721ecda31')}
for name,(url,digest) in sources.items():
    dest=root/(name+'.pdf')
    if not dest.exists() and args.fetch:
        with urllib.request.urlopen(url,timeout=60) as response:dest.write_bytes(response.read())
    if not dest.exists():raise SystemExit('Missing regression PDF; use --fetch: '+str(dest))
    if hashlib.sha256(dest.read_bytes()).hexdigest()!=digest:raise SystemExit('Regression PDF hash differs: '+name)
cases=[
('resnet','Deep Residual Learning for Image Recognition','Kaiming He, Xiangyu Zhang, Shaoqing Ren, Jian Sun','CVPR 2016 / official paper','https://openaccess.thecvf.com/content_cvpr_2016/papers/He_Deep_Residual_Learning_CVPR_2016_paper.pdf',
'把深网络的学习目标改为残差映射',
'更深的普通网络可能出现训练误差上升。作者让堆叠层学习相对输入的残差，并用快捷连接相加；实验比较了普通网络和残差网络，支持在所测图像识别设置中改善优化。',
['卷积网络：逐层提取图像特征。','残差与快捷连接：学习F(x)，再与输入x相加。'],
[('问题：普通网络加深后可能更难优化',1,'Deeper neural networks'),('方法：学习残差，再加回输入',2,'Residual learning: a building block.'),('机制：输入维度改变时需匹配快捷连接',3,'Residual Learning'),('证据：对照普通网络与残差网络',6,'Table 3.'),('边界：实验结果依赖网络和训练配置',5,'Implementation')]),
('adam','Adam: A Method for Stochastic Optimization','Diederik P. Kingma, Jimmy Ba','arXiv:1412.6980v9','https://arxiv.org/abs/1412.6980v9',
'用梯度矩估计自适应调整参数更新',
'随机梯度存在噪声，不同参数可能需要不同更新尺度。Adam利用一阶与二阶矩估计并修正初始化偏差；论文报告了多种任务的实验，但不支持任意非凸问题都必然收敛的推论。',
['随机梯度：用小批量样本近似目标函数梯度。','矩估计与指数移动平均：分别跟踪梯度均值和平方尺度。'],
[('问题：随机目标带来噪声梯度',1,'Abstract'),('方法：更新矩估计并进行参数更新',2,'Algorithm 1:'),('机制：修正从零初始化带来的偏差',3,'INITIALIZATION BIAS CORRECTION'),('证据：查看任务与基线的实测对照',5,'EXPERIMENTS'),('边界：理论分析有明确适用条件',4,'CONVERGENCE ANALYSIS')])]
results=[]
for name,title,authors,identifier,url,headline,core,prereqs,stages in cases:
    source=root/(name+'.pdf');doc=fitz.open(source);steps=[]
    for i,(heading,pn,query) in enumerate(stages):
        # Match actual source heading/caption, falling back transparently to page-level.
        hits=doc[pn-1].search_for(query)
        point=list(hits[0].tl) if hits else [0,0]
        label=f'第{pn}页 · '+('原文位置' if hits else '整页入口')
        steps.append({'title':heading,'read':heading.split('：',1)[1],'minutes':9,'pages':[pn],
                      'targets':[{'page':pn,'point':point,'label':label}],
                      'match':'exact native text' if hits else 'page-level fallback'})
    data={'paper':{'title':title,'authors':authors,'identifier':identifier,'url':url,'sha256':hashlib.sha256(source.read_bytes()).hexdigest()},
          'reading_guide':{'headline':headline,'target_minutes':45,'core_view':core,'prerequisites':prereqs,'steps':steps},'annotations':[]}
    datafile=root/(name+'.json');datafile.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    output=root/(name+'-guide.pdf');r=prepend(source,datafile,output)
    with fitz.open(output) as out:out[0].get_pixmap(matrix=fitz.Matrix(1.4,1.4)).save(root/(name+'-guide.png'))
    results.append({'case':name,'source_url':url,'source_sha256':data['paper']['sha256'],'style':r['profile'],
                    'checks':r['validation'],'navigation':[s['match'] for s in steps]})
way=prepend(ROOT/'local/attention-is-all-you-need-v1.pdf',ROOT/'examples/attention-is-all-you-need/annotations.json',root/'attention-guide.pdf')
results.append({'case':'attention','checks':way['validation'],'style':way['profile']})
(root/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps([{'case':r['case'],'pages':r['checks']['source_pages'],'columns':r['style']['columns']} for r in results]))

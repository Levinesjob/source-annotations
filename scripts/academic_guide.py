"""Analyze PDF typography; lay out and render a searchable academic reading brief.

Semantic content is supplied by the reader/agent. This module never summarizes
papers or changes annotations. Coordinates are PDF physical points.
"""
from collections import Counter
from pathlib import Path
import re
import unicodedata
import pymupdf as fitz

FONT=Path(__file__).resolve().parents[1]/'assets/NotoSerifCJKsc-Regular.otf'


def analyze_pdf(doc):
    if doc.is_encrypted:
        raise ValueError('Encrypted PDF requires an explicitly decrypted working copy')
    first=doc[0]
    if any(p.rotation or p.cropbox!=p.mediabox for p in doc):
        raise ValueError('Rotated or nontrivial cropped pages need a verified adapter')
    spans=[];lines=[]
    for p in list(doc)[1:5] or [first]:
        for block in p.get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                if abs(line['dir'][0]-1)>.01:continue
                lines.append(line)
                spans.extend(s for s in line['spans'] if s['text'].strip())
    sizes=Counter()
    for s in spans:
        if 7<=s['size']<=14:sizes[round(s['size'],1)]+=len(s['text'])
    body_size=sizes.most_common(1)[0][0] if sizes else 10
    body=[s for s in spans if abs(s['size']-body_size)<.4 and len(s['text'])>15
          and .05*first.rect.height<s['bbox'][1]<.94*first.rect.height]
    names=Counter(s['font'] for s in body)
    body_font=names.most_common(1)[0][0] if names else 'unavailable'
    width,height=first.rect.width,first.rect.height
    left=sum(1 for l in lines if l['bbox'][0]<width*.4 and l['bbox'][2]<width*.54 and len(''.join(s['text'] for s in l['spans']))>35)
    right=sum(1 for l in lines if l['bbox'][0]>width*.44 and len(''.join(s['text'] for s in l['spans']))>35)
    columns=2 if min(left,right)>15 else 1
    margin_left=min((s['bbox'][0] for s in body),default=width*.09)
    margin_right=width-max((s['bbox'][2] for s in body),default=width*.91)
    # Ignore marginal labels; use real outer text edges, not a column's gutter.
    ml=max(32,min(margin_left,width*.19));mr=max(32,min(margin_right,width*.19))
    observed_lines=[list(d['rect']) for d in first.get_drawings() if d['rect'].height<2 and d['rect'].width>width*.4]
    headings=sorted({round(s['size'],1) for s in spans if s['size']>body_size+.8},reverse=True)[:4]
    header_footer=[first.get_text(clip=fitz.Rect(0,0,width,height*.07)).strip(),
                   first.get_text(clip=fitz.Rect(0,height*.94,width,height)).strip()]
    serif=bool(re.search('times|nimbusrom|cmr|roman|serif|lmr',body_font,re.I))
    return {'theme':'academic-native','width':width,'height':height,
            'orientation':'landscape' if width>height else 'portrait',
            'margins':{'left':round(ml,2),'right':round(mr,2),'top':max(35,height*.065),'bottom':max(32,height*.05)},
            'body_font':body_font,'body_font_class':'serif' if serif else 'sans',
            'body_size':body_size,'columns':columns,'heading_sizes':headings,
            'header_footer_samples':header_footer,'horizontal_rules':observed_lines,
            'analysis':'heuristic from native text spans; inspect rendered guide'}


def compile_content(data):
    paper=data.get('paper',{});guide=data['reading_guide']
    if sum(x['minutes'] for x in guide['steps'])!=guide['target_minutes']:
        raise ValueError('Reading route time allocations do not add up')
    if len(guide['steps'])>5:raise ValueError('Academic brief supports at most five focused points')
    title=guide.get('headline','论文阅读导览').replace('\n','')
    url=paper.get('url','')
    identifier=paper.get('identifier') or (re.search(r'(?:abs|pdf)/([^/#?]+)',url).group(1) if re.search(r'(?:abs|pdf)/([^/#?]+)',url) else '/')
    return {'title':title,'english_title':paper.get('title','/'),'authors':paper.get('authors','/'),
            'identifier':identifier,'url':url,'minutes':guide['target_minutes'],
            'core':guide.get('core_view') or guide.get('plain_method') or guide.get('goal','/'),
            'prerequisites':guide.get('prerequisites') or data.get('background',{}).get('paragraphs',[]),
            'references':data.get('background',{}).get('links',[]),
            'steps':guide['steps']}


def wrap(text,font,size,width):
    result=[];line=''
    for token in re.findall(r'[A-Za-z0-9_]+(?:[-./][A-Za-z0-9_]+)*|\n|[^\n]',text):
        if token=='\n':result.append(line);line='';continue
        if font.text_length(token,fontsize=size)>width:raise ValueError('English term exceeds guide line width')
        if font.text_length(line+token,fontsize=size)>width:result.append(line.rstrip());line=token.lstrip()
        else:line+=token
    if line:result.append(line)
    return result


def plan_brief(content,profile):
    font=fitz.Font(fontfile=str(FONT));english=fitz.Font('Times-Roman')
    for body_size in (10.5,10,9.5):
        ops=[];links=[];y=profile['margins']['top'];x=profile['margins']['left']
        right=profile['width']-profile['margins']['right'];width=right-x
        def text(value,size=body_size,indent=0,color=(0,0,0),face='cjk',gap=4):
            nonlocal y
            if face=='english' and any(not english.has_glyph(ord(c)) for c in value if not c.isspace()):face='cjk'
            f=font if face=='cjk' else english
            start=y
            for line in wrap(value,f,size,width-indent):
                ops.append({'op':'text','text':line,'x':x+indent,'y':y,'size':size,'face':face,'color':color})
                y+=size*1.28
            y+=gap
            return [x+indent,start,right,y-gap]
        def section(label):
            nonlocal y
            y+=6;text(label,11.5,gap=5)
        text('PAPER READING GUIDE / AI-ASSISTED',8,face='english',color=(.35,.35,.35),gap=9)
        text(content['title'],min(19,max(16,profile['width']/34)),gap=7)
        text(content['english_title'],10,face='english',gap=3)
        text(content['authors'],8.5,face='english',gap=3)
        box=text(f"论文标识：{content['identifier']}    建议阅读：{content['minutes']} 分钟",8.5,gap=8)
        if content['url']:links.append({'box':box,'uri':content['url']})
        ops.append({'op':'line','box':[x,y,right,y]});y+=3
        section('核心观点')
        text(content['core'])
        section('先修知识')
        for p in content['prerequisites']:text(p,9.5,gap=2)
        for link in content['references']:
            box=text(link.get('short_label',link['label']),8.5,color=(.19,.31,.42),gap=1)
            links.append({'box':box,'uri':link['url']})
        section('阅读路径与原文入口')
        for i,step in enumerate(content['steps'],1):
            title=step['title']
            if '：' in title:category,summary=title.split('：',1)
            else:category,summary=title,step['read']
            text(f"{i:02}  {category}  /  {step['minutes']} 分钟",10.5,gap=2)
            text(summary,body_size,indent=17,gap=2)
            # Details stay in the source; avoid repeating each point's explanation.
            targets=step.get('targets',[])
            if targets:
                start_y=y;cx=x+17
                for target in targets:
                    size=8.5;label=target['label']
                    if label.startswith('第'):label='PDF'+label
                    tw=font.text_length(label,fontsize=size)
                    if cx+tw>right:y+=size*1.28;cx=x+17
                    ops.append({'op':'text','text':label,'x':cx,'y':y,'size':size,'face':'cjk','color':(.19,.31,.42)})
                    links.append({'box':[cx,y,cx+tw,y+size*1.28],'target':target})
                    cx+=tw+16
                y+=8.5*1.28+5
            else:
                text(step.get('read',''),9.5,indent=17,gap=4)
        y+=5;ops.append({'op':'line','box':[x,y,right,y]});y+=7
        text('实测：实验直接支持；推导：公式或数学关系；作者主张：作者判断；导读解释：辅助说明。',8.5,color=(.35,.35,.35),gap=3)
        text('入口页码指原论文PDF页序；印刷页码以正文页脚为准。',8.5,color=(.35,.35,.35),gap=0)
        if y<=profile['height']-profile['margins']['bottom']:
            for op in ops:
                if op['op']=='text':
                    selected_font=font if op['face']=='cjk' else english
                    if any(not selected_font.has_glyph(ord(c)) for c in op['text'] if not c.isspace()):
                        raise ValueError('Guide font lacks a requested character')
            return {'ops':ops,'links':links,'bottom':y,'body_size':body_size,'profile':profile}
    raise ValueError(f'Academic brief overflows one page ({y:.1f}pt); shorten core/prerequisites or secondary text, not fonts')


def canonicalize_guide_cmap(page,fontxref):
    """Fix CJK compatibility mappings on a private guide font object only.

    Noto CJK shares glyph IDs between canonical and compatibility ideographs.
    MuPDF sometimes chooses the latter for extraction. Glyphs stay unchanged.
    """
    doc=page.parent;kind,value=doc.xref_get_key(fontxref,'ToUnicode')
    if kind!='xref':raise ValueError('Embedded CJK guide font has no ToUnicode map')
    cmapxref=int(value.split()[0]);cmap=doc.xref_stream(cmapxref).decode('ascii')
    def mapped(value):
        if len(value)<=6:
            code=int(value,16)
            if 0xd800<=code<=0xdfff:return value.lower()
            chars=chr(code)
        else:chars=bytes.fromhex(value).decode('utf-16-be')
        return ''.join('-' if ord(c) in (0x2010,0x2011) else ' ' if c=='\u00a0' else
                       unicodedata.normalize('NFKC',c) if 0xf900<=ord(c)<=0xfaff or 0x2f800<=ord(c)<=0x2fa1f else c
                       for c in chars).encode('utf-16-be').hex()
    def ranges(block):
        rows=[]
        for line in block.group(1).splitlines():
            m=re.fullmatch(r'\s*<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>\s*',line)
            if not m:
                if line.strip():raise ValueError('Unsupported guide CMap range syntax')
                continue
            start,end,base=(int(x,16) for x in m.groups());digits=len(m[3])
            values=[f'{base+i:0{digits}x}' for i in range(end-start+1)]
            normalized=[mapped(v) for v in values]
            if all(a.lower()==b.lower() for a,b in zip(values,normalized)):rows.append(line.strip())
            else:rows.extend(f'<{start+i:04x}> <{start+i:04x}> <{v}>' for i,v in enumerate(normalized))
        return '\n'.join(f'{len(rows[i:i+100])} beginbfrange\n'+'\n'.join(rows[i:i+100])+'\nendbfrange' for i in range(0,len(rows),100))
    cmap=re.sub(r'\d+\s+beginbfrange(.*?)endbfrange',ranges,cmap,flags=re.S)
    def chars(block):
        rows=[]
        for a,b in re.findall(r'<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>',block.group(1)):
            rows.append(f'<{a}> <{mapped(b)}>')
        return f'{len(rows)} beginbfchar\n'+'\n'.join(rows)+'\nendbfchar'
    cmap=re.sub(r'\d+\s+beginbfchar(.*?)endbfchar',chars,cmap,flags=re.S)
    private_map=doc.get_new_xref();doc.update_object(private_map,'<<>>');doc.update_stream(private_map,cmap.encode('ascii'))
    private_font=doc.get_new_xref();doc.update_object(private_font,doc.xref_object(fontxref))
    doc.xref_set_key(private_font,'ToUnicode',f'{private_map} 0 R')
    resources=int(doc.xref_get_key(page.xref,'Resources')[1].split()[0])
    obj,count=re.subn(r'/GuideCJK\s+\d+\s+0\s+R',f'/GuideCJK {private_font} 0 R',doc.xref_object(resources))
    if count!=1:raise ValueError('Expected one private guide CJK font resource')
    doc.update_object(resources,obj)


def render_brief(doc,plan,pno=-1):
    profile=plan['profile'];p=doc.new_page(pno=pno,width=profile['width'],height=profile['height'])
    cjk_xref=p.insert_font(fontname='GuideCJK',fontfile=str(FONT))
    p.insert_font(fontname='GuideEnglish',fontbuffer=fitz.Font('Times-Roman').buffer)
    fonts={'cjk':fitz.Font(fontfile=str(FONT)),'english':fitz.Font('Times-Roman')}
    for op in plan['ops']:
        if op['op']=='line':p.draw_line(op['box'][:2],op['box'][2:],color=(.45,.45,.45),width=.4);continue
        font=fonts[op['face']]
        p.insert_text((op['x'],op['y']+font.ascender*op['size']),op['text'],
                      fontname='GuideCJK' if op['face']=='cjk' else 'GuideEnglish',fontsize=op['size'],color=op['color'])
    for link in plan['links']:
        if 'uri' in link:p.insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(link['box']),'uri':link['uri']})
    canonicalize_guide_cmap(p,cjk_xref)
    return plan


def resolve_links(doc,plan,source_pages,annotations=None):
    by_id={a['id']:a for a in annotations or []};result=[]
    for item in plan['links']:
        target=item.get('target')
        if not target:continue
        if target.get('annotation'):
            a=by_id.get(target['annotation'])
            if not a:raise ValueError('Missing annotation for guide target: '+target['annotation'])
            pn=a['page'];point=fitz.Rect(a['source_boxes'][0]).tl
        else:
            pn=target['page'];point=fitz.Point(target.get('point',[0,0]))+fitz.Point(source_pages[pn].get('extension_each_side',0),0)
        info=source_pages[pn];dest_page=info['output_page']-1
        if not doc[dest_page].rect.contains(point):raise ValueError('Guide target point outside destination')
        doc[0].insert_link({'kind':fitz.LINK_GOTO,'from':fitz.Rect(item['box']),'page':dest_page,'to':point})
        result.append({'label':target['label'],'source_page':pn,'output_page':dest_page+1,'point':list(point)})
    return result


def structure_report(doc):
    cat=doc.pdf_catalog()
    return {'attachments':doc.embfile_count(),'forms':bool(doc.is_form_pdf),
            'tag_tree':doc.xref_get_key(cat,'StructTreeRoot')[0]!='null',
            'page_labels':doc.get_page_labels(),
            'limitations':['New guide page is not tagged for PDF/UA; existing tag tree is retained, not revalidated.',
                          'Digital signatures cannot remain valid after insertion; signed PDFs are refused.',
                          'XFA, portfolios and rich-media semantics are not certified; inspect such documents separately.']}

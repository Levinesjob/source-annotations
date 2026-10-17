"""Insert one academic guide without rebuilding the research pages."""
import argparse
import copy
import hashlib
import json
import uuid
import unicodedata
from pathlib import Path
import pymupdf as fitz
from academic_guide import analyze_pdf, compile_content, plan_brief, render_brief, resolve_links, structure_report


def verify_inserted(source,output,expected_links,plan=None):
    checks={'source_pages':0,'pixels':'passed','text':'passed','links':'passed','bookmarks':'passed'}
    with fitz.open(source) as before,fitz.open(output) as after:
        if len(after)!=len(before)+1:raise ValueError('Incorrect insertion page count')
        if after[0].rect!=before[0].rect:raise ValueError('Guide paper size differs')
        if before.metadata!=after.metadata:raise ValueError('Original metadata changed')
        if structure_report(before)['tag_tree']!=structure_report(after)['tag_tree']:
            raise ValueError('Existing structure tree lost')
        if before.embfile_names()!=after.embfile_names():raise ValueError('Embedded file list changed')
        for name in before.embfile_names():
            if before.embfile_get(name)!=after.embfile_get(name):raise ValueError('Embedded file changed')
        for i,p in enumerate(before):
            q=after[i+1]
            if p.get_text()!=q.get_text():raise ValueError('Research text changed')
            if p.get_pixmap(matrix=fitz.Matrix(1,1)).samples!=q.get_pixmap(matrix=fitz.Matrix(1,1)).samples:
                raise ValueError(f'Original page {i+1} pixels changed')
            old,new=p.get_links(),q.get_links()
            if len(old)!=len(new):raise ValueError('Original links lost')
            for a,b in zip(old,new):
                if a['kind']!=b['kind'] or a['from']!=b['from']:raise ValueError('Link geometry changed')
                if a['kind'] in (fitz.LINK_GOTO,fitz.LINK_NAMED) and a.get('page',-1)>=0:
                    if b['page']!=a['page']+1 or b.get('to')!=a.get('to'):raise ValueError('Original GoTo offset incorrect')
                elif any(a.get(k)!=b.get(k) for k in ('uri','file','page','to','nameddest')):
                    raise ValueError('Original external destination changed')
            aa=list(p.annots() or []);bb=list(q.annots() or [])
            if len(aa)!=len(bb):raise ValueError('Original annotations lost')
            for a,b in zip(aa,bb):
                if a.type!=b.type or a.rect!=b.rect or a.info!=b.info:raise ValueError('Original annotation changed')
            aw=list(p.widgets() or []);bw=list(q.widgets() or [])
            if [(w.field_name,w.field_value) for w in aw]!=[(w.field_name,w.field_value) for w in bw]:raise ValueError('Form data changed')
            checks['source_pages']+=1
        oldtoc=before.get_toc();newtoc=after.get_toc()
        expected=[[1,'阅读导览',1]]+[[r[0],r[1],r[2]+1 if r[2]>0 else r[2]] for r in oldtoc]
        if newtoc!=expected:raise ValueError('Bookmark offset incorrect')
        for old,new in zip(before.get_toc(False),after.get_toc(False)[1:]):
            if old[3].get('to') is not None:
                a,b=old[3]['to'],new[3].get('to')
                if b is None or abs(a.x-b.x)>.02 or abs(a.y-b.y)>.02:
                    raise ValueError('Original bookmark position changed')
        if before.get_page_labels():
            expected_labels=[{'startpage':0,'prefix':'Guide','firstpagenum':1}]+[dict(l,startpage=l['startpage']+1) for l in before.get_page_labels()]
            if after.get_page_labels()!=expected_labels:raise ValueError('Original page labels shifted incorrectly')
        actual=[l for l in after[0].get_links() if l['kind']==fitz.LINK_GOTO]
        if len(actual)!=len(expected_links):raise ValueError('Missing guide links')
        for a,b in zip(actual,expected_links):
            if a['page']+1!=b['output_page'] or abs(a['to'].x-b['point'][0])>.02 or abs(a['to'].y-b['point'][1])>.02:
                raise ValueError('Guide destination mismatch')
        for block in after[0].get_text('blocks'):
            if not after[0].rect.contains(fitz.Rect(block[:4])):raise ValueError('Guide text clipped')
        if '\ufffd' in after[0].get_text():raise ValueError('Guide replacement glyph')
        if plan:
            def norm(s):return ''.join(unicodedata.normalize('NFKC',s).replace('\u2010','-').replace('\u2011','-').split())
            visible=norm(after[0].get_text())
            for op in plan['ops']:
                if op['op']=='text' and norm(op['text']) not in visible:
                    raise ValueError('Guide text missing from searchable layer: '+op['text'])
        if any(not after.extract_font(f[0])[3] for f in after[0].get_fonts()):
            raise ValueError('Guide contains a nonembedded font')
        checks['searchable_guide']=bool(after[0].get_text().strip())
        checks['structure']=structure_report(after)
    return checks


def prepend(source,datafile,output):
    source,datafile,output=map(Path,(source,datafile,output))
    if output.resolve() in (source.resolve(),datafile.resolve()):raise ValueError('Never overwrite original inputs')
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    data=json.loads(datafile.read_text(encoding='utf-8'))
    if digest!=data['paper']['sha256']:raise ValueError('Pinned source SHA256 differs')
    doc=fitz.open(source)
    if doc.is_encrypted or doc.is_repaired:raise ValueError('Encrypted or repaired PDF needs manual inspection')
    if doc.get_sigflags()>0:raise ValueError('Signed PDFs cannot retain signature validity after insertion')
    profile=analyze_pdf(doc);content=compile_content(data);plan=plan_brief(content,profile)
    original_toc=copy.deepcopy(doc.get_toc(simple=False));structure=structure_report(doc)
    labels=doc.get_page_labels()
    # Resolve annotation quotations on the untouched source, before index insertion.
    from annotate import validate_data
    annotations=[]
    for a in validate_data(doc,data):
        annotations.append(dict(a,source_boxes=[list(r) for r in a['anchor']]))
    page_count=len(doc)
    render_brief(doc,plan,pno=0)
    pages={n:{'output_page':n+1,'extension_each_side':0} for n in range(1,page_count+1)}
    links=resolve_links(doc,plan,pages,annotations)
    toc=[[1,'阅读导览',1]]
    for item in original_toc:
        if item[2]>0:item[2]+=1
        detail=item[3]
        if detail.get('kind') in (fitz.LINK_GOTO,fitz.LINK_NAMED) and detail.get('page',-1)>=0:
            # PyMuPDF reads resolved named bookmarks as kind=4; set_toc cannot
            # serialize that form. Preserve the resolved destination as GoTo.
            detail['page']+=1
            detail['kind']=fitz.LINK_GOTO
            detail.pop('nameddest',None)
        detail.pop('xref',None)
        toc.append(item)
    doc.set_toc(toc)
    if labels:
        shifted=[dict(l,startpage=l['startpage']+1) for l in labels]
        doc.set_page_labels([{'startpage':0,'prefix':'Guide','style':'','firstpagenum':1}]+shifted)
    output.parent.mkdir(parents=True,exist_ok=True)
    temporary=output.with_name('.'+output.stem+'.'+uuid.uuid4().hex+'.checking.pdf')
    doc.save(temporary,garbage=3,deflate=True);doc.close()
    validation=verify_inserted(source,temporary,links,plan)
    result={'source_sha256':digest,'output_sha256':hashlib.sha256(temporary.read_bytes()).hexdigest(),
            'theme':'academic-native','profile':profile,'guide_body_size':plan['body_size'],
            'guide_links':links,'source_structure':structure,'page_offset':1,
            'validation':validation}
    if hashlib.sha256(source.read_bytes()).hexdigest()!=digest:raise ValueError('Original input changed')
    temporary.replace(output)
    output.with_suffix('.guide-report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source');p.add_argument('data');p.add_argument('output')
    a=p.parse_args()
    try:r=prepend(a.source,a.data,a.output)
    except (ValueError,KeyError,RuntimeError,OSError) as exc:p.exit(1,str(exc)+'\n')
    print(json.dumps({'research_pages_preserved':r['validation']['source_pages'],'theme':r['theme']},ensure_ascii=False))

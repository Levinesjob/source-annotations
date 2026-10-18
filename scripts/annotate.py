"""Locate quotations in native PDF characters and add readable marginal notes."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import unicodedata

import pymupdf as fitz
from academic_guide import analyze_pdf, compile_content, plan_brief, render_brief, resolve_links

ROOT = Path(__file__).resolve().parents[1]
FONT = ROOT / 'assets' / 'NotoSansCJKsc-Regular.otf'
KINDS = {'term', 'sentence', 'key', 'note', 'formula'}
EVIDENCE = {'实测','推导','主张','解读'}


def visible_label(item):
    if item['kind']=='term':
        return ''
    tag=item.get('tag',{'sentence':'译句','key':'要点','note':'说明','formula':'公式'}.get(item['kind'],'说明'))
    return f"【{item.get('evidence','解读')}·{tag}】"


def prepare_source(doc,data):
    """Remove only an explicitly requested vertical version stamp in memory."""
    expected=data.get('presentation',{}).get('omit_first_page_vertical_stamp')
    if not expected:
        return []
    page=doc[0]
    def horizontal_text(p):
        return ''.join(s['text'] for b in p.get_text('dict')['blocks']
                       for l in b.get('lines',[]) if abs(l['dir'][0]-1)<.01 for s in l['spans'])
    before=horizontal_text(page)
    found=[]
    for b in page.get_text('dict')['blocks']:
        for line in b.get('lines',[]):
            value=''.join(s['text'] for s in line['spans'])
            if abs(line['dir'][0])<.01 and normalized(value)==normalized(expected):
                found.append((fitz.Rect(line['bbox']),value))
    if len(found)!=1:
        raise ValueError('Requested vertical version stamp must match exactly once')
    rect,value=found[0]
    page.add_redact_annot(rect,fill=None)
    page.apply_redactions(images=0,graphics=0)
    if horizontal_text(page)!=before:
        raise ValueError('Version stamp removal changed horizontal source content')
    return [{'page':1,'text':value,'box':list(rect)}]


def check_coverage(data):
    by_id = {a['id']:a for a in data['annotations']}
    findings = data.get('core_findings', [])
    if findings and not 3 <= len(findings) <= 5:
        raise ValueError('Select 3–5 core findings')
    for finding in findings:
        a = by_id.get(finding['annotation'])
        if not a or a['kind'] != 'key' or not a.get('limitation'):
            raise ValueError('Core finding needs highlighted evidence and attached limits')
    coverage = data.get('coverage',{})
    for group in ('domains','main_visuals','appendix_visuals'):
        for name, ids in coverage.get(group,{}).items():
            if not ids or any(i not in by_id for i in ids):
                raise ValueError(f'Missing coverage: {name}')
    return coverage


def verify_visual_inventory(doc,data):
    coverage=data.get('coverage',{})
    if not coverage:
        return {}
    declared=coverage.get('main_visuals',{})
    by_id={a['id']:a for a in data['annotations']}
    found={}
    for p in doc:
        if p.number+1 > coverage.get('main_source_pages',len(doc)):
            break
        for kind,num in re.findall(r'\b(Figure|Table)\s+(\d+)\s*:',p.get_text()):
            name=('图' if kind=='Figure' else '表')+num
            ids=declared.get(name,[])
            if not any(by_id[i]['page']==p.number+1 for i in ids if i in by_id):
                raise ValueError(f'Main visual lacks a same-page annotation: {name}')
            found[name]=p.number+1
    if set(found)!=set(declared):
        raise ValueError('Declared main visuals differ from source caption inventory')
    return {'main_visuals_covered':len(found),'main_visuals_total':len(found),
            'inventory':found,'meaning':'caption inventory and same-page links only; human relevance review required'}


def normalized(text):
    text = unicodedata.normalize('NFKC', text).replace('\u2010', '-').replace('\u2011', '-')
    return ''.join(c for c in text
                   if not c.isspace() and c != '\u00ad')


def locate(page, quote, occurrence=None):
    """Map normalized characters back to original boxes; reject ambiguity."""
    chars, mapped = [], []
    for bi, block in enumerate(page.get_text('rawdict')['blocks']):
        for li, line in enumerate(block.get('lines', [])):
            if abs(line['dir'][0] - 1) > .01:
                continue
            for span in line['spans']:
                for ch in span['chars']:
                    for c in normalized(ch['c']):
                        chars.append(c)
                        mapped.append(((bi, li), fitz.Rect(ch['bbox'])))
    text, needle = ''.join(chars), normalized(quote)
    if not needle:
        raise ValueError('Empty quotation')
    hits, start = [], 0
    while (start := text.find(needle, start)) >= 0:
        hits.append(start)
        start += 1
    if not hits:
        raise ValueError(f'Quotation not found on page {page.number + 1}: {quote}')
    if occurrence is None and len(hits) != 1:
        raise ValueError(f'Ambiguous quotation ({len(hits)} occurrences): {quote}')
    index = 0 if occurrence is None else occurrence - 1
    if index < 0 or index >= len(hits):
        raise ValueError('Occurrence is one-based and must identify an existing match')
    start = hits[index]
    groups = {}
    for line, rect in mapped[start:start + len(needle)]:
        groups[line] = groups[line] | rect if line in groups else rect
    return list(groups.values())


def wrap(text, font, size, width):
    lines, current = [], ''
    tokens = re.findall(r'[A-Za-z0-9_]+(?:[-.][A-Za-z0-9_]+)*|\n|[^\n]',text)
    for c in tokens:
        if c == '\n':
            lines.append(current)
            current = ''
        elif font.text_length(c,fontsize=size) > width:
            raise ValueError('Margin too narrow for a complete word')
        elif font.text_length(current + c, fontsize=size) > width:
            if not current:
                raise ValueError('Margin too narrow for a character')
            lines.append(current)
            current = c
        else:
            current += c
    if current:
        lines.append(current)
    return lines


def plan_side(entries, x0, x1, height, font):
    for size in (9.5, 9):
        result = []
        fits = True
        for entry in sorted(entries, key=lambda a: a['anchor'][0].y0):
            try:
                lines = wrap(entry['display'], font, size, x1 - x0 - 8)
            except ValueError:
                fits = False
                break
            h = len(lines) * size * 1.38 + 12
            y = max(34, min(entry['anchor'][0].y0, height - h - 36))
            if result:
                y = max(y, result[-1]['box'].y1 + 14)
            result.append(dict(entry, box=fitz.Rect(x0, y, x1, y+h),
                               lines=lines, size=size))
        if not fits:
            continue
        if result and result[-1]['box'].y1 > height - 30:
            shift = result[-1]['box'].y1 - (height - 30)
            for item in result:
                item['box'] = item['box'] + (0, -shift, 0, -shift)
        if not result or result[0]['box'].y0 >= 30:
            return result
    return None


def validate_data(doc, data):
    check_coverage(data)
    items, seen = [], set()
    for a in data['annotations']:
        if a['id'] in seen:
            raise ValueError('Duplicate annotation id')
        seen.add(a['id'])
        if a['kind'] not in KINDS or a['side'] not in ('left', 'right'):
            raise ValueError('Unsupported annotation kind or side')
        if a.get('evidence','解读') not in EVIDENCE:
            raise ValueError('Unknown visible evidence category')
        if a['kind'] == 'formula' and any(not a.get(k) for k in ('symbols','design','example')):
            raise ValueError('Formula needs symbols, design and a sourced example')
        if not isinstance(a['page'], int) or not 1 <= a['page'] <= len(doc):
            raise ValueError('Invalid one-based page')
        if not isinstance(a['text'], str) or not a['text'].strip():
            raise ValueError('Missing note text')
        if a['kind'] == 'term' and not normalized(a['text']).startswith(normalized(a['quote'])):
            raise ValueError(f"Term {a['id']} must display the complete source phrase")
        page = doc[a['page']-1]
        if page.rotation or page.cropbox != page.mediabox:
            raise ValueError('Rotated/cropped PDF requires a separately verified adapter')
        boxes = locate(page, a['quote'], a.get('occurrence'))
        if any(not page.rect.contains(r) for r in boxes):
            raise ValueError('Source character outside page')
        items.append(dict(a, anchor=boxes))
    return items


def add_reading_guide(doc, data, font=None, profile=None):
    if profile is None:
        profile={'theme':'academic-native','width':612,'height':792,
                 'margins':{'left':54,'right':54,'top':42,'bottom':40}}
    plan=plan_brief(compile_content(data),profile)
    render_brief(doc,plan)
    return plan


def build(source, annotations, output, pages=None):
    source, annotations, output = map(Path, (source, annotations, output))
    if output.resolve() in (source.resolve(), annotations.resolve()):
        raise ValueError('Output must not replace source or annotation data')
    if not FONT.is_file():
        raise ValueError('Bundled Noto font is missing')
    data = json.loads(annotations.read_text(encoding='utf-8'))
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != data['paper']['sha256']:
        raise ValueError('Source SHA256 differs: verify the paper version')
    doc = fitz.open(source)
    if doc.is_encrypted:
        raise ValueError('Encrypted PDF is unsupported')
    for source_page in doc:
        if source_page.rotation or source_page.cropbox != source_page.mediabox:
            raise ValueError('Rotated/cropped PDF requires a separately verified adapter')
        if next(source_page.annots() or iter(()), None) is not None or source_page.first_widget:
            raise ValueError('Source contains annotations/form fields; preserve them with a separately verified workflow')
    guide_profile=analyze_pdf(doc)
    presentation_changes=prepare_source(doc,data)
    all_items = validate_data(doc, data)
    coverage_report=verify_visual_inventory(doc,data)
    # Internal IDs remain in reports; readers see stable evidence/content labels.
    ordered = sorted(all_items, key=lambda a: (a['page'], a['anchor'][0].y0,
                                              a['anchor'][0].x0, a['id']))
    for item in ordered:
        item['label'] = visible_label(item)
        item['display'] = item['label'] + item['text']
        if item['kind']=='formula':
            item['display'] += '\n符号：'+item['symbols']+'\n设计：'+item['design']+'\n例子：'+item['example']
        if item.get('limitation'):
            item['display'] += '\n限制：'+item['limitation']
    selected = list(range(1, len(doc)+1)) if pages is None else pages
    if not selected or len(selected) != len(set(selected)) or any(p < 1 or p > len(doc) for p in selected):
        raise ValueError('Invalid page selection')
    font = fitz.Font(fontfile=str(FONT))
    if any(not font.has_glyph(ord(c)) for a in ordered for c in a['display'] if not c.isspace()):
        raise ValueError('Note contains characters absent from the bundled font')
    dest, report = fitz.open(), {'source_sha256': digest, 'pages': [], 'annotations': [],
                               'checks': 'geometry and exact character mapping only; human review required'}
    report['annotations_sha256'] = hashlib.sha256(annotations.read_bytes()).hexdigest()
    report['guide_pages'] = 0
    report['coverage']=coverage_report
    report['presentation_changes']=presentation_changes
    if data.get('reading_guide') and pages is None:
        guide_plan=add_reading_guide(dest,data,font,guide_profile)
        report['guide_style']=guide_profile
        report['guide_body_size']=guide_plan['body_size']
        report['guide_pages'] = 1
    for pn in selected:
        original = doc[pn-1]
        w, h = original.rect.width, original.rect.height
        entries = [a for a in ordered if a['page'] == pn]
        # Keep the entire original page protected. Reuse margins only where
        # no source word/image/vector graphic intersects the proposed note.
        protected = [fitz.Rect(b[:4]) for b in original.get_text('blocks')]
        protected += [fitz.Rect(d['rect']) for d in original.get_drawings()]
        left, right = [a for a in entries if a['side'] == 'left'], [a for a in entries if a['side'] == 'right']
        plans = None
        # Try original white space before extending either edge.
        for extension in (0, 90, 126, 162, 216, 270, 324):
            if any(a['kind']=='formula' for a in entries) and extension<270 and pn not in data.get('presentation',{}).get('try_original_width_pages',[]):
                continue
            lx0, lx1 = (6, 96) if extension == 0 else (6, extension-6)
            rx0, rx1 = (w-96, w-6) if extension == 0 else (w+extension+6, w+extension*2-6)
            l = plan_side(left, lx0, lx1, h, font)
            r = plan_side(right, rx0, rx1, h, font)
            if l is None or r is None:
                continue
            candidates = l + r
            shifted_protected = [p + (extension, 0, extension, 0) for p in protected]
            if any(a['box'].intersects(p) for a in candidates for p in shifted_protected):
                continue
            plans = candidates
            break
        if plans is None:
            raise ValueError(f'Page {pn}: too many notes; shorten or remove notes')
        page = dest.new_page(width=w + extension*2, height=h)
        page.show_pdf_page(fitz.Rect(extension, 0, extension+w, h), doc, pn-1)
        page.insert_font(fontname='Noto', fontfile=str(FONT))
        for item in plans:
            boxes = [r + (extension, 0, extension, 0) for r in item['anchor']]
            if item['kind'] == 'key':
                highlight = page.add_highlight_annot(boxes)
                highlight.set_colors(stroke=(1, .85, .18))
                highlight.set_opacity(.30)
                highlight.set_info(title='source-annotations', content=item['text'])
                highlight.update()
            elif item['kind'] in ('sentence', 'term','formula'):
                underline = page.add_underline_annot(boxes)
                underline.set_colors(stroke=(.25, .4, .6))
                underline.update()
            box, size = item['box'], item['size']
            color = (.18, .23, .29) if item['kind'] in ('term', 'sentence') else (.30, .27, .20)
            for i, line in enumerate(item['lines']):
                baseline = box.y0 + 5 + font.ascender*size + i*size*1.38
                page.insert_text((box.x0+4, baseline), line, fontsize=size,
                                 fontname='Noto', color=color)
            # Number placed in the margin, never over the original text.
            anchor = boxes[0]
            edge = box.x1 if item['side'] == 'left' else box.x0
            # Stop outside source content, including vertical version labels.
            # This is an alignment cue, not a line crossing text to the quote.
            nearby = [p for p in shifted_protected if p.y0 <= anchor.y0+3 <= p.y1]
            if item['side'] == 'left':
                target_x = min([p.x0 for p in nearby] + [anchor.x0]) - 3
            else:
                target_x = max([p.x1 for p in nearby] + [anchor.x1]) + 3
            line_box = fitz.Rect(min(edge,target_x), min(box.y0+7,anchor.y0+3),
                                 max(edge,target_x), max(box.y0+7,anchor.y0+3))
            other_notes = [other['box'] for other in plans if other['id'] != item['id']]
            connector_drawn = not any(line_box.intersects(p) for p in shifted_protected + other_notes)
            if connector_drawn:
                page.draw_line((edge, box.y0+7), (target_x, anchor.y0+3),
                               color=(.7, .7, .7), width=.35)
            report['annotations'].append({'id':item['id'], 'page':pn, 'kind':item['kind'],
                'label':item['label'], 'font_size':size, 'note_box':list(box),
                'source_boxes':[list(b) for b in boxes], 'matched':True,
                'connector': 'drawn_to_outer_margin' if connector_drawn else 'omitted_to_protect_content'})
        footer = f"{data['paper']['url']} | {data['paper'].get('license', 'see source')} | notes added | source p.{pn}"
        page.insert_text((6, h-10), footer, fontsize=6, color=(.4,.4,.4))
        report['pages'].append({'source_page':pn, 'output_page':len(dest),
                                'extension_each_side':extension, 'notes':len(plans)})
    report['guide_links']=[]
    if report['guide_pages']:
        source_pages={p['source_page']:p for p in report['pages']}
        report['guide_links']=resolve_links(dest,guide_plan,source_pages,report['annotations'])
    toc = []
    if report['guide_pages']:
        toc.append([1,f"{data['reading_guide']['target_minutes']}分钟阅读路线（未实测）",1])
        source_to_output = {p['source_page']:p['output_page'] for p in report['pages']}
        for step in data['reading_guide']['steps']:
            target = step.get('pages',[])
            if target:
                toc.append([2,f"{step['title']}（{step['minutes']}分钟）",source_to_output[target[0]]])
    toc += [[1,f'原论文第{p["source_page"]}页',p['output_page']] for p in report['pages']]
    dest.set_toc(toc)
    dest.set_metadata({'title':data['paper']['title']+' | annotated reading copy',
                       'author':'Original paper: '+data['paper']['authors'],
                       'subject':data['paper'].get('license','see source')+' original; Chinese annotations added by source-annotations. '+data['paper']['url'],
                       'creator':'source-annotations 0.1.0-preview'})
    output.parent.mkdir(parents=True, exist_ok=True)
    # Retain the complete OTF: subsetting CFF fonts can corrupt outlines in
    # some MuPDF versions. Bigger files are preferable to missing characters.
    dest.save(output, garbage=4, deflate=True)
    dest.close()
    report['output_sha256'] = hashlib.sha256(output.read_bytes()).hexdigest()
    report['annotation_count'] = len(report['annotations'])
    output.with_suffix('.report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('annotations')
    parser.add_argument('output')
    parser.add_argument('--pages', help='One-based source pages, e.g. 1,4,7')
    args = parser.parse_args()
    try:
        report = build(args.source, args.annotations, args.output,
                       [int(p) for p in args.pages.split(',')] if args.pages else None)
    except (ValueError, KeyError, OSError, RuntimeError) as exc:
        parser.exit(1, f'FAILED: {exc}\n')
    print(f"Generated {len(report['pages'])} source pages + {report['guide_pages']} guide page(s), {report['annotation_count']} mapped annotations")


if __name__ == '__main__':
    main()

"""Verify output geometry and readable text; not a semantic/human review."""
import argparse
import hashlib
import json
from pathlib import Path
import pymupdf as fitz
from annotate import normalized, prepare_source

def verify(source, datafile, output):
    source, datafile, output = map(Path, (source,datafile,output))
    data = json.loads(datafile.read_text(encoding='utf-8'))
    report = json.loads(output.with_suffix('.report.json').read_text(encoding='utf-8'))
    assert report['source_sha256'] == hashlib.sha256(source.read_bytes()).hexdigest(), 'Source changed'
    assert report['output_sha256'] == hashlib.sha256(output.read_bytes()).hexdigest(), 'Output changed after report'
    by_id = {a['id']:a for a in data['annotations']}
    src, out = fitz.open(source), fitz.open(output)
    changes=prepare_source(src,data)
    assert changes==report.get('presentation_changes',[]), 'Unrecorded source presentation change'
    assert len(out) == len(report['pages']) + report.get('guide_pages',0), 'Page count mismatch'
    count = 0
    for pageinfo in report['pages']:
        p = out[pageinfo['output_page']-1]
        original = src[pageinfo['source_page']-1]
        ext = pageinfo['extension_each_side']
        assert abs(p.rect.width-original.rect.width-ext*2) < .01, 'Width mismatch'
        assert abs(p.rect.height-original.rect.height) < .01, 'Height mismatch'
        original_text = normalized(original.get_text())
        assert original_text in normalized(p.get_text()), 'Original text not preserved'
        entries = [a for a in report['annotations'] if a['page'] == pageinfo['source_page']]
        occupied = []
        protected = [fitz.Rect(b[:4])+(ext,0,ext,0) for b in original.get_text('blocks')]
        protected += [fitz.Rect(d['rect'])+(ext,0,ext,0) for d in original.get_drawings()]
        for a in entries:
            box = fitz.Rect(a['note_box'])
            assert a['font_size'] >= 9, 'Font below minimum'
            assert p.rect.contains(box), 'Note outside page'
            assert not any(box.intersects(b) for b in occupied), 'Notes overlap'
            assert not any(box.intersects(b) for b in protected), 'Note covers source'
            occupied.append(box)
            content = normalized(p.get_text(clip=box))
            assert normalized(by_id[a['id']]['text']) in content, f"Missing/clipped note: {a['id']}"
            assert '\ufffd' not in p.get_text(clip=box), 'Replacement glyph found'
            for anchor in a['source_boxes']:
                assert p.rect.contains(fitz.Rect(anchor)), 'Anchor outside page'
            count += 1
    src.close()
    out.close()
    expected = [a for a in data['annotations'] if a['page'] in {p['source_page'] for p in report['pages']}]
    assert {a['id'] for a in report['annotations']} == {a['id'] for a in expected}, 'Missing/extra annotation'
    return {'pages':len(report['pages']), 'annotations':count, 'geometry_and_text':'passed',
            'semantic_review':'not assessed', 'human_review':'not assessed', 'phone_review':'not assessed'}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('annotations')
    parser.add_argument('output')
    args = parser.parse_args()
    try:
        result = verify(args.source,args.annotations,args.output)
    except (AssertionError, ValueError, OSError, KeyError) as exc:
        parser.exit(1, f'FAILED: {exc}\n')
    print(json.dumps(result,ensure_ascii=True))

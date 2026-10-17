import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import sys
import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
spec = importlib.util.spec_from_file_location('annotate', ROOT/'scripts/annotate.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class AnnotationTests(unittest.TestCase):
    def setUp(self):
        self.doc = fitz.open()
        p = self.doc.new_page()
        p.insert_text((108,100), 'A difficult sentence. A difficult sentence.')
        p.insert_text((108,130), 'Across lines and')
        p.insert_text((108,145), 'pages of thought.')

    def tearDown(self):
        self.doc.close()

    def test_missing_and_ambiguous_quotes_are_rejected(self):
        for quote in ('not present','A difficult sentence.'):
            with self.assertRaises(ValueError):
                mod.locate(self.doc[0],quote)
        self.assertEqual(len(mod.locate(self.doc[0],'A difficult sentence.',2)),1)
        with self.assertRaises(ValueError):
            mod.locate(self.doc[0],'A difficult sentence.',0)

    def test_multiline_mapping_preserves_line_rectangles(self):
        boxes = mod.locate(self.doc[0],'Across lines and pages of thought.')
        self.assertEqual(len(boxes),2)
        self.assertLess(boxes[0].y0,boxes[1].y0)

    def test_overflow_does_not_silently_shrink_or_drop(self):
        font = fitz.Font(fontfile=str(mod.FONT))
        entries = [{'display':'需要保留的解释'*100,'anchor':[fitz.Rect(108,100,200,112)]}]
        self.assertIsNone(mod.plan_side(entries,6,96,792,font))

    def test_compatibility_normalization_keeps_math_sign(self):
        self.assertEqual(mod.normalized('reverse\u2011KL'), 'reverse-KL')
        self.assertNotEqual(mod.normalized('a-b'),mod.normalized('a\u2212b'))

    def test_short_english_terms_are_not_split(self):
        font = fitz.Font(fontfile=str(mod.FONT))
        lines = mod.wrap('相对 Direct-OPD 的差异',font,10,82)
        self.assertTrue(any('Direct-OPD' in line for line in lines))

    def test_term_must_display_complete_source_phrase(self):
        a = {'id':'term','page':1,'kind':'term','side':'left',
             'quote':'Across lines and','text':'lines：说明'}
        with self.assertRaisesRegex(ValueError,'complete source phrase'):
            mod.validate_data(self.doc,{'annotations':[a]})
        a['text'] = 'Across lines and：说明'
        self.assertEqual(len(mod.validate_data(self.doc,{'annotations':[a]})),1)

    def test_reading_budget_must_add_up_and_keeps_text_visible(self):
        font = fitz.Font(fontfile=str(mod.FONT))
        guide = {'target_minutes':45,'goal':'理解问题、方法和证据。','audience':'有基本背景的读者。',
                 'steps':[{'title':'先读问题','minutes':45,'read':'原页1摘要。','question':'解决什么问题？'}],
                 'defer':'逐式推导。','checkpoint':'回答问题后再决定补读。'}
        with fitz.open() as out:
            mod.add_reading_guide(out,{'reading_guide':guide,'background':{
                'paragraphs':['先说明任务背景，再读论文。'],
                'links':[{'label':'基础入口','url':'https://example.org/base'}]}},font)
            self.assertIn('45',out[0].get_text())
            self.assertEqual(len(out),1)
            self.assertEqual(out[0].get_links()[0]['uri'],'https://example.org/base')
            self.assertNotIn('参考答案',mod.normalized(out[0].get_text()))
            for block in out[0].get_text('blocks'):
                self.assertTrue(out[0].rect.contains(fitz.Rect(block[:4])))
        guide['steps'][0]['minutes'] = 40
        with fitz.open() as out:
            with self.assertRaisesRegex(ValueError,'add up'):
                mod.add_reading_guide(out,{'reading_guide':guide},font)

    def test_duplicate_ids_are_rejected(self):
        a = {'id':'same','page':1,'kind':'key','side':'right',
             'quote':'Across lines and','text':'解释'}
        with self.assertRaises(ValueError):
            mod.validate_data(self.doc,{'annotations':[a,a]})

    def test_scanned_page_and_rotated_page_fail(self):
        empty = self.doc.new_page()
        with self.assertRaises(ValueError):
            mod.locate(empty,'Anything')
        self.doc[0].set_rotation(90)
        data = {'annotations':[{'id':'one','page':1,'kind':'key','side':'right',
                  'quote':'Across lines and','text':'解释'}]}
        with self.assertRaises(ValueError):
            mod.validate_data(self.doc,data)
        self.doc[0].set_rotation(0)
        self.doc[0].set_cropbox(fitz.Rect(72,72,500,700))
        with self.assertRaises(ValueError):
            mod.validate_data(self.doc,data)

    def test_build_preserves_source_and_chinese_and_checks_hash(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            src, datafile, out = root/'source.pdf', root/'notes.json', root/'out.pdf'
            self.doc.save(src)
            before = src.read_bytes()
            data = {'paper':{'title':'Test','authors':'Test','url':'https://example.org',
                     'sha256':hashlib.sha256(before).hexdigest()}, 'annotations':[
                     {'id':'one','page':1,'kind':'key','side':'right',
                      'quote':'Across lines and','text':'中文说明：条件不能遗漏。'}]}
            datafile.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
            report = mod.build(src,datafile,out,pages=[1])
            self.assertEqual(src.read_bytes(),before)
            self.assertEqual(report['annotation_count'],1)
            self.assertGreaterEqual(report['annotations'][0]['font_size'],9)
            with fitz.open(out) as result:
                self.assertIn('中文说明',mod.normalized(result[0].get_text()))
                self.assertIn('Across lines and',result[0].get_text())
                self.assertEqual(result[0].rect.height,self.doc[0].rect.height)
            data['paper']['sha256']='wrong'
            datafile.write_text(json.dumps(data),encoding='utf-8')
            with self.assertRaises(ValueError):
                mod.build(src,datafile,out)
            with self.assertRaises(ValueError):
                mod.build(src,datafile,src)

    def test_existing_human_annotations_are_not_silently_lost(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            src, datafile = root/'source.pdf', root/'notes.json'
            self.doc[0].add_text_annot((40,40),'Existing human note')
            self.doc.save(src)
            data = {'paper':{'sha256':hashlib.sha256(src.read_bytes()).hexdigest()},'annotations':[]}
            datafile.write_text(json.dumps(data),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'annotations/form'):
                mod.build(src,datafile,root/'out.pdf')

    def test_caption_inventory_rejects_uncovered_visual(self):
        self.doc[0].insert_text((108,200),'Figure 1: A real chart.')
        data={'annotations':[{'id':'one','page':1}],
              'coverage':{'main_source_pages':1,'main_visuals':{'图1':['one']}}}
        self.assertEqual(mod.verify_visual_inventory(self.doc,data)['main_visuals_total'],1)
        data['coverage']['main_visuals']={}
        with self.assertRaisesRegex(ValueError,'same-page'):
            mod.verify_visual_inventory(self.doc,data)

    def test_core_findings_require_attached_limits_and_highlights(self):
        data={'annotations':[{'id':str(i),'kind':'key','limitation':'限定本设置'} for i in range(3)],
              'core_findings':[{'annotation':str(i)} for i in range(3)]}
        mod.check_coverage(data)
        data['annotations'][0]['kind']='note'
        with self.assertRaisesRegex(ValueError,'highlighted'):
            mod.check_coverage(data)

    def test_formula_requires_design_and_example(self):
        data={'annotations':[{'id':'f','page':1,'kind':'formula','side':'left',
              'quote':'Across lines and','text':'公式说明','evidence':'推导'}]}
        with self.assertRaisesRegex(ValueError,'symbols, design'):
            mod.validate_data(self.doc,data)

    def test_explicit_stamp_removal_preserves_horizontal_source(self):
        stamp='arXiv:test [cs.LG] 15 Oct 2026'
        self.doc[0].insert_text((30,650),stamp,rotate=90)
        data={'presentation':{'omit_first_page_vertical_stamp':stamp}}
        changes=mod.prepare_source(self.doc,data)
        self.assertEqual(len(changes),1)
        self.assertNotIn(stamp,self.doc[0].get_text())
        self.assertIn('Across lines and',self.doc[0].get_text())
        self.assertFalse(any(fitz.Rect(x['rect']).intersects(fitz.Rect(changes[0]['box']))
                             for x in self.doc[0].get_drawings()))
        with self.assertRaisesRegex(ValueError,'exactly once'):
            mod.prepare_source(self.doc,data)


if __name__ == '__main__':
    unittest.main()

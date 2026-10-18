import importlib.util
from html.parser import HTMLParser
import json
import base64
import hashlib
import pymupdf as fitz
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('mobile',ROOT/'scripts/mobile.py')
# annotate is used by both generators.
import sys
sys.path.insert(0,str(ROOT/'scripts'))
mobile=importlib.util.module_from_spec(spec);spec.loader.exec_module(mobile)

class Targets(HTMLParser):
    def __init__(self):super().__init__();self.ids=set();self.links=[];self.images=[];self.jumps=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.add(a['id'])
        if tag=='a' and a.get('href','').startswith('#source-'):self.links.append(a['href'][1:])
        if tag=='a' and a.get('href','').startswith('#jump-'):self.jumps.append(a['href'][1:])
        if tag=='img':self.images.append(a['src'])

class MobileTests(unittest.TestCase):
    def test_reader_uses_exact_pdf_pages_and_retains_source_targets(self):
        source=ROOT/'local/attention-is-all-you-need-v1.pdf'
        if not source.exists():self.skipTest('Fetch pinned example for integration test')
        data=ROOT/'examples/attention-is-all-you-need/annotations.json'
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'reader.html'
            annotated=ROOT/'local/attention-preview/attention-is-all-you-need-v1-annotated.pdf'
            count=mobile.build_mobile(source,data,out,annotated)
            text=out.read_text(encoding='utf-8');p=Targets();p.feed(text)
            self.assertEqual(len(p.links),count)
            self.assertTrue(set(p.links)<=p.ids)
            self.assertTrue(set(p.jumps)<=p.ids)
            planned=sum(len(s.get('targets',[])) for s in json.loads(data.read_text(encoding='utf-8'))['reading_guide']['steps'])
            self.assertEqual(len(p.jumps),planned)
            with fitz.open(annotated) as pdf:
                self.assertEqual(len(p.images),len(pdf))
                for i in (0,4):
                    actual=base64.b64decode(p.images[i].split(',',1)[1])
                    expected=pdf[i].get_pixmap(matrix=fitz.Matrix(2.5,2.5),alpha=False).tobytes('png')
                    self.assertEqual(actual,expected)
                goto=[l for l in pdf[0].get_links() if l['kind']==fitz.LINK_GOTO]
                report=json.loads(annotated.with_suffix('.report.json').read_text(encoding='utf-8'))
                self.assertEqual(len(goto),planned)
                for link,target in zip(goto,report['guide_links']):
                    self.assertEqual(link['page']+1,target['output_page'])
                    self.assertLess(abs(link['to'].x-target['point'][0]),.01)
                    self.assertLess(abs(link['to'].y-target['point'][1]),.01)
            self.assertIn(hashlib.sha256(annotated.read_bytes()).hexdigest(),text)
            self.assertNotIn('固定v1第',text)
            self.assertNotIn('参考答案',text)
            self.assertNotIn('【解读·词义】',text)

    def test_changed_data_cannot_silently_use_stale_pdf(self):
        source=ROOT/'local/attention-is-all-you-need-v1.pdf'
        if not source.exists():self.skipTest('Fetch pinned example for integration test')
        with tempfile.TemporaryDirectory() as tmp:
            changed=Path(tmp)/'notes.json'
            changed.write_bytes((ROOT/'examples/attention-is-all-you-need/annotations.json').read_bytes()+b' ')
            with self.assertRaisesRegex(ValueError,'Regenerate'):
                mobile.build_mobile(source,changed,Path(tmp)/'out.html',ROOT/'local/attention-preview/attention-is-all-you-need-v1-annotated.pdf')

if __name__=='__main__':unittest.main()

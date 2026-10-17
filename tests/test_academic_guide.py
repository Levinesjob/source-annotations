import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import pymupdf as fitz
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from academic_guide import analyze_pdf,compile_content,plan_brief
from prepend_guide import prepend


class AcademicGuideTests(unittest.TestCase):
    def fixture(self,root,landscape=False):
        source=root/'research.pdf';doc=fitz.open()
        w,h=(792,612) if landscape else (612,792)
        for i in range(2):
            p=doc.new_page(width=w,height=h)
            p.insert_text((72,100),f'Research page {i+1}',fontname='tiro',fontsize=10)
        doc[0].insert_link({'kind':fitz.LINK_GOTO,'from':fitz.Rect(72,120,220,140),'page':1,'to':fitz.Point(72,100)})
        doc[0].insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(72,150,220,170),'uri':'https://example.org/research'})
        doc[1].add_text_annot((40,180),'Original review')
        widget=fitz.Widget();widget.field_name='original-field';widget.field_type=fitz.PDF_WIDGET_TYPE_TEXT
        widget.rect=fitz.Rect(72,220,210,245);widget.field_value='retained';doc[1].add_widget(widget)
        doc.embfile_add('evidence.txt',b'original attachment')
        doc.set_metadata({'title':'Research title','author':'Original Author','subject':'Original subject'})
        doc.set_page_labels([{'startpage':0,'prefix':'R-','style':'D','firstpagenum':5}])
        doc.set_toc([[1,'Original section',1],[2,'Evidence',2]])
        doc.save(source);doc.close()
        data={'paper':{'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'title':'Research title',
                      'authors':'中文作者 / Original Author','identifier':'test-case','url':'https://example.org'},
              'reading_guide':{'headline':'明确的导读概括','core_view':'本文研究一个具体问题。原文给出有限证据，不保证更高性能。',
                               'prerequisites':['先了解输入、输出和比较对象。'],'target_minutes':10,
                               'steps':[{'title':'证据：查看真实结果','read':'详细推导留在原文。','minutes':10,
                                         'targets':[{'page':2,'point':[72,100],'label':'原文PDF第2页 · 结果'}]}]},'annotations':[]}
        datafile=root/'guide.json';datafile.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
        return source,datafile,data

    def test_insert_preserves_links_bookmarks_notes_forms_labels_and_attachment(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source,datafile,_=self.fixture(root);before=source.read_bytes()
            result=prepend(source,datafile,root/'guided.pdf')
            self.assertEqual(result['validation']['source_pages'],2)
            self.assertEqual(source.read_bytes(),before)
            with fitz.open(root/'guided.pdf') as out:
                self.assertEqual(out[1].get_links()[0]['page'],2)
                self.assertEqual(out.get_toc()[2][2],3)
                self.assertEqual(out.embfile_get('evidence.txt'),b'original attachment')
                self.assertIn('中文作者',out[0].get_text())
                self.assertIn('更高',out[0].get_text())
                self.assertEqual(len(out[0].search_for('更高')),1)
                self.assertEqual(out.get_page_labels()[1]['startpage'],1)
                self.assertEqual(out.get_page_labels()[1]['firstpagenum'],5)

    def test_landscape_paper_dimensions_are_retained(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source,datafile,_=self.fixture(root,True)
            prepend(source,datafile,root/'guided.pdf')
            with fitz.open(root/'guided.pdf') as out:self.assertEqual(out[0].rect,fitz.Rect(0,0,792,612))

    def test_overflow_is_rejected_without_tiny_fonts(self):
        with tempfile.TemporaryDirectory() as tmp:
            source,_,data=self.fixture(Path(tmp))
            data['reading_guide']['core_view']='不能缩小字体来掩盖过长内容。'*600
            with fitz.open(source) as doc:
                with self.assertRaisesRegex(ValueError,'shorten'):
                    plan_brief(compile_content(data),analyze_pdf(doc))

    def test_encryption_rotation_and_overwrite_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source,datafile,data=self.fixture(root)
            with self.assertRaisesRegex(ValueError,'overwrite'):prepend(source,datafile,source)
            with fitz.open(source) as doc:
                doc[0].set_rotation(90);doc.save(root/'rotated.pdf')
            data['paper']['sha256']=hashlib.sha256((root/'rotated.pdf').read_bytes()).hexdigest()
            datafile.write_text(json.dumps(data),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'Rotated'):prepend(root/'rotated.pdf',datafile,root/'out.pdf')
            with fitz.open(source) as doc:doc.save(root/'encrypted.pdf',encryption=fitz.PDF_ENCRYPT_AES_256,owner_pw='test-owner',user_pw='test-user')
            data['paper']['sha256']=hashlib.sha256((root/'encrypted.pdf').read_bytes()).hexdigest()
            datafile.write_text(json.dumps(data),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'Encrypted'):prepend(root/'encrypted.pdf',datafile,root/'out.pdf')


    def test_waypoint_requested_pages_fit_original_width(self):
        source=ROOT/'local/waypoint-opd-v1.pdf'
        if not source.exists():self.skipTest('Fetch pinned example for case integration test')
        from annotate import build
        from verify import verify
        datafile=ROOT/'examples/waypoint-opd/annotations.json'
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'pages.pdf';report=build(source,datafile,out,pages=[3,4])
            self.assertTrue(all(p['extension_each_side']==0 for p in report['pages']))
            self.assertTrue(all(a['font_size']>=9 for a in report['annotations']))
            self.assertEqual(verify(source,datafile,out)['geometry_and_text'],'passed')

    def test_guide_search_mapping_does_not_modify_same_font_in_source(self):
        from academic_guide import FONT
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source,datafile,data=self.fixture(root)
            with fitz.open(source) as doc:
                doc[0].insert_font(fontname='OriginalCJK',fontfile=str(FONT))
                doc[0].insert_text((72,300),'原文更高 / Direct-OPD',fontname='OriginalCJK',fontsize=10)
                doc.save(root/'source-cjk.pdf')
            source=root/'source-cjk.pdf';data['paper']['sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
            datafile.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
            prepend(source,datafile,root/'guided.pdf')
            with fitz.open(source) as before,fitz.open(root/'guided.pdf') as after:
                self.assertEqual(before[0].get_text(),after[1].get_text())
                self.assertEqual(len(after[0].search_for('更高')),1)

if __name__=='__main__':unittest.main()

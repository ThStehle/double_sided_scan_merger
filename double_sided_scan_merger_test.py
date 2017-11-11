# -*- coding: utf-8 -*-
"""
Created on Sun Sep 17 20:25:05 2017

@author: Thomas Stehle
"""
import os
import mock
import unittest
import double_sided_scan_merger as dssm


class double_sided_scan_merger_test(unittest.TestCase):
    scan_dir = 'some_dir'
    result_dir = 'some_other_dir'
    
    def get_default_scan_merger(self):
        merger = dssm.scan_merger(self.scan_dir, self.result_dir)
        return merger
    
    @mock.patch('double_sided_scan_merger.os')
    def test_listdir_scan_dir(self, mock_os):
        merger = self.get_default_scan_merger()
        merger._get_pdf_files_in_scan_dir()
        mock_os.listdir.assert_called_with(self.scan_dir)
        
    @mock.patch('double_sided_scan_merger.os')
    def test_listdir_return_only_pdfs(self, mock_os):
        list_of_files = ['.', '..', 'Scan000032.pdf', 'Scan000050.pdf', 'Scan000051.jpg']
        mock_os.listdir.return_value = list_of_files
        mock_os.path.join.side_effect = os.path.join
        merger = self.get_default_scan_merger()
        returned_list_of_files = merger._get_pdf_files_in_scan_dir()
        self.assertListEqual(returned_list_of_files, ['some_dir' + os.sep + 'Scan000032.pdf', 'some_dir' + os.sep + 'Scan000050.pdf'])

    @mock.patch('double_sided_scan_merger.scan_merger._get_pdf_files_in_scan_dir')
    def test_select_pdfs_to_merge_oneGiven(self, mock_get_pdfs):
        mock_get_pdfs.return_value = ['Scan000032.pdf']
        merger = self.get_default_scan_merger()
        pdfs_to_merge = merger._select_pdfs_to_merge()
        self.assertListEqual(pdfs_to_merge, list())

    @mock.patch('double_sided_scan_merger.scan_merger._get_pdf_files_in_scan_dir')
    def test_select_pdfs_to_merge_threeGiven(self, mock_get_pdfs):
        mock_get_pdfs.return_value = ['Scan0000150.pdf', 'Scan000050.pdf', 'Scan000032.pdf']
        merger = self.get_default_scan_merger()
        pdfs_to_merge = merger._select_pdfs_to_merge()
        self.assertListEqual(pdfs_to_merge, ['Scan000032.pdf', 'Scan000050.pdf'])

    @mock.patch('double_sided_scan_merger.PyPDF2')
    @mock.patch('double_sided_scan_merger.scan_merger._select_pdfs_to_merge')
    def test_merge_pdfs_emptyList(self, mock_select_pdfs, mock_pypdf2):
        mock_select_pdfs.return_value = []
        merger = self.get_default_scan_merger()
        outfile = 'test_file.pdf'
        merger.merge_pdfs(outfile)
        mock_pypdf2.PdfFileReader.assert_not_called()      

    @mock.patch('double_sided_scan_merger.open')
    @mock.patch('double_sided_scan_merger.PyPDF2')
    @mock.patch('double_sided_scan_merger.scan_merger._pdfs_have_same_length')
    @mock.patch('double_sided_scan_merger.scan_merger._select_pdfs_to_merge')
    def test_merge_pdfs_notSameLength(self, mock_select_pdfs, mock_pdfs_have_same_length, mock_pypdf2, mock_open_fct):
        mock_select_pdfs.return_value = ['Scan000032.pdf', 'Scan000050.pdf']
        mock_pdfs_have_same_length.return_value = False
        mock_pypdf2.PdfFileReader.return_value = None
        mock_open_fct.return_value = None
        merger = self.get_default_scan_merger()
        outfile = 'test_file.pdf'
#        merger.merge_pdfs(outfile)
        self.assertRaises(Exception, merger.merge_pdfs, outfile)


    def test_combine_pdfs_combinationOK(self):
        pdf_in1 = mock.Mock()
        pdf_in2 = mock.Mock()
        pdf_out = mock.Mock()
        
        pdf_in1.getNumPages.return_value = 3
        pdf_in1.getPage.side_effect = lambda x: x
        pdf_in2.getPage.side_effect = lambda x: x

        merger = self.get_default_scan_merger()
        merger._combine_pdfs(pdf_in1, pdf_in2, pdf_out)
        
        calls = [mock.call(0), mock.call(2), 
                 mock.call(1), mock.call(1), 
                 mock.call(2), mock.call(0), ]
        pdf_out.addPage.assert_has_calls(calls)


def run_all_tests():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(double_sided_scan_merger_test))
    return test_suite
    
if __name__ == '__main__':
    unittest.main(defaultTest='run_all_tests')
    